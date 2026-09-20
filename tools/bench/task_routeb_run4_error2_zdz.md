# Failed prediction — D1 route-B v1 run 4. Attack both claims below.

Context: a Python COM client (`tools/gscript.py`) drives LabVIEW 2026 VI Scripting over ActiveX to restructure a
copy of a large tracking VI. Run 4 (`tools/bench/build_d1_routeb_v1_run4.log`, `BGRUN END rc=1 after 1713s`,
80 PASS / 1 FAIL) PREDICTED an "S3w ledger" stage and reached neither it nor the later S4/S5/S6 stages. The
prediction failed, so this review is mandatory. Your job is to REFUTE, not to agree.

---

## CLAIM 1 — "run 4's crash is a resource-budget failure of the READING LabVIEW instance, not a defect in what the recipe built"

Stated flatly so you can attack it:

> The crash `RuntimeError: count(LoopTunnel) on SCRATCH_routeb_221324.vi: error 2: Invoke Node in TRef
> Traverse.vi->VI Scripting - Traverse.lvlib:Traverse for GObjects.vi->OpReport_v3.vi` was raised inside
> `settle_index_modes()` with **51,284 handles** open in the LabVIEW process, against this install's measured
> fresh baseline of ~31,500 handles. LabVIEW error 2 is *memory full*. THEREFORE re-running the same recipe
> against a freshly restarted LabVIEW, with the whole-VI `count(LoopTunnel)` census narrowed in scope or dropped
> entirely, would get past this point — nothing the recipe BUILT is implicated.

Rivals you must weigh explicitly, and say which the evidence favours:

- (a) the recipe's own constructions (newly created shift registers, moved nodes, reparented terminals) left the
  VI in a state that makes `Traverse for GObjects` unbounded or cyclic, so the traverse never terminates and
  exhausts memory regardless of the starting handle count;
- (b) `OpReport_v3.vi` or the Traverse path leaks VI Server references per call, so cost is per-call and a
  restart only delays the same crash;
- (c) `count()` over a whole VI is simply the wrong instrument at this object count, and the fix is not a restart
  but a different query.

Also answer: is LabVIEW error 2 in a VI-Scripting Invoke Node reliably "memory full", or is it overloaded to
other conditions on this path? Cite a source.

---

## CLAIM 2 — "`Z/dZ` → `#2222` t0 has NO by-index route on this fleet"

Stated flatly:

> `docs/cycle15-plan.md` Pre-decided 3 says the `Z/dZ` wire is to be REORDERED. That cannot be executed as
> written. MEASURED in run 4 (`build_d1_routeb_v1_run4.log:163-164`): the `ControlTerminal` for `Z/dZ` is uid
> `#403`; on `Diagram[56]` it is `Nodes[None]` with terminals `[]`; the sink `#2222` is `Diagram[24].Nodes[20]`
> t0 = `('', False, 0)` — an UNNAMED sink terminal. `OpConnectNested_v1` addresses wires as
> `Diagram[].Nodes[].Terminals[]` (`tools/recipes/build_opconnectnested_v1.py:418-420`), so a `ControlTerminal`
> that does not appear in that diagram's `Nodes[]` array has no by-index address at all.

The question we actually need answered — be concrete and cheap:

**What is the CHEAPEST mechanism that wires a control terminal to an UNNAMED sink terminal on a DIFFERENT
diagram, using an op we already have?** Two facts constrain the answer:

1. `OpConnectFromWire_v0` IS built (`docs/toolkit-capabilities.md:70`) and branches from a WIRE's source
   terminal rather than from a node index.
2. But `'Z/dZ'` carries wire `w730` on a PRISTINE copy and carries **NO wire at all on the BUILT copy, because
   the node moves performed earlier in the recipe cut it** (`tools/bench/diag_sr_transport.log:20`, `:25-26`;
   `archive/peer/2026-09-18-priorart-d1-routeb-v1.md:871-873`). So a wire-source-based op has nothing to branch
   from at the moment we would call it.

Constraint on your answer: the user has a STANDING ORDER forbidding the construction of NEW process devices /
tooling. Prefer an answer that uses an EXISTING op, a different ORDERING of the existing steps (e.g. doing the
connection BEFORE the moves that cut `w730`), or a documented LabVIEW VI-Scripting address form we are not
using. If your answer requires new tooling, say so explicitly and say why nothing existing suffices.

---

## For BOTH claims, give me, per claim:

1. the STRONGEST reason the claim is WRONG;
2. an ALTERNATIVE explanation of the same evidence;
3. what observation would FALSIFY the claim;
4. the CHEAPEST DISCRIMINATING TEST that separates the claim from its best rival — a concrete command or query,
   not a comparison of options.

---

## ALREADY RULED OUT — do not spend the answer on these (all measured in run 4)

- The build is NOT broken in the way our old gate suggested: the BASELINE `ExecState` read **0 COLD (logged
  UNREAD)** while the LIVE working copy read **`ExecState` 1 PRELOADED**, and the original resident read-only
  also read 1. The cold read measures subVI linkage, not brokenness.
- Rule 1 (never modify an original) held: original md5 `2a78e17c449cacdaf5da389818526859` unchanged before,
  after, and across the preloaded read; the working copy was deleted.
- The build's OTHER two planned rows SUCCEEDED: shift registers `#26032` (on `#1359` t1/t2) and `#26082` (on
  `#29874` t3/t5) were created and moved together with their nodes. ONLY row 3 (`Z/dZ`) failed — it is the single
  FAIL line in the whole 80-pass run (`:164`).
