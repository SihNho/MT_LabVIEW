# c66-m3-movelocals

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.5921  in 16 / out 49041 / cache-create 178884 / cache-read 810467  (627s, 20 turn(s))
- **date:** 2026-09-21 17:16:38
- **outcome:** ANSWERED (628s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# REFUTE two claims about a LabVIEW VI-Scripting move stage, then answer one factual API question

You are attacking two claims. Find the strongest reason each is WRONG, name an alternative
explanation, say what would falsify it, and name the cheapest discriminating test we could run over
our COM/VI-Server property path. Then answer the separate FACTUAL question at the end, using the web.

## Background in one paragraph

We are restructuring a copy of a LabVIEW tracking VI by SCHEDULING only (rule: the computation must
not change). The working bed is `claudeDev\D1_s3b_row2_20260921_160311.vi`. On the top-level
sub-diagram `Diagram #639` (owner `WhileLoop #637`) sit 75 nodes. A previously built empty
`WhileLoop #23032` has an empty body `Diagram #23058`. Stage "S3b-M3" moves a set of objects from
`#639` into `#23058` with one `move_in` call per object, then re-wires the rows that the move
severed. Everything is verified STRUCTURALLY only (`ExecState`, object censuses, `Wire.Is Broken?`)
— we never run the VI.

## CLAIM 1 — the move set is SEVEN objects, not five

> S3b-M3's move set is not the five loop-1.5 nodes but **seven objects**: those five plus the two
> Local variables `#23499` and `#23523`, all moved into `#23032`'s body `Diagram #23058`.
> Reason: `#10407` (a CaseStructure) moves to `#23058` while both Locals currently sit on
> `Diagram #639`, so leaving them behind makes rows 1 and 2 cross-diagram, and our `connect_nested_v1`
> verb addresses one nested diagram only. A Local variable binds to its front-panel control **by
> label**, not by wire, so relocating one changes no data path — which is precisely what the
> indicator+Local substitution was built to buy. This is therefore a pure SCHEDULING change,
> permitted by our behaviour-preserving-refactor rule, and it keeps every row intra-diagram with no
> new tunnel and no border object.

Attack in particular: is "a Local variable can be moved between diagrams with no semantic effect"
actually true in LabVIEW? Name any way a Local's diagram membership changes behaviour, legality,
race semantics, dataflow scheduling or the compiler's verdict — e.g. inside a Case/Event/Disabled
structure, a Timed Loop, a subVI boundary, reentrancy, or the race conditions LabVIEW's own docs
warn about for Locals. Also: is there any way `Diagram.MoveObject`-style relocation of a Local can
silently rebind, orphan or duplicate it?

## CLAIM 2 — the abort clause that fired was mis-scoped, and the re-scoping is correct

> Abort clause A2 was written to catch "a watched wire branching onto an existing structure's
> tunnel" and was scoped as "on ANY tunnel terminal". It fired on wires **23540** and **23502**,
> whose sinks are `#10407`'s **own** t2 / t0 case tunnels — the very connection the two rows were
> built to make, and the same sink the original undivided wire **10990** used. The new net **23556**
> was measured tunnel-free (`IndexArray #10757` -> owner `Diagram 639`). Each of the three wires
> walked by uid showed exactly **one source and one sink**; a branch would show a third endpoint.
> The clause is therefore re-scoped to: abort only if a watched wire has **more than one sink**, or
> a sink other than the terminal its row was built to feed.

The machine's own lines, verbatim, from `tools/bench/diag_c66_s3b_m3.log`:

```
  FAIL  P1b-A2 NO watched wire sits on a terminal of a STRUCTURE node on #639  [{'node_uid': 10407, 'node_class': 'CaseStructure', 'terminal': 0, 'is_source': False, 'wire': 23502, 'node_is_structure': True}, {'node_uid': 10407, 'node_class': 'CaseStructure', 'terminal': 2, 'name': 'index', 'is_source': False, 'wire': 23540, 'node_is_structure': True}]
  PASS  P1c-A2 wire 23556 has NO terminal whose OWNER is in the Tunnel family  owner classes ['IndexArray', 'Diagram', '']
  FAIL  P1c-A2 wire 23540 has NO terminal whose OWNER is in the Tunnel family  owner classes ['Local', 'SelectorTunnel', '']
  FAIL  P1c-A2 wire 23502 has NO terminal whose OWNER is in the Tunnel family  owner classes ['Local', 'Tunnel', '']
```

Attack in particular: (a) is "exactly one source and one sink when walked by uid" a SOUND test for
"this wire is not branched" over LabVIEW's VI Server object model — i.e. can a branched net present
as one Wire object whose `Terminals[]` enumeration returns only two entries, or can a branch live on
a *different* Wire object of the same net that a uid walk never visits? (b) Does the re-scoped clause
still catch the failure it was written for? (c) Note the third owner class in each list is the empty
string `''` — say what an empty owner class most plausibly is on this path and whether it can hide a
third endpoint.

## Already ruled out (do not re-propose these)

1. "The tunnel class is a blind spot in our census" — `report_all('Tunnel')` now resolves and returns
   **471** rows (LoopTunnel 135 · ConditionalTunnel 146 · SelectorTunnel 146 · shift registers 36/36),
   so that class is counted.
2. "Our reader cannot see structure tunnel terminals" — `node_terms` run on all 15 structure nodes of
   `#639` returned their tunnel terminals.
3. "`#639` might not be the diagram we think" — `owner_of(639)` = `('WhileLoop', 637)`, so `#639` is a
   sub-diagram, consistent with every other census.

## SEPARATE FACTUAL QUESTION — please use web search for this one

We measured `TYPE READ UNREACHABLE`: no property our fleet wraps carries a wire's or a terminal's
**data type**. Tried and named, each with the field its wrapper returns:

- `Terminal.Name` 634A004
- `Terminal.Is Source?` 634A003
- `Terminal.Connected Wire` 634A000
- `Terminal.Diagram` 634A002
- `Tunnel.Outside Terminal` 6356001
- `Tunnel.Inside Terminals[]` 6356000
- `Wire.Is Broken?` 6371004
- `NumericConstant.Representation` 5DCFC00

Question: over LabVIEW's VI Server / ActiveX property-and-method surface, **is there a reachable
route to the data type of a wire or of a node terminal** — a property short name, a method, or a
documented indirection — that we have not tried? We need it because `Is Broken?` catches a
type-INCOMPATIBLE connection but **not a LEGAL COERCION** (DBL->SGL, DBL->I32), which leaves
`ExecState` 1 and every count correct while silently changing the numbers. Name the exact identifier
and cite its source (NI documentation page, property node reference, forum post with the short name
visible). If there is genuinely no such route, say so and name the closest indirect proxy
(e.g. a coercion-dot indicator, a saved-file inspection route, a `Get Type Descriptor`-style path).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session (correctly — the brief says read-only), so the review is the output.

---

# Failed-prediction review — S3b-M3 move set, abort clause A2, and the type read

**CLAIM 1 — REFUTED.** **CLAIM 2 — the mis-scoping half is correct; the evidence half is unsound and the replacement is weaker than what it replaces.** **FACTUAL QUESTION — the premise is false: the type read is reachable, and the identifier you need is `Terminal.Coercion Dot?` 634A006.**

---

## CLAIM 1 — the seven-object move set

### 1. Strongest reason it is wrong

The load-bearing sentence is *"a Local binds to its control by label, not by wire, so relocating one changes no data path."* Both halves are true; neither supports the conclusion. **A Local has no data path — that is the hazard.** A wired node's value is fixed by dataflow: the producer must finish before the consumer starts. A Local read returns whatever was last written *at the instant that node executes*, and its execution instant is decided by which diagram owns it. NI's own position is that locals break dataflow execution and the outcome then depends on the order in which events occur.

So moving `#23499` and `#23523` from `Diagram #639` (body of `WhileLoop #637`) into `Diagram #23058` (body of a *different* `WhileLoop #23032`) changes at minimum:

- **sampling rate** — once per `#637` iteration becomes once per `#23032` iteration;
- **what they race against** — the reader now runs in a loop concurrent with the writer instead of sequenced in the same diagram, which is the restructure's entire purpose;
- **the first-iteration value** — `#23032` can complete an iteration before the writer has ever written, so the first sample is the control's current contents, not this frame's value.

None of that is visible to `ExecState`, a census, or `Wire.Is Broken?`. This is not "permitted by the behaviour-preserving-refactor rule"; it is the case CLAUDE.md §1a reserves: *"A change of decomposition can be a change of computation … Acceptance is numeric … When a step cannot be shown computation-preserving, stop and ask the user."*

**Direct answer to "name any way a Local's diagram membership changes behaviour":** conditional execution (inside a Case / Event / Diagram-Disable / Conditional-Disable frame a Local executes only when that frame runs — an always-read becomes a sometimes-read); iteration count; race semantics and ordering; the start-up race. **Legality and binding are *not* affected** — within one VI a Local is legal on any diagram, binding follows the control reference, reentrancy gives each clone its own control instance regardless of diagram, and the compiler verdict is unchanged. I found no route by which `MoveObject`-style relocation silently rebinds, orphans or duplicates a Local. **That absence is not reassurance — it is the problem.** Every mechanism that could have made this visible is inert, which is exactly why structural-only acceptance cannot clear it.

### 2. Alternative explanation of the same evidence

**The set grew from five to seven to fit a verb's addressing limit, not because the design calls for it.** The claim says so itself — *"our `connect_nested_v1` verb addresses one nested diagram only."* Rows 1 and 2 are cross-diagram *by construction*: an indicator+Local pair exists precisely so a value can cross a loop boundary, so a Local on `#639` feeding a case structure in `#23058` is the pattern working as intended. The alternatives are to extend the verb, or to **drop a fresh Local inside `#23058` and delete the one on `#639`** — Locals are freely duplicable, so nothing forces a *move*. Under this reading "seven" is a tooling artefact; CLAUDE.md has the slug (`tool-not-built`).

**Second alternative the run never excluded: `#10407` t0 or t2 may be the case SELECTOR.** Log:70 shows Local `#23499` ('Automatic Error Handling') feeding **t0**; log:71 shows `#23523` ('index') feeding **t2**. Log:78 gives t0's owner class as plain `Tunnel` #10429; log:76 gives t2's as **`SelectorTunnel`** #10978. LabVIEW's taxonomy ties `SelectorTunnel` to the selector — `ConditionalTunnel` carries a *Replace With Case Selector* method that "converts a tunnel on a Case structure to the case selector". If either row now feeds the selector through a Local, a stale sample changes **which case executes**, not a number. The run does not settle this and did not ask.

### 3. What would falsify Claim 1

Rule 1a's own criterion: identical inputs through the S3a path and the moved-Local path producing a different X/Y/Z sequence — or a different first-frame value. Structurally: any difference in `Terminal.Data Type` (634A008) or `Coercion Dot?` (634A006) at the same terminal between `D1_s3a_focus_ind.vi` and the bed falsifies it before any run.

### 4. Cheapest discriminating test

**Two property reads on a diagnostic that already holds both references.** `[P3]` already resolves `#10757` t1 and `#10407` t0/t2 on the bed (log:95-99) *and* on the untouched S3a artefact (log:114-128). Read `Coercion Dot?` **634A006** and `Data Type` **634A008** on those terminals in both files and compare — zero new references, one ID registration, and A1 stops being vacuous. Separately and just as cheaply: read `Terminal.Name` on `#10978` and `#10429` and find out which one LabVIEW calls the selector. One read decides whether Claim 1 is a scheduling change or a control-flow change.

---

## CLAIM 2 — the A2 re-scoping

### Conceded first, because it is true

**The clause as written is logically unsatisfiable for the rows it guards.** `diag_c66_s3b_m3.py:67` scopes A2 as "any tunnel terminal"; `:657`/`:670` implement it as *any* structure-node terminal plus a `"Tunnel" in owner_class` substring test. Rows 1 and 2 were built to terminate on `#10407`'s case tunnels. A gate that cannot pass when the work is correct is not a gate. Log:123 corroborates the row-2 target — on S3a, `#10407` t2 carried wire **10990**, the wire being replaced. That part stands.

### 1. Strongest reason the rest is wrong

**"Exactly one source and one sink" is not a sound branch test, and this run contains the proof.** `docs/NAMES.md:1020` defines the terminator: *"Walk `term index` 0,1,2… until error 1055 = past the end."* The script asks for twelve (`WIRE_TERMS(WORK, ww, n=12)`, `:663`) and gets three rows, the third being the terminator printed as a data row.

**1055 is overloaded at least three ways inside this project:**

1. past the end of `Terminals[]` (`NAMES.md:1020`);
2. **a real terminal that is BARE** — `diag_c66_s3b_m3.py:348`: *"the one legitimate bare-terminal error pattern: wire 0 with conn_err/wire_err 1055 and name_err/src_err 0"*;
3. a genuine invalid-reference failure on a real object — **this very run, log:88-90**, `owner_of(26117)` → `error 1055: Property Node in OpOwnerChain_v1.vi`.

1055 is just "Object reference is invalid"; it carries no end-of-array meaning. And log:91 says outright that `owner_of` *"answered with the PREVIOUS query's object once, silently"* and these reads are *"evidence to read, not a verdict to act on."* **The run applies that caution to P2, then rests A2's exoneration on the same reader in P1c.**

Worse: **the walker's branch detection has never been exercised.** `NAMES.md:1021-1022` records its only validation — *"wire 10850 → source `DigitalNumericConstant` 10739 / sink `Comparison` 10950"* — a two-endpoint wire. It has never been shown to report a third endpoint on a wire that has one.

### 2. Alternative explanation of the same evidence

**The re-scoping does not fix a mis-scope; it removes the check.** ">1 sink" is close to unfalsifiable right after a fresh single connect. The hazard A2 was written for — an accidental landing on an *existing* structure's tunnel — would in most realisations produce exactly **one** sink that is the wrong one, so the whole weight shifts to "a sink other than the terminal its row was built to feed". That anchor is a **terminal index**, and case-structure tunnel indices renumber when tunnels are added or deleted — which is what five-to-seven `move_in` calls are about to do. The anchor has already drifted once: log:123 names `#10407` t2 `'Index of closest\ncal image slice, bead 2'` on S3a; log:56 names the same index `'index'` on the bed.

And it drops the **source** side entirely — at the stage that creates source-side branches. `NAMES.md:1031-1034`, measured here: *"Deleting a node leaves its wire behind as a loose stub … a later connection from that source then counts as a BRANCH, and a search for 'unwired sinks' will NOT find the orphaned consumer."*

**Separately, already-ruled-out item 1 is not established.** Log:44-49 reports `Tunnel` 471, then 135 + 146 + 146 + 36 + 36 = **499**. Either those are a breakdown of 471 — in which case the classes **overlap by ≥ 28** and the `"Tunnel" in owner_class` substring test (`:668`) rests on a taxonomy that does not partition — or they are not a breakdown, in which case the tunnel population is ~970 and "that class is counted" is wrong the other way. The run does not say which, and A2's premise is "we can see tunnel attachments".

### 3. What would falsify Claim 2

Run `wire_source_owner` on a wire **known** to have one source and two sinks. Three resolved rows ⇒ the walker sees branches and the readings hold. Stops at the sentinel after two ⇒ every "no branch" conclusion this cycle is void, including the one being used to weaken A2.

**On the empty owner class specifically:** `''` with `owner_uid: 0` and `recip: 0` is most plausibly an Index-Array-past-the-end default refnum, not a hidden endpoint — a live branch endpoint would have a valid reference and its reciprocal `Connected Wire` would echo the wire. I do **not** think a third endpoint is hiding there. But **the measurement does not distinguish "no third terminal" from "a third terminal whose reference failed to resolve"**, and P2 proves that failure mode is live on this path. Stop inferring array length from an error code.

### 4. Cheapest discriminating test

**A positive control on a scratch VI**: one wire, one source, two sinks, same `wire_source_owner(n=12)`, count resolved rows. One scratch VI, one op call, the bed never opened.

Alongside it, the free independent detector the fleet has never used: **`Wire.Joints[]`**, which returns all joints of the wire "including intersections, bends, and end points". A branch **is** an intersection; a two-endpoint wire has only bends and end points. That is a branch test that does not depend on guessing an array's length from 1055.

For the clause itself: replace it with an **expected-sinks whitelist written before the run** — per watched wire, the `{node uid, terminal NAME, owner class}` it may land on, failing on anything else, source side included. Strictly stronger than both the original and the proposal, costs nothing, and would have passed this run. CLAUDE.md already requires it: *"Recipes must state their prediction contracts … before execution so 'failed prediction' is machine-checkable."* Deciding the contract from the evidence that fired the alarm, in the session that wants to proceed, is the wrong order even when the conclusion is right.

---

## FACTUAL QUESTION — the type read is reachable

**`TYPE READ UNREACHABLE` (log:132-133) is a conclusion about eight wrappers promoted to a conclusion about LabVIEW's property surface.** The `Terminal` class carries at least eleven properties; the eight tried are not the relevant ones.

| identifier | ID (hex) | short name | returns |
|---|---|---|---|
| **`Terminal.Coercion Dot?`** | **634A006** | **`Coerced?`** | Boolean — True if a coercion dot is present on the terminal |
| **`Terminal.Data Type`** | **634A008** | `Data Type` | the terminal's data type as a Variant; read-only, remote access allowed, does not load the diagram |
| `Terminal.Type Descriptor` | 634A001 | `TypeDesc` | I16 array — **write-only and deprecated; not the read route** |
| `Terminal.Create Constant` (method) | — | — | creates a constant of the terminal's type — the classic indirection, now unnecessary |

**`Coercion Dot?` 634A006 is the exact answer to your stated need.** `Is Broken?` catches a type-*incompatible* connection but not a legal coercion; a coercion dot is the marker LabVIEW itself draws for precisely that event — NI: "LabVIEW converted the value passed into the node to a different representation … places a coercion dot on the border of the terminal where the conversion takes place." NI's own answer to "Finding coercion dots?" is the recipe, using machinery you already have: **Traverse for GObjects with class name `Terminal`, then read `Coercion Dot?`**.

`Data Type` 634A008 is the ground truth for identity; `Coerced?` is the better *gate* — a Boolean is trivially comparable where two Variants carrying types are awkward over this COM path. Gate on `Coerced?`, evidence with `Data Type`.

**Wire-level: there is genuinely no route.** The `Wire` class has `Terminals[]`, `Is Broken?`, `Joints[]`, `Wire Width`, `Value`, `Get Error List` — and no data-type or type-descriptor property. That matches NI's own "Scripting: Find wire class type" thread, whose accepted answer reaches the type **through the terminal**, not the wire. Terminal-level yes, wire-level no — read the type at the wire's source and sink terminals.

**One caveat, because this project has been bitten by it.** `VI.Get Errors` (452) is absent from the exported `VirtualInstrument` ActiveX interface, so "the VI Server property exists" does not prove "reachable over our path". The one-call test: build a `VI Server:Terminal` property node with 634A006 and read the carrier's short name — `NAMES.md:369` shows that pattern already working for `Is Source?` 634A003 → `IsSource` and `Connected Wire` 634A000 → `Wire`. These are **cited IDs, not guesses**, so `toolkit-capabilities.md:256-260`'s objection does not apply.

### Why this matters more than either claim

A1 fires on *a MEASURED type MISMATCH*, and `TYPE READ UNREACHABLE` is explicitly declared "NOT a mismatch" (`diag_c66_s3b_m3.py:66`). So **A1 passed (log:134) because the measurement was declared impossible** — the run's only rule-1a safeguard was vacuous, and rows 1 and 2 were built and saved with nothing checking that a DBL did not become an I32. That is the most expensive thing in this log, and as of these two property IDs it costs one registration to fix.

**Sources:** [NI — Coercion Dot? property](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/coerciondot.html) · [NI — Coercion Dots](https://www.ni.com/docs/en-US/bundle/labview/page/coercion-dots.html) · [NI Community — Finding coercion dots?](https://forums.ni.com/t5/LabVIEW/Finding-coercion-dots/td-p/3734995) · [NI Community — Scripting: Find wire class type](https://forums.ni.com/t5/LabVIEW/Scripting-Find-wire-class-type/td-p/3796825) · [NI — Error 1055](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE) · [NI — Local/Global Variables Can Cause Race Conditions](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P83YSAS) · [NI — Wire Joints property](https://zone.ni.com/reference/en-XX/help/371361R-01/lvscript/wire_joints091093) · [LabVIEW Wiki — Terminal class](https://labviewwiki.org/wiki/Terminal_class), [Data Type](https://labviewwiki.org/wiki/Terminal_class/Data_Type_property), [Coercion Dot?](https://labviewwiki.org/wiki/Terminal_class/Coercion_Dot%3F_property), [Type Descriptor](https://labviewwiki.org/wiki/Terminal_class/Type_Descriptor_property) · [LabVIEW Wiki — Wire class](https://labviewwiki.org/wiki/Wire_class), [Race condition](https://labviewwiki.org/wiki/Race_condition), [ConditionalTunnel/Replace With Case Selector](https://labviewwiki.org/wiki/ConditionalTunnel_class/Replace_With_Case_Selector_method)

## Sources

(extract from answer)

## What was done with it

Dispositioned IN FULL by cycle 66 material #3 (2026-09-21 17:2x), under the brief's rule: a finding is either
(i) IMPLEMENTED MECHANICALLY when it does not change Part B's route, or (ii) QUOTED VERBATIM AND NOT ACTED ON
and marked a ROUTE CHANGE FOR JUDGEMENT. A material session does not change a route, does not make a rule-1a
equivalence call, and does not decide what to accept from a review. Outcome: **ANSWERED**, 628 s, $3.5921,
`tools/bench/peer_c66_m3_movelocals.log` `BGRUN END rc=0 after 628s`, archived here.

### (ii) ROUTE CHANGES FOR JUDGEMENT — quoted verbatim, NOT acted on

**R1. CLAIM 1 REFUTED — the seven-object move set is called a COMPUTATION change, not a scheduling change.
This is a rule-1a equivalence call and is therefore not a material session's to make.** Verbatim:

> "The load-bearing sentence is *'a Local binds to its control by label, not by wire, so relocating one changes
> no data path.'* Both halves are true; neither supports the conclusion. **A Local has no data path — that is
> the hazard.** … So moving `#23499` and `#23523` from `Diagram #639` (body of `WhileLoop #637`) into
> `Diagram #23058` (body of a *different* `WhileLoop #23032`) changes at minimum: **sampling rate** — once per
> `#637` iteration becomes once per `#23032` iteration; **what they race against** — the reader now runs in a
> loop concurrent with the writer instead of sequenced in the same diagram, which is the restructure's entire
> purpose; **the first-iteration value** — `#23032` can complete an iteration before the writer has ever
> written, so the first sample is the control's current contents, not this frame's value. None of that is
> visible to `ExecState`, a census, or `Wire.Is Broken?`. This is not 'permitted by the behaviour-preserving-
> refactor rule'; it is the case CLAUDE.md §1a reserves."

> "**Legality and binding are *not* affected** — within one VI a Local is legal on any diagram, binding follows
> the control reference, reentrancy gives each clone its own control instance regardless of diagram, and the
> compiler verdict is unchanged. I found no route by which `MoveObject`-style relocation silently rebinds,
> orphans or duplicates a Local. **That absence is not reassurance — it is the problem.** Every mechanism that
> could have made this visible is inert, which is exactly why structural-only acceptance cannot clear it."

> "**The set grew from five to seven to fit a verb's addressing limit, not because the design calls for it.** …
> The alternatives are to extend the verb, or to **drop a fresh Local inside `#23058` and delete the one on
> `#639`** — Locals are freely duplicable, so nothing forces a *move*. Under this reading 'seven' is a tooling
> artefact; CLAUDE.md has the slug (`tool-not-built`)."

**R2. `#10407` t0 / t2 may be the CASE SELECTOR, which would make the two Local rows a control-flow change, not
a numeric one.** Verbatim:

> "Log:78 gives t0's owner class as plain `Tunnel` #10429; log:76 gives t2's as **`SelectorTunnel`** #10978.
> LabVIEW's taxonomy ties `SelectorTunnel` to the selector … If either row now feeds the selector through a
> Local, a stale sample changes **which case executes**, not a number. The run does not settle this and did not
> ask."

NOT acted on beyond a READ: the brief's move set and row table are fixed, and re-cutting them is judgement's.
What WAS added mechanically is (i.3) below — `#10407`'s full terminal table is now dumped so the question is
answerable from the run's own record.

**R3. THE TYPE READ IS REACHABLE — `Terminal.Coercion Dot?` 634A006 and `Terminal.Data Type` 634A008.** The
brief RETIRED A1 and said in terms "Do not re-attempt it in Part B", so registering a new property ID is
outside this dispatch. Recorded here in full for judgement. Verbatim:

> "**`TYPE READ UNREACHABLE` (log:132-133) is a conclusion about eight wrappers promoted to a conclusion about
> LabVIEW's property surface.** … `Terminal.Coercion Dot?` **634A006**, short name `Coerced?`, Boolean — True
> if a coercion dot is present on the terminal. `Terminal.Data Type` **634A008**, short name `Data Type`, the
> terminal's data type as a Variant; read-only, remote access allowed, does not load the diagram.
> `Terminal.Type Descriptor` 634A001 — **write-only and deprecated; not the read route.**"

> "**`Coercion Dot?` 634A006 is the exact answer to your stated need.** … NI's own answer to 'Finding coercion
> dots?' is the recipe, using machinery you already have: **Traverse for GObjects with class name `Terminal`,
> then read `Coercion Dot?`**. … Gate on `Coerced?`, evidence with `Data Type`."

> "**Wire-level: there is genuinely no route.** The `Wire` class has `Terminals[]`, `Is Broken?`, `Joints[]`,
> `Wire Width`, `Value`, `Get Error List` — and no data-type or type-descriptor property. … Terminal-level yes,
> wire-level no — read the type at the wire's source and sink terminals."

> "One caveat … `VI.Get Errors` (452) is absent from the exported `VirtualInstrument` ActiveX interface, so
> 'the VI Server property exists' does not prove 'reachable over our path'. The one-call test: build a
> `VI Server:Terminal` property node with 634A006 and read the carrier's short name … These are **cited IDs,
> not guesses**, so `toolkit-capabilities.md:256-260`'s objection does not apply."

> "**A1 passed (log:134) because the measurement was declared impossible** — the run's only rule-1a safeguard
> was vacuous, and rows 1 and 2 were built and saved with nothing checking that a DBL did not become an I32.
> That is the most expensive thing in this log, and as of these two property IDs it costs one registration to
> fix."

**R4. `wire_source_owner`'s branch detection has never been exercised, and error 1055 is overloaded three ways.**
Building the positive control it asks for is a new scratch VI plus an op call that the brief does not name, so
it is NOT acted on. Verbatim:

> "**'Exactly one source and one sink' is not a sound branch test, and this run contains the proof.** …
> The script asks for twelve (`WIRE_TERMS(WORK, ww, n=12)`, `:663`) and gets three rows, the third being the
> terminator printed as a data row. **1055 is overloaded at least three ways inside this project:** past the
> end of `Terminals[]`; **a real terminal that is BARE**; a genuine invalid-reference failure on a real object
> — **this very run, log:88-90**, `owner_of(26117)` → `error 1055`. … **the walker's branch detection has never
> been exercised.** … It has never been shown to report a third endpoint on a wire that has one."

> "**A positive control on a scratch VI**: one wire, one source, two sinks, same `wire_source_owner(n=12)`,
> count resolved rows. One scratch VI, one op call, the bed never opened. Alongside it, the free independent
> detector the fleet has never used: **`Wire.Joints[]`** … A branch **is** an intersection; a two-endpoint wire
> has only bends and end points."

On the empty third row specifically, the peer's own verdict, recorded because it narrows the risk:

> "`''` with `owner_uid: 0` and `recip: 0` is most plausibly an Index-Array-past-the-end default refnum, not a
> hidden endpoint … I do **not** think a third endpoint is hiding there. But **the measurement does not
> distinguish 'no third terminal' from 'a third terminal whose reference failed to resolve'**."

### (i) IMPLEMENTED MECHANICALLY — none of these changes Part B's route

1. **CLAIM 2's concession is implemented, and the source side the peer said was dropped is now gated.** The
   peer conceded the mis-scope in terms — *"A gate that cannot pass when the work is correct is not a gate"* —
   and then objected that the replacement *"drops the **source** side entirely — at the stage that creates
   source-side branches."* `tools/bench/diag_c66b_s3b_m3.py` therefore carries **both** whitelists, written as
   constants BEFORE the run (`EXPECTED_SINK`, `EXPECTED_SOURCE`), and A2 fires on a wrong or extra endpoint on
   EITHER side: exactly one source AND exactly one sink AND each being the endpoint its row was built for.
2. **The `Tunnel` arithmetic the peer disputed is now printed as a FACT, not assumed.** *"Log:44-49 reports
   `Tunnel` 471, then 135 + 146 + 146 + 36 + 36 = **499** … the classes **overlap by ≥ 28** … or the tunnel
   population is ~970 … The run does not say which."* Step P1a now computes and prints the sum, the parent
   count and the difference, so the record states which it is instead of leaving it to inference.
3. **`#10407`'s FULL terminal table, and both Locals' tables, are dumped before any move** (existing verbs
   only), so R2 — whether t0/t2 is the case selector — is answerable from this run's record without a new op.
4. **Terminal-index drift is addressed the way the peer framed it.** *"That anchor is a **terminal index**, and
   case-structure tunnel indices renumber when tunnels are added or deleted."* Every row is addressed by
   `resolve_term`, which prefers the terminal NAME when it is non-empty and unique among terminals of the right
   direction and falls back to the RE-MEASURED index, recording in the JSON which route it used and what the
   chosen terminal actually reads.

### What was NOT changed, and why

Part B's route — the seven-object move set, the row table, the pass criterion — is unchanged. The brief states
it, and it rests on a rule-1a equivalence call. Accepting R1 would re-cut the stage; accepting R3 would add a
property registration the brief excluded. Both are judgement's, and both are carried out of this cycle in the
material session's `OPEN:` block rather than settled here.
