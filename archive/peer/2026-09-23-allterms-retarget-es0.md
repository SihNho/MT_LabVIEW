# allterms-retarget-es0

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.4121  in 24 / out 54799 / cache-create 209055 / cache-read 1741541  (697s, 20 turn(s))
- **date:** 2026-09-23 05:58:30
- **outcome:** ANSWERED (702s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# Failed prediction: a re-targeted `To More Specific Class` feeding a `Terminal` property node reads ExecState 0

Attack the diagnosis below. LabVIEW 2026 VI Scripting, driven headlessly over COM. Read-only research;
no LabVIEW here.

## What we are trying to build and why the construction matters

`OpAllTerms_v0.vi`: ONE call on a VI path returning every block-diagram terminal (uid, name, is_source,
connected-wire uid, owner uid, owner class). `Traverse for GObjects` with class `Terminal` returns 5,811
refs on our test VI in 5.28 s in one round trip, against ~508 s for the per-node reader we have.

The blocker is a type one: `Traverse` yields **GObject** refs, and `Name` (634A004) / `Is Source?`
(634A003) / `Connected Wire` (634A000) are **Terminal**-class properties, so each element needs a
`To More Specific Class` (TMSC). Measured, one variable at a time, on ONE copy:

- `Traverse.References` -> a `VI Server:Terminal` property node inside a For-loop body: ExecState **0**.
- the SAME wire -> a `VI Server:GObject` property node in the SAME body: ExecState **1**.
  (`tools/bench/diag_allterms_donor.log:33`)

A TMSC has no scripted creator in this fleet, and our project rule forbids the `copy_by_index` +
`move_in`-into-a-loop-body construction (4 attempts, 0 successes). Measured this session:
`copy_by_index` has no destination-diagram parameter; our loop creator makes an EMPTY loop and cannot
enclose existing nodes; and a census of **all 26** op VIs that own both a Function node and a loop found
**0** carrying a TMSC inside a loop body (`tools/bench/diag_allterms_donor2.log`, 26 pass / 1 fail, the
one fail being that free prediction).

So the remaining construction is: put the cast in a one-row **subVI** whose own ROOT diagram holds it,
and call that subVI from inside the loop. Its one unmeasured link is whether an existing TMSC can be
**re-targeted** to `Terminal` and feed a Terminal-class property node.

## The prediction and what was measured

PREDICTED: ExecState **1**.  MEASURED: ExecState **0**.  (`tools/bench/diag_allterms_retarget2.log:114`)

The run took a dated scratch copy of `OpLoopCast_v0.vi` (a working op, ExecState 1, whose root diagram
carries TMSC uid 683 with `target class` fed by a refnum-control seed) and:

1. deleted its Property nodes (they read `ForLoop`-class properties off the cast, so they had to go);
   Property 2 -> 0, Function unchanged 3 -> 3.
2. created `build_property("VI Server:Terminal", [634A004, 634A003, 634A000, 632A813, 6327806])` on the
   ROOT diagram - op error `''`, Property 0 -> 1.
3. `create_control` on that node's own `reference` -> a control LabVIEW named `'reference 2'`, arriving
   WIRED (birth wire w362), which is the documented behaviour.
4. deleted w362, deleted the old seed wire and the old cast-output wire, then wired
   `'reference 2'` -> TMSC `target class` and TMSC `specific class reference` -> the Terminal node's
   `reference`. Both landed: Wire count 8 -> 9 -> 10, both op errors `''`.
5. ExecState: **1 at open -> 0 at the end**.

The final root-diagram census read back off the machine (node index, uid, terminal -> connected wire):

```
0  #43   Open VI Reference  vi path w106, vi reference w467, error out 0
1  #124  Traverse           VI Refnum w467, Traverse Target w415, Class Name w373, References w600
2  #308  Index Array        array w600, element w605, index w1066
3  #683  TMSC               reference w605, target class w333, specific class reference w348
4  #316  Open VI Reference  vi path w550, vi reference 0, error out 0
5  #331  (no terminals at all)
6  #186  Terminal property   reference w348, Name 0, IsSource 0, Wire 0, UID 0, Owner 0
```

## The diagnosis to attack

**H1 (ours): the 0 is leftover wreckage from stripping the donor, not the cast.** Node 5 (`#331`) reports
no terminals, which in our reader is how a STRUCTURE appears; `OpLoopCast_v0` owns a For loop whose body
held the Property nodes that step 1 deleted. Our own recipe notes say of a freshly created For loop
"ExecState 0 is EXPECTED - an empty loop has no N" (`tools/recipes/build_opreportall_v1.py:134`). Node 4
(`#316`) is a second `Open VI Reference` whose output is now unwired. On H1 the cast chain itself is
sound - `#683.specific class reference` w348 does reach `#186.reference` w348 - and the construction
stands.

**H2: a re-targeted TMSC genuinely cannot serve a Terminal-class property node.** The `target class`
input takes any wire of the target type, so a refnum control made on a Terminal node's own `reference`
should specify `Terminal` by construction - but we have never verified that the CONTROL's class is what
we assume, only that a control appeared and that the wire landed with an empty error. On H2 the last
construction our rules permit is closed.

We would like: the strongest reason H1 is wrong; any third explanation for ExecState 0 on this diagram
that neither H1 nor H2 covers; what observation would falsify H1; and the cheapest discriminating test
we can run headlessly over COM (we can read ExecState, class censuses, per-node terminal/wire maps,
`Wire.Is Broken?` on one wire after a write, and a GUI Error List is being built in parallel). Note that
"the VI is broken" is all our COM path exposes - `VI.Get Errors` (452) is absent from the exported
ActiveX interface here, so per-object error text is not readable by script.

Also worth attacking: is the subVI-in-loop construction itself sound in LabVIEW terms - a For loop
auto-indexing an array of GObject refs into a subVI whose connector-pane input is a GObject refnum
control, that subVI casting to Terminal on its own root diagram and returning scalars that the loop
auto-indexes back out?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this session (correct for a read-only peer role), so the review is below.

---

# Failed-prediction review — re-targeted TMSC → Terminal property node reads ExecState 0

**H1 does not hold, and neither does the experiment.** The run carries one ExecState bit across ~10 mutations, and the single piece of evidence H1 offers for "the cast chain is sound" is the one class of evidence this project has already measured to be compatible with a broken wire.

## 1. The strongest reason H1 is WRONG

H1's load-bearing inference — *"the cast chain itself is sound — `#683.specific class reference` w348 does reach `#186.reference` w348"* — is inadmissible **by your own measurement**:

- `docs/toolkit-capabilities.md:70`, `OpConnectFromWire_v0` T2: "op error `''`, sink **0 → 1231**" … "🔴 **T2c2 FAILED: that wire reads `Is Broken? TRUE`**". A wire that reached both terminals, +1 on the count, op error empty — and broken.
- `tools/recipes/build_opconnectfromwire_v0.py:41-50` replaced the count/identity gate for exactly this reason. `docs/toolkit-capabilities.md:68`: **"Do not cite RBW-survival as evidence a wire is good."**
- U4's gate is a wire **count** (`tools/bench/diag_allterms_retarget2.py:147-149`: `w1 == w0+1 and w2 == w1+1 and not err`).

A created-but-broken wire is precisely what a bad GObject→Terminal cast looks like: LabVIEW draws the wire, marks it a class conflict, VI reads 0 ([NI: Wire Class Conflict and Broken Wires](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019XS0SAM&l=en-US)).

**The decisive blade — you have run this before and the brief omits it.** The identical five-step construction ran 2026-09-21 for class `Local`, with the per-step ExecState recorded: `1 → 0 after build_property → 1 after the seed control → 0 after the birth-wire delete → 0 thereafter` (`docs/cycle27-plan.md:2220-2222`, citing `diag_s3b_l0_localname_v2.log:83-126`). **The VI returns to 1 in the middle of the sequence.** Leftover wreckage cannot hold a VI broken and then let it read 1. That run used a *different donor* with a *different* set of deletions and reached the same terminal 0 — so a donor-specific wreckage hypothesis cannot explain a failure that already occurred on another donor. It even records the same three-way ambiguity you are re-deriving from scratch (`:2226-2227`).

**Both of H1's named culprits are LabVIEW-legal.** Node #316's unwired *outputs* never break a VI. Node #331 is a **pre-existing** For loop inside a VI that compiled at ExecState 1 (`diag_allterms_retarget2.log:16`), so its count terminal was already satisfied; emptying a loop does not unwire N. The cited precedent (`tools/recipes/build_opreportall_v1.py:134`) is about a *freshly created* loop that never had N — importing it here is a category error.

## 2. Alternative explanation (H3) — neither H1 nor H2

Deleting the birth wire takes ExecState to 0 by an ordinary, already-measured mechanism (an unwired Property-Node `reference` is a broken VI — that is the `Local` run's "0 after the birth-wire delete"), and **nothing was measured again until the end**. Two live sub-variants:

- **H3a — the seed's class was never verified.** The gate checks only that one control appeared and got a label (`diag_allterms_retarget2.py:119-121`). Creating a control from a property node's own terminal is a documented source of class conflict ([NI forum](https://forums.ni.com/t5/LabVIEW/wire-conflict-when-connecting-a-control-to-a-property-node-value/td-p/3561234)).
- **H3b — node #187.** An eighth root node appears in *every* walk from U3 onward (`diag_allterms_retarget2.log:55, 67, 86, 108`) and is **absent from the 7-row census the brief presented to me**. `build_property` asserts exactly one new Property (`tools/gscript.py:2324-2326`) and Function was unchanged 3→3, so #187 is neither. It was created in this run and never identified.

**H2 as stated is not a type-system fact.** Terminal's parent *is* GObject, with four subclasses (ControlTerminal, InnerTerminal, OuterTerminal, ParameterTerminal) — [Terminal class](https://labviewwiki.org/wiki/Terminal_class), [GObject class](https://labviewwiki.org/wiki/GObject_class). GObject→Terminal is a legal downcast. If it fails, it fails for an implementation reason, and the seed is the likeliest.

## 3. What would falsify H1

Any ExecState reading of **1** taken after the donor was stripped — H1 says the stripping left it broken. Concretely: read ExecState immediately after `create_control` in U3, **before** the birth-wire delete. H1 predicts 0; the `Local` run read **1** at that exact point. One COM property read.

## 4. Cheapest discriminating test

Add five `s.es()` calls to `diag_allterms_retarget2.py` — after `build_property`, after `create_control`, after the birth-wire delete, after each of the two wires. The file already calls `s.es()` once (`:154`). No new op, no new VI, no restart; the run is 77 s.

| reading | H1 (wreckage) | H3 (seed / cast) |
|---|---|---|
| after `build_property` | 0 | 0 (unwired `reference`) |
| after `create_control` | **0** | **1** |
| after birth-wire delete | 0 | 0 |
| after cast → `reference` | 0 | 0 if bad, **1** if good |

**One-variable follow-up if that is ambiguous:** re-run byte-identical with `build_property("VI Server:GObject", [632A813])` instead of the Terminal node. Same 0 ⇒ the fault is in the sequence; 1 ⇒ it is class-specific. That is exactly the control `diag_allterms_donor.log:26-33` used correctly and this run dropped.

## 5. Attacking the subVI-in-loop construction itself

Type-wise it is sound — a For loop auto-indexing a GObject array into a subVI with a GObject/Generic refnum on the connector pane is ordinary LabVIEW, and `conpane`/`conpane_assign`/`drop_subvi` exist (`diag_allterms_donor.log:24`). But:

- **It moves the cast, it does not remove it.** The subVI still needs a GObject→Terminal TMSC seeded by the same unverified control. If H3a is the fault, the subVI inherits it exactly.
- **Five properties on one node violates your own measured rule.** `docs/toolkit-capabilities.md:74`: *"one property per node with its own error chain (a failing row silently defaults the rows below it on the same node)"*. `TERM_PROPS` (`diag_allterms_retarget2.py:51-52`) is ordered Name, IsSource, **ConnectedWire**, UID, Owner — on any terminal with no wire, `Connected Wire` errors and **UID and Owner silently return 0**. Those are two of the six deliverable columns (`docs/connectivity-map-plan.md:48`), and unconnected terminals are the majority. That is a rule-1a-class silent corruption sitting in the code now.
- **`owner_uid` has its own measured silent failure.** `Generic.Owner` returns a Generic ref, so the uid needs a second cast, and `docs/toolkit-capabilities.md:61` records the limit: when the owner is a `FlatSequenceFrame`, ClassName returns but **the UID does not** (`owner_uid 0`, `error 1055`, empty echo). The main VI is full of flat sequences.

**And the route that needs no GObject→Terminal cast at all — already built, already permitted.** `OpWireSource_v5.vi` is one of the three donors Pre-decided 139 explicitly allows (`docs/connectivity-map-plan.md:69`), and it already runs: cast(**Wire**) → `Wire.Terms[]` 6371003 → Index Array → **`Is Source?` 634A003 / `Connected Wire` 634A000 / `Generic.Owner` 6327806 → ClassName + cast(GObject) → UID** (`docs/toolkit-capabilities.md:60`), ExecState 1, functional 12/12. `Wire.Terms[]` hands back **Terminal-class references with no cast** — which is why those Terminal properties read straight off it, and why `OpConnectFromWire_v0` reads `Name` off the same kind of reference (`:70`). The only cast on that path is **GObject→Wire**, already proven from a `create_control` Wire seed (built, saved, ExecState 1, cold-verified). With `Traverse('Wire')` already measured at 1,920 wires in 1.67 s (commit `1f9fdd4`), that is `OpAllWires_v0` — which your plan names in the same table cell as `OpAllTerms_v0`, and whose graph step is specified as "edges from wires" (`:51`) with pass criteria "wire join = 1,920" and "the 11 broken wires show a missing side" (`:48`). It omits only wire-less terminals, which contribute no edge. Decide whether any pass criterion actually needs them before buying another cycle of cast work.

## Where the evidence does not settle the question

- The measurement **does not distinguish** "the seed control is not Terminal-class" from "the seed is fine and something else on the diagram is broken". One bit, ten mutations.
- The census uids are uninformative in both directions: LabVIEW recycles uids here — the new Property node took uid **186**, below pre-existing 308/316/331/683 — so w333 matching the wire deleted at `diag_allterms_retarget2.log:93` proves neither reuse nor survival.
- `Wire.Is Broken?` would answer this directly, but the built reader is a post-write readback embedded in the connect ops and cannot be used read-only (`docs/toolkit-capabilities.md:68`, corrected 2026-09-23; `archive/peer/2026-09-23-priorart-allwires.md` A3 concedes a write-free per-wire census is genuinely unbuilt). So the ExecState bracket, not `Is Broken?`, is the cheap instrument here.

## Process finding

This stage has now ended **three times with no saved artefact and no per-step evidence** — `Local` 2026-09-21, `Terminal` 2026-09-23 ×2 — and the 2026-09-21 run already recorded the narrowing this one re-derives. Under the user's 2026-09-19 re-split rule and CLAUDE.md's "when a diagnosis is guessed twice, build the reader", the next act is a decomposition carrying per-step ExecState readings, not a third re-target.

**I do not believe H1 holds.** What would change my mind: an ExecState of 0 read immediately after `create_control` in U3, before any wire was deleted — that would show the stripped donor was already broken and put the wreckage hypothesis back in play.

Sources: [Terminal class](https://labviewwiki.org/wiki/Terminal_class) · [GObject class](https://labviewwiki.org/wiki/GObject_class) · [VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) · [NI: Wire Class Conflict and Broken Wires](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019XS0SAM&l=en-US) · [NI: Class conflict error reference](https://www.physik.uzh.ch/local/teaching/SPI301/LV-2015-Help/lverror.chm/edClassConflict.html) · [NI: To More Specific Class target-class constraint](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/to-more-specific-class-must-cast-to-original-type-in-a-reference.html) · [NI forum: control-from-property-node class conflict](https://forums.ni.com/t5/LabVIEW/wire-conflict-when-connecting-a-control-to-a-property-node-value/td-p/3561234)

## Sources

(extract from answer)

## What was done with it

Written by the MATERIAL session that dispatched it, 2026-09-23 06:0x. **The material failure budget (2) was
already spent when this answer arrived**, so nothing here was re-run: every finding is recorded and dispositioned,
and the re-run itself is the judgement session's to order.

**§1 — H1 IS WITHDRAWN. ACCEPTED IN FULL, and the decisive citation was ours.** `docs/cycle27-plan.md:2220-2222`
records the identical five-step construction run for class `Local` on 2026-09-21 with the per-step ExecState
`1 → 0 after build_property → 1 after the seed control → 0 after the birth-wire delete → 0 thereafter`. A VI that
reads **1** in the middle of the sequence cannot be held broken by leftover wreckage, and that run used a
DIFFERENT donor with DIFFERENT deletions and still ended 0 — so no donor-specific hypothesis survives. The two
culprits H1 named are legal (unwired *outputs* never break a VI; `#331` is a PRE-EXISTING For loop inside a VI
that read ExecState 1 at open — `diag_allterms_retarget2.log:16` — so emptying it does not unwire N, and citing
`build_opreportall_v1.py:134`, which is about a FRESHLY CREATED loop, was a category error). The H1 text in
`docs/toolkit-capabilities.md` and in STATUS's `purpose_allterms_routes` is marked "not attributed", which stays
true; it must not be re-stated as an explanation.

**§1 also kills U4's gate.** U4 asserts a wire COUNT (`diag_allterms_retarget2.py:147-149`), and this project has
already measured a wire that reached both terminals, counted +1, returned op error `''` **and read
`Is Broken? TRUE`** (`docs/toolkit-capabilities.md:70`, `OpConnectFromWire_v0` T2c2). "Both wires landed" is
therefore NOT evidence the cast is sound, and the U4 PASS must not be cited as such anywhere.

**§2/§3/§4 — ACCEPTED as the next measurement, NOT RUN (budget spent).** The live hypothesis is H3: H3a the seed
control's CLASS was never verified (the gate checks only that a control appeared and got a label,
`diag_allterms_retarget2.py:119-121`); H3b an eighth root node **#187** appears in every walk from U3 onward
(`diag_allterms_retarget2.log:55,67,86,108`), is neither the new Property nor a Function (3→3), and was never
identified. The prescribed test is five extra `s.es()` calls in the existing file — after `build_property`, after
`create_control`, after the birth-wire delete, after each wire — 77 s, no new op, no restart, with the published
H1-vs-H3 truth table; plus the byte-identical `VI Server:GObject` control arm if that is ambiguous.

**§5 — TWO DESIGN DEFECTS ACCEPTED, and they are the most valuable thing in this review.** Both sit in code
written this session and would have corrupted the deliverable silently:
1. `TERM_PROPS` puts FIVE properties on ONE node, against our own measured rule that a failing row silently
   defaults the rows below it on the same node (`docs/toolkit-capabilities.md:74`). Ordered
   Name, IsSource, **ConnectedWire**, UID, Owner, an UNWIRED terminal errors at `Connected Wire` and returns
   **UID and Owner as 0** — two of the six deliverable columns (`docs/connectivity-map-plan.md:48`), on what is
   the MAJORITY of terminals. One property per node with its own error chain.
2. `owner_uid` needs a second cast (`Generic.Owner` returns Generic) and is MEASURED to fail when the owner is a
   `FlatSequenceFrame` — `owner_uid 0`, error 1055, empty echo (`docs/toolkit-capabilities.md:61`). The main VI is
   full of flat sequences, so this is not an edge case.
The subVI-in-loop route is conceded type-sound but "moves the cast, it does not remove it" — if H3a is the fault
the subVI inherits it. Accepted.

**§5's last paragraph — the wire-centric alternative — is RECORDED, NOT ACCEPTED, and it has one unanswered
hole.** `Wire.Terms[]` **6371003** does hand back Terminal-class references with no cast, and `OpWireSource_v5`
already reads `Is Source?` / `Connected Wire` / `Generic.Owner` off them at ExecState 1 (12/12). But the review
does not say how a WHOLE-VI wire census gets its per-element **GObject→Wire** cast INSIDE the loop: that is the
same wall this session measured shut on three of four routes (`tools/bench/diag_allterms_donor.log` A1/A2,
`diag_allterms_donor2.log` R3). Whether the plan's step-4 criteria are satisfiable without wire-less terminals is
a scope decision, and scope is judgement's.

**Process finding — ACCEPTED, and it is the honest cost of this dispatch.** The stage has now ended three times
with no saved artefact (`Local` 2026-09-21, `Terminal` 2026-09-23 ×2), and the 2026-09-21 run had already
recorded the narrowing this one re-derived. Under the user's 2026-09-19 re-split rule the next act is a
DECOMPOSITION carrying per-step ExecState readings, not a third re-target — which is also exactly §4's test.
