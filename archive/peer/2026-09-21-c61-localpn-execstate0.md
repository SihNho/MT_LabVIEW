# c61-localpn-execstate0

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.9786  in 10 / out 25926 / cache-create 209993 / cache-read 362055  (339s, 13 turn(s))
- **date:** 2026-09-21 09:07:30
- **outcome:** ANSWERED (340s)
- **why asked:** MANDATORY failed-prediction review (CLAUDE.md §5). Cycle 61 material #2 predicted `ExecState == 1` at the save point of `claudeDev\OpCreateLocalRead_v0.vi` and read **0**: `tools/bench/diag_c61_localdir_write.log` FAIL `S3_b *** ExecState == 1 at the save point ***`, 38 pass / 1 fail, `BGRUN END rc=1 after 110s`. Nothing was saved; the unsaved copy was removed.
- **verdict:** unverified

## Question

# Failed prediction: a `Local`-class Property Node makes the VI illegal the instant it is created

LabVIEW 2026 (26.3.1f1), Windows 10, VI Scripting over ActiveX/COM. Everything below is a reading taken
off the machine in ONE run today (`tools/bench/diag_c61_localdir_write.log`, 38 pass / 1 fail).

## The prediction that failed

PREDICTED: after adding a `VI Server:Local` Property Node to a copy of a working op VI, wiring its
`reference` input from a `Control -> Create:Local Variable` Invoke Node's output terminal, and creating a
front-panel control on the node's `Write?` input, the VI would read `ExecState == 1` (legal) and could be saved.

OBSERVED: `ExecState` went **1 -> 0 the moment `build_property('VI Server:Local', [('6355401', True)])`
returned**, and stayed 0 through every later step. The VI was therefore never saved.

## The readings, verbatim

On a scratch duplicate of a large application VI (`Property` census 106):
- `build_property('VI Server:Local', [('6355401', True)])` -> node #23493 created, creator error column `''`,
  its i=4 row `{'i': 4, 'name': 'Write?', 'is_source': False, 'wire': 0}`. **ExecState 1 -> 0.**
  `delete_object` the node again -> **ExecState 0 -> 1**, census 106 -> 107 -> 106.
- The same with `('6355400', True)` (`CtrlName`, a SINK): **1 -> 0**, delete -> **1**.
- The same with `('6355401', False)` (`Write?`, now a SOURCE): **1 -> 0**, delete -> **1**.
- The same with `('6355400', False)` (`CtrlName`, a SOURCE): **1 -> 0**, delete -> **1**.
- CONTROL: `build_property('VI Server:VI', [('242', False)])` -> i=4 `'Def Err Handling'`, SOURCE.
  **ExecState 1 -> 1.** Delete -> 1. So the creator itself does not break VIs; the `Local` CLASS does here.

On a throwaway copy of the op VI `OpCreateLocal_v0.vi` (9,688 B, `Property` census 4, `Wire` census 9):
- `ExecState` 1 at open.
- `build_property('VI Server:Local', [('6355401', True)])` -> node #339 at Nodes[9], error column `''`,
  i=4 `{'name': 'Write?', 'is_source': False, 'wire': 0}`. **ExecState 1 -> 0.**
- `connect_terminals(sink = #339 'reference' i=0, src = Invoke #306 i=5 'Create Local' SOURCE)`:
  `wire_delta 1`, error column `''`, `Wire` 9 -> 10, new wire uid **390**, and the `reference` row afterwards
  reads `{'i': 0, 'name': 'reference', 'is_source': False, 'wire': 390}`. **ExecState 0 before and 0 after.**
- An ORDERED second pass through our `Wire.Is Broken?` (6371004) carrier on that same connection:
  **`Is Broken?` = False** on wire 390, `wire_delta 0`, op error `''`. So THAT wire is not broken.
- `create_control` on #339's `Write?` SINK -> one new ControlTerminal #496, label read back off the machine as
  `'Write?'`, plus wire #536. **ExecState 0 before and 0 after.**
- Nothing was saved; the copy was deleted; the donor is byte-unchanged.

The Invoke Node is `Control -> Create:Local Variable`, method id `6331C02`, six terminals:
`(0 reference sink, 1 reference out source, 2 error in sink, 3 error out source, 4 'Create Local' sink,
5 'Create Local' SOURCE)`. Terminal 4 was and is unwired; terminal 5 is the one we wired.

## Already ruled out (do not spend your answer here)

1. NOT the wire: `ExecState` was already 0 before any wire existed, and the wire we made reads `Is Broken? False`.
2. NOT the created control: `ExecState` was 0 before `create_control` and 0 after.
3. NOT the write/read mode and NOT the property id: all four `Local` combinations go 1 -> 0, while
   `VI Server:VI` id 242 on the same bed stays at 1; deleting the `Local` node restores 1 every time.

## What we want from you

Attack the diagnosis "a `Local`-class Property Node cannot legally exist on a diagram built this way, so this
route is blocked". In particular:

- The strongest reason that diagnosis is WRONG.
- An alternative explanation for `ExecState` 1 -> 0 that our four readings do not exclude (for example: what a
  Property Node whose class the creator wrote as a string, with an UNWIRED `reference`, actually is to
  LabVIEW's type checker; whether a `Local` refnum wire from `Create:Local Variable` is the type this node's
  `reference` expects at all, given `Is Broken?` reads False; whether `ExecState 0` here means "broken VI" or
  something weaker, and what would distinguish those).
- What observation would FALSIFY your alternative.
- The single cheapest discriminating test we could run next, using only: creating/deleting nodes, wiring
  terminals by index, reading terminal tables (`name`, `is_source`, `wire`), `Wire.Is Broken?`, `ExecState`,
  front-panel control creation, and the LabVIEW error list if you know a scripting route to it over ActiveX.

Public documentation on `Local Variable` refnum class, `Local.Write?` / `Local.Control Name` property ids
(6355401 / 6355400), and on what makes a Property Node itself break a VI, is welcome — cite it.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this role, as the brief requires — so the review is the answer itself.

---

# The claim is REFUTED — by this project's own machine record, taken 45 minutes before the run under review

## 1. Strongest reason the claim is wrong: a `Local`-class Property Node has already sat on a diagram here at `ExecState` 1

Same day, same `build_property` verb, cycle 60 material #2:

| step | reading |
|---|---|
| `build_property('VI Server:Local',[('6355400',False)])` | `ExecState` **0** — `tools/bench/diag_s3b_l0_localname_v2.log:83` |
| `create_control` on that node's `reference` SINK | `ExecState` **1** — `:88-89` (the seed was born wired, wire 1086, `:91`) |
| that birth wire deleted again | `ExecState` **0** — `:95` |

`ExecState` followed **whether `reference` was fed**, not the node's class. "A `Local`-class Property Node makes the VI illegal the instant it is created" is false as stated, and the run under review never had to find that out — it is in a log the same fleet wrote this morning.

## 2. The alternative explanation your four readings do not exclude

**Every `Local` probe was created with `reference` unwired — by construction, not by accident.** `tools/gscript.py:2198`: *"Same rules as build_invoke: **reference unwired**, class by string, IDs not names."* A Property Node with an unsatisfied `reference` is broken for **every** class except the ones carrying an implicit reference — and the control you chose, `VI Server:VI` id 242 (`diag_c61_localdir_write.log:85-94`), is exactly that exception: *"If you do not wire a refnum to the reference input of the Property Node, LabVIEW gets or sets the property for the current VI"*, and implicit nodes exist only for the current application, the current VI, and controls in the same VI. **The control varied class and reference-requirement together, then attributed the result to class.**

Ruled-out item 3 ("deleting the node restores 1, four times", `:38/:52/:66/:80`) is predicted equally well by the unwired-reference explanation — deleting an unsatisfied node removes the unsatisfied input. It discriminates nothing.

**And the reading the FAIL gate fired on is inadmissible under your own rule.** `docs/NAMES.md:912-918`, measured cycle 23: reading `Wire.Is Broken?` **perturbs the target** — *"an ExecState read taken AFTER a wire read is not evidence of brokenness … treat any ExecState taken after it as SUSPECT, and re-establish legality from a VI the reader has not touched."* The ordered `Is Broken?` pass ran at `diag_c61_localdir_write.log:128-131`; the before/after-`create_control` readings and the save-point gate are `:137`, `:140`, `:142-143` — **all downstream of it**. Cycle 60's 0 → 1 recovery was taken before any such read. The two runs are not comparable at the one step that matters.

## 3. What the evidence genuinely does not settle

Two things changed together between the cycle-60 recovery and today's failure: **(a)** `6355400` READ vs `6355401` WRITE, and **(b)** the reference source — a `Terminal.Create Control` typed seed vs the Invoke's `Create Local` output wire. `Is Broken? False` on wire 390 does not exonerate (b): **a node can be broken while its wires are not.** `Write?` is documented read/write only on the LabVIEW Wiki, a source `docs/cycle27-plan.md:2029` already records as self-declaring incompleteness — so "the write mode of 6355401 is refused" remains live and is *not* the same finding as "the class is illegal".

## 4. What would falsify my alternative

`build_property('VI Server:Local', [('6355401', False)])` followed by `create_control` on the node's `reference` SINK, with no `Is Broken?` call in the run, leaving `ExecState` at **0**. Then the unwired-reference explanation is dead and the claim survives — and the next question becomes why cycle 60's node reached 1 and this one cannot.

## 5. Cheapest discriminating test — one throwaway copy, two probes, nothing saved, **no `Wire.Is Broken?` anywhere in the run**

| probe | steps | expected if I am right |
|---|---|---|
| **P1** | `build_property('VI Server:Local',[('6355401',False)])` → `create_control` on `reference` | 0 → **1** |
| **P2** | same with `('6355401',True)` → `create_control` on `reference` → `create_control` on `Write?` | 0 → ? → ? |

- **P1 → 1**: the class is legal, the claim is dead, cycle 60 reproduced on this bed.
- **P1 → 1, P2 → 0**: the fault is the **write mode of `6355401`** — a precise, actionable result that decides the D1 direction question instead of closing a route.
- **both → 1**: the fault was the Invoke's `Create Local` wire and/or the perturbing read; the route is open.
- **P1 → 0**: I am falsified.

Two node creations, two control creations, four `ExecState` reads, both probes deleted again. No save, no cast, no new verb, no donor substitution.

**Sources:** [NI forums — VI self reference / implicit property node](https://forums.ni.com/t5/LabVIEW/vi-self-reference/td-p/404239) · [NI forums — implicit vs explicit property node](https://forums.ni.com/t5/LabVIEW/implicit-vs-explicit-property-node/td-p/654014) · [LabVIEW Wiki — Local class](https://labviewwiki.org/wiki/Local_class) (`Write?` 6355401 and `Control Name` 6355400 both listed Read/Write; the page says nothing about the `reference` input) · [LabVIEW Wiki — Control References](https://labviewwiki.org/wiki/Control_References)

## Sources

(extract from answer)

## What was done with it

**Disposed 2026-09-21 by the cycle-61 judgement session. ACCEPTED on its central point; one sub-claim
recorded as holding only in part. No probe of the review's was run before this disposition — the
disposition is the judgement act, and the separator below is judgement's own design.**

1. **ACCEPTED — "the 1→0 at `build_property` is expected, not the fault."** The review cites
   `tools/bench/diag_s3b_l0_localname_v2.log:83-95`, where a `VI Server:Local` property node on this same
   fleet read `ExecState` **1** once its `reference` input was fed. A property node whose class has no
   implicit reference is broken while that input is bare, so the transition the dispatch reported as the
   fault is ordinary. The framing it attacked — *"the 1→0 follows the PROPERTY-NODE CREATION"* — is
   withdrawn.
2. **ACCEPTED — the `VI Server:VI` 242 regression is a confounded control.** 242 is an implicit-reference
   property, so that comparison varied class and reference-requirement together and cannot separate them.
   It stays in the record as a regression check on the `build_property` patch, which is all it was for.
3. **HOLDS IN PART — the perturbation sub-claim.** The review says the save gate sits downstream of the
   `Is Broken?` read, which `docs/NAMES.md:912-918` measures as perturbing `ExecState`. That is true of the
   readings at `tools/bench/diag_c61_localdir_write.log:137-143` and false of the first 1→0 at `:111`, as
   the dispatch itself noted. Both halves are kept.
4. **WHAT IT CHANGED — the next run's ORDER, not its construction.** The chain built in this dispatch is
   kept exactly as it is (`build_property` write-mode → `reference` from Invoke `#306` i=5 → `create_control`
   on the `Write?` SINK); what changes is that no `Is Broken?` is read before the save, and the ordered pass
   moves to after a COLD reopen — the order `tools/recipes/stage_d1_s3a_focus_ind.py` proved at 64/0 and that
   `docs/cycle27-plan.md` Pre-decided 42(b) already required. With the perturbing read out of the timeline,
   a residual 0 becomes attributable and the review's P1/P2 probes become the next cycle's first act.
5. **NOT ACTED ON — P1 and P2 were not run.** Running a review's conditional next step is accepting its
   whole framing, and the separator above is cheaper and tests the same question.

**Standing fact this exchange did NOT produce but which the same run measured, recorded here so it is not
lost:** `Create:Local Variable` **6331C02**'s `i=5 'Create Local'` SOURCE wires into a `VI Server:Local`
property node's `reference` SINK with **`Is Broken?` False** (`tools/bench/diag_c61_localdir_write.log:100-132`),
so this route needs **no `To More Specific Class`** — the blocker that ended both of cycle 60's builds.
