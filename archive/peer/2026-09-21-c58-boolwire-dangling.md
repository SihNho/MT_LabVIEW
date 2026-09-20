# c58-boolwire-dangling

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.3192  in 26 / out 43567 / cache-create 218488 / cache-read 1904980  (586s, 22 turn(s))
- **date:** 2026-09-21 00:59:02
- **outcome:** ANSWERED (588s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim. It is the explanation this project formed for a FAILED PREDICTION, and the next build
depends on it. Find the strongest reason it is WRONG.

# The failed prediction

`tools/bench/diag_s58_boolcarrier_run2.log` (cycle 58 material #1, run 2, `BGRUN END rc=1 after 248s`,
54 pass / 9 fail) predicted, in its own docstring, gate `B3b`: *"ExecState after the delete == 1"*.
It measured **0**, on all three candidates (gate lines `C1 B3b` / `C2 B3b` / `C3 B3b`).

# THE CLAIM UNDER ATTACK (written into docs/cycle27-plan.md as Pre-decided 48(b)+48(d))

> A Boolean type needs a **SOURCE** terminal, and `create_indicator` on a SOURCE terminal makes a REAL wire.
> The whole-VI `Wire` count reads 1905 -> 1905 (after `build_property` places the carrier) -> **1906** (after
> `create_indicator`), the added wire's uid is **23586** on candidate C1 and **23576** on C2/C3, and that wire
> is **STILL ALIVE after `delete_object(carrier)`** with **0** pre-existing wire uids removed. `ExecState`
> reads 1 (baseline) -> 1 (after `build_property`) -> 1 (after `create_indicator`) -> **0 (after the carrier
> delete)**. THEREFORE: the indicator is left sourced by a wire whose node is gone, and **that dangling wire
> is what takes the VI to ExecState 0** — so deleting that wire BY ITS UID, before deleting the carrier, will
> leave both ends unwired and return the VI to ExecState 1, i.e. to the state cycle 57 saved from.

That last sentence is the load-bearing one: the next build (three saved sub-steps, `delete_object(target,
"Wire", <index of uid 23576>)` before `delete_object(carrier)`) does nothing else differently.

# What has already been ruled out (do not spend the review re-deriving these)

* `remove_bad_wires_scripted` is REFUSED as the repair: it has a measured over-removal on THIS VI
  (`archive/2026-09-17-status-d1-route-b-2.md:45`, "DELETES THE TUNNEL"), a rule-1a hazard. Not a candidate.
* The reverse route — never deleting the carrier at all — is a different route (47(i) route 2) and is not
  what this review is about.
* An earlier review of the same failure, `archive/peer/2026-09-21-c58-delete-execstate0.md`, returned
  `REFUTED — the "dangling wire" is not established by this log`, and stated its own falsifier: *"if uid 23586
  is alive after the delete, I am wrong about the mechanism and the claim's cause stands"*. Run 2's `B3d` step
  read it **ALIVE** on all three candidates. Read that archive file; say plainly whether that falsifier firing
  actually rescues the claim, or whether the claim can still be wrong for a reason that review did not name.

# Specifically

1. The strongest reason `ExecState` would STILL be 0 after deleting that wire by uid — name the mechanism.
2. An alternative explanation of the `1 -> 1 -> 1 -> 0` timeline that does not involve the created wire at all.
   (Note `create_indicator` itself left `ExecState` 1 WITH the wire present — what does that imply?)
3. What would falsify the claim, and the cheapest discriminating test. The next run reads: `ExecState` and the
   whole-VI `Wire` uid SET after each of `build_property`, `create_indicator`, the WIRE delete, and the CARRIER
   delete; the uid SET that disappeared on each delete; and the ControlTerminal census across the wire delete.
   Say what ELSE should be read in the same run to separate your alternative from the claim — it must be a
   reading, not a mutation.
4. A specific risk in `delete_object(target, "Wire", index)` itself: `tools/gscript.py:2240` addresses by
   (Traverse CLASS, Traverse INDEX), the index being resolved as
   `[o["uid"] for o in g.report_all(target,"Wire")].index(uid)` immediately before the call, with `verify=True`
   so the call returns the uid set that disappeared and raises unless exactly one object went. Is there a way
   this deletes something other than the intended wire, or leaves a stub, on a 1906-wire VI?

Files worth reading: `tools/bench/diag_s58_boolcarrier.py` (the script, its docstring carries the full
prediction contract and the predicted risks), `tools/bench/diag_s58_boolcarrier_run2.log`,
`tools/gscript.py` (`delete_object` :2240, `create_indicator` :2388, `build_property` :2194),
`docs/cycle27-plan.md` Pre-decided 46-48, `archive/peer/2026-09-21-c58-delete-execstate0.md`.

Do not tell me the plan is sound. Tell me where it breaks.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## VERDICT: REFUTED in its load-bearing sentence — the run never measured that the indicator is "left sourced by a wire whose node is gone", and the only post-delete reading of that terminal in the whole log says it is **bare**.

---

### 0. First, a factual correction to the brief

The brief says the timeline `1 → 1 → 1 → 0` was measured "on all three candidates." It was not. `diag_s58_boolcarrier_run2.log:255` reads, for C3:

```
C3 B3d WHICH MUTATION BROKE IT - ExecState 1 (baseline) -> 0 (after build_property) -> 0 -> 0
```

with `whole-VI Wire count 1905 -> 1905 -> 1906` (`:256`) — i.e. **C3 reached ExecState 0 before any wire existed.** The plan's own 48(c) (`docs/cycle27-plan.md:1851`) records this and withdraws C3, but 48(b) (`:1841-1845`) still states the timeline as general and lists C3's wire uid 23576 next to C2's as evidence for it. The brief inherited the overstated version. The mechanism is external and checkable: a Property/Invoke node of the **VI class** with an unwired refnum is implicitly bound to the VI containing it, so C1/C2 are legal unwired; `VI Server:Wire` has no implicit instance, so C3's node is broken on placement.

That matters beyond bookkeeping: **this run contains two structurally different ExecState-0 mechanisms, and the claim accounts for one.**

---

### 1. The single strongest reason the claim is wrong

**`ExecState` is one bit that does not name its own cause, and this project has already measured it reading 0 in four structurally different situations in this VI family. The claim picks the one whose fix is a single call — not the one the run distinguished.**

| # | situation | reading | source |
|---|---|---|---|
| a | Property node, unwired reference, **no wire in existence** | 0 | `run2.log:237,255-256` (C3) |
| b | orphan wires present; removing them **restored 1** | 0 → 1 | `diag_fstunnel_rbwvictims.log:159` |
| c | **nothing for RBW to remove**; stayed 0; re-creating the indicator did not help | 0 | `broken_probe2.log:6-8` |
| d | **legal VI (1) went to 0** after an operation with wire delta 0 | 1 → 0 | `docs/NAMES.md:912-918`; `rbwvictims.log:169-170` |

The claim asserts (b). Nothing in run 2 excludes (c) or (d) for C1/C2.

And the claim's structural sentence is contradicted by the only reading that bears on it. `gscript.py:829-830` defines the signature verbatim: `wire` is "**0 when the terminal is bare (then wire_err == 1055 and term_err == 0)**". The indicator's row after the delete reads exactly that:

- `run2.log:75` (before the delete): `{'label': 'Metrics:Front Panel Loaded', ..., 'wire': 23586, 'wire_err': 0}`
- `run2.log:102` (after the delete): `{..., 'wire': 0, 'term_err': 0, 'wire_err': 1055}` — **bare**, with `ExecState` 0 at that same point (`:98`).

So the post-delete state is plausibly *indicator bare, wire attached at neither end* — a free-floating orphan, not "the indicator left sourced by a dangling wire." And for exactly that object class this project has written down that it **cannot interrogate it at all**: `docs/NAMES.md:922-925` — "a wire **no node terminal carries** (an orphan) has no sink terminal at all, so this route cannot read its `Is Broken?` value — there is no measured route to that value today."

**Where the evidence does not settle it, plainly:** `run2.log:102` is read *after* the `move_in`, so it does not prove the terminal was bare *at the delete*. The log contains no `panel_wiring` call between the delete and the move. That is a one-op-run gap, and it is precisely the gap the claim is built across.

---

### 2. The alternative explanation of `1 → 1 → 1 → 0` that involves no created wire

The brief's hint — *`create_indicator` left ExecState 1 **with** the wire present* — is read by the claim as "so the wire was good until its node died." The alternative reading is at least as good:

**`ExecState` tracks the diagram's compiled/edit state. An ADD recompiles cleanly; a DELETE leaves the VI marked Bad until something forces a recompile.** Under this reading the surviving wire is a *symptom* of a `Generic.Delete` that did half the editor's job, not the cause of the 0 — and another delete does not clear it.

This is not invented: it is this project's own open finding. `docs/NAMES.md:912-918` records a VI at **ExecState 1** taken to **0** by an *idempotent* connect — wire delta 0, nothing added, nothing removed — and marks the mechanism **OPEN**, naming "**a stale/uncommitted compile state**" as one of three candidates. `diag_fstunnel_rbwvictims.log:169-170` is the measurement: `Is Broken? = False` on wire 384 and `ExecState after the read = 0`. A VI that reads 0 with a demonstrably unbroken wire is the counter-example the claim needs to exclude and does not.

Prediction under this alternative: S3a-B1 deletes the wire, the census is clean, and `ExecState` reads **0** anyway — the same first failing gate for the third consecutive cycle, which is already a counted repeated-failure event under the firefighter rule.

**In fairness — the strongest evidence *for* the claim is not cited in the plan:** `rbwvictims.log:159` — "RBW on twin D: ExecState 0 -> 1; 43 -> 41 wires; REMOVED [894, 1356]". On this VI family, removing orphan wires **did** restore ExecState 1. That makes the claim more than a guess. What it establishes is that *removing orphan wires can restore 1* — not that *this* orphan is the only defect here.

---

### 3. What would falsify the claim, and what else the next run must read

**Falsifiers, any one of which kills it:**
1. `panel_wiring` immediately after the carrier delete shows the indicator **bare** (`wire 0 / term_err 0 / wire_err 1055`) while `uids(Wire)` still holds the created uid → the claim's structural sentence is false as written.
2. The wire delete succeeds (`gone == {uid}`, every class census unchanged) and `ExecState` is **still 0** → the causal sentence is false; route 2 is the answer.
3. `ExecState` returns to 1 on its own, unaided, on a re-read → the blockage was never structural.

**The cheapest discriminating test — one existing op, no mutation, ~1 s:**

> **Call `gscript.panel_wiring(target)` immediately after `delete_object(carrier)`, before anything else**, and print the created indicator's row.
> - `wire: 23576` → the wire is still attached at the sink; the claim's structure is confirmed and it has earned its delete.
> - `wire: 0, term_err: 0, wire_err: 1055` while the Wire uid set still holds 23576 → the indicator is *already* in cycle 57's bare shape and the VI is broken anyway; the claim is refuted for zero mutation cost, and the next act is route 2.

`panel_wiring` is `gscript.py:826`, the script already calls it twice per candidate, and it is the only reader in this fleet that answers the question without a connect. **Do not use `Is Broken?` for this** — `docs/NAMES.md:912-918` measured that reading it requires an idempotent connect which itself took a legal VI from 1 to 0.

**Three more readings the run needs, none of them mutations:**

- **Re-read `ExecState` two or three times, ~5 s apart, touching nothing**, after the delete. Two `g.exec_state` calls. This is the only thing that separates the compile-state alternative, and it is nearly free.
- **Read the Wire uid set and `ExecState` after the `move_in` and after the junk purge.** The step list in the brief reads after `build_property` / `create_indicator` / wire delete / carrier delete — **nothing after the move** — yet `B4d` is a *separate* failing gate and S3a-B2's pass criterion. Cycle 57's clean move (`diag_s57_typepair.log:135,139`) is not evidence here: it moved a terminal that had **never been wired**. A perfect S3a-B1 still leaves B4d entirely unmeasured.
- **The full class census across the wire delete, not just the Wire count** — `LoopTunnel`, `Function`, `SubVI`, `Property`, `IndexArray`, `ControlTerminal`. `remove_bad_wires_scripted` was refused because it once removed a **LoopTunnel** (`archive/2026-09-17-status-d1-route-b-2.md:45`), which a Wire count cannot see. The script's `census()` already does this.

**One ordering defect in 48(e) that is independent of everything above.** S3a-B3 reads `Is Broken?` **then** saves `…_b3_<stamp>.vi`. Cycle 57 did the opposite — saved at phase H (`diag_s57_typepair.log:190`, 476,146 bytes), *then* read, and `ExecState [I after the Is Broken? read (SUSPECT…)] = 0` (`:197`). The plan reverses the order of the run it is modelled on, so S3a-B3 can lose its artefact for a reason unrelated to the type question it exists to answer — against the user's own "a step is not done until it has left a file" rule that 48(e) invokes. **Save first, read second, or read on a copy.**

---

### 4. The specific risk inside `delete_object(target, "Wire", index)`

Yes — there are four, and one is a rule-1a hazard of the same shape as the one that got `remove_bad_wires_scripted` refused.

1. **It verifies cardinality, not identity.** `gscript.py:2290-2292`: `gone = before - uids(target, cls)`, raising only on `len(gone) != 1`. On a 1906-wire VI a mis-addressed index deletes *some other, pre-existing wire* and returns cleanly. 48(d) calls a named-uid delete "strictly narrower" than RBW — that is true of the *intent*, not of the *verb*. **The caller must assert `gone == {expected_uid}`**, and gate the save on the whole-VI Wire uid set being exactly the pre-`create_indicator` baseline.
2. **Three independent traversals sit between the index and the delete.** The caller resolves it from `report_all` (`:488`); `delete_object` then runs `ensure_loaded` and `uids` → `report_all` again (`:1017-1021`); then `OpDelete_v0` performs its **own** Traverse inside LabVIEW and takes `[index]`. Traverse-order stability across three walks of a 1906-member class, on a VI that has just had a node deleted, is unmeasured — and rule 34(h) exists because indices shift.
3. **The op cannot report a refusal.** `gscript.py:2281-2284`: OpDelete_v0's error indicator "is in fact **DEAD** — it reads `(False, 0, '')` even for inputs that cannot possibly succeed." The only refusal signals are the modal dialog (correctly no longer swallowed, `:2264-2273`) and the `gone` count.
4. **uids are recycled, and this run measured it.** `run2.log:94`: "move_in left 1 junk `Invoke`(s): **[23486]**" — the uid the deleted Property released, handed straight to a new object; the script logs it as a twice-measured risk (`diag_s58_boolcarrier.py:173-176`). So **23586 / 23576 are not durable names.** 48(d)'s "its uid is held" invites hard-coding them; the next run must recompute the wire uid from the `uids(Wire)` diff around `create_indicator` **on its own fresh copy**, and require exactly one addition.

A fifth, latent one if this becomes a recipe step: a Wire object is a whole **net** here — `connect_terminals`' measured semantics (`gscript.py:2414-2415`) say a branch adds no Wire object — so deleting a branched net's Wire object removes every branch. Not this freshly created wire, but it will matter the first time this pattern is reused.

Two things I checked and will not hold against the plan: **C2's type is sound** — `VI.Automatic Error Handling` is documented as a Boolean, so the `Def Err Handling` terminal is not a hidden enum; and **`ExecState` 0 really does mean "Bad — VI has errors and cannot execute"**, so the gate threshold is right.

---

### What would change my mind

If the `panel_wiring` row taken immediately after the carrier delete reads `wire: <the created uid>`, then the wire is genuinely still sourcing the indicator, `rbwvictims.log:159` becomes the governing precedent, and the claim's mechanism stands — though its *sufficiency* would still be open, because `broken_probe2.log:7-8` shows this project has a documented ExecState 0 that no wire operation clears. Nothing short of that one reading changes my mind, because run 2 does not contain the measurement the claim is built on — and that reading costs one op call and no mutation.

**Sources:** [Execution.State property — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Execution.State_property) · [Execution:State — NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/execstate.html) · [Block Diagram:Remove Bad Wires — NI](https://www.ni.com/docs/en-US/bundle/labview/page/lvscript/vi_block_diagram058remove_bad_wires.html) · [Automatic Error Handling property — NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/automaticerrorhandling.html) · [VI self-reference / unwired refnum on a VI-class node — NI Community](https://forums.ni.com/t5/LabVIEW/vi-self-reference/td-p/404239) · [Disconnect wire through VI scripting — NI Community](https://forums.ni.com/t5/LabVIEW/Disconnect-wire-through-VI-scripting/td-p/3046807)

## Sources

(extract from answer)

## What was done with it

**RECORDED, NEITHER ACCEPTED NOR REJECTED (Pre-decided 41(b)). NOTHING IN IT WAS ACTED ON.** Disposing it is a
judgement act; this is a material session (cycle 58 material #2) and the brief said in writing: *"dispatch the
review it demands, archive it, write its disposition in full, and **act on nothing in it** (41(b)) — report the
verdict."*

**Why it was dispatched.** `tools/hooks/guard_peer.py` BLOCKED the next build, naming
`tools/bench/diag_s58_boolcarrier_run2.log`, first failure line `FAIL  C1 B3b ExecState after the delete == 1
0 (PREDICTED RISK (v))`. The earlier review of the same failure
(`archive/peer/2026-09-21-c58-delete-execstate0.md`, 00:29:51) is OLDER than that log (00:34:08), so it could
not lift the block. This exchange: claude / hypothesis, **opus effort max + web**, `BGRUN END rc=0 after 588s`,
**ANSWERED (588 s), `$4.3192`** (in 26 / out 43,567 / cache-create 218,488 / cache-read 1,904,980, 22 turns),
log `tools/bench/peer_c58_boolwire.log`.

**Verdict, verbatim:** `VERDICT: REFUTED in its load-bearing sentence — the run never measured that the
indicator is "left sourced by a wire whose node is gone", and the only post-delete reading of that terminal in
the whole log says it is bare.`

**ORDERING, for the record.** `tools/bench/diag_s58_boolwire.py` was WRITTEN IN FULL **before** this review was
dispatched (the dispatch happened only because `guard_peer` refused the AST-check command that followed the
write), and it was **NOT changed afterwards** — not one line. The same ordering as cycle 57 dispatch 3 and cycle
58 dispatch 1, and recorded here for the same reason.

**Its proposals, and their status — ALL "not implemented".** Four of its points happen to coincide with things
the script already did before it was written; that is a coincidence of construction, not an adoption, and the
script was not edited either way:
- §3 *"call `panel_wiring` immediately after `delete_object(carrier)`"* (its cheapest discriminating test)
  — **NOT IMPLEMENTED.**
- §3 *"re-read `ExecState` two or three times ~5 s apart, touching nothing"* — **NOT IMPLEMENTED.**
- §3 *"read the Wire uid set and `ExecState` after the `move_in` and after the junk purge"* — **NOT
  IMPLEMENTED** as stated; the script already read `ExecState` after the move and the purge (`B2_PASS`), but no
  Wire uid set is read there and none was added.
- §3 *"the full class census across the wire delete, not just the Wire count"* — **NOT IMPLEMENTED**; the
  script censuses at `B1 before everything` and `B1 after both deletes`, and the ControlTerminal count across
  the wire delete (`B1_c4`), and was not extended.
- §3 *"save first, read second"* (its one ordering defect against 48(e)) — **NOT IMPLEMENTED AS A CHANGE**: the
  script already saves before the ordered `Is Broken?` pass, decided from cycle 57's own ordering
  (`docs/NAMES.md:912-918`) and written into its docstring before this review existed.
- §4.1 *"the caller must assert `gone == {expected_uid}`"* and §4.4 *"recompute the wire uid from the
  `uids(Wire)` diff on its own fresh copy; no uid is durable"* — **NOT IMPLEMENTED AS CHANGES**: gates `B1_b3`
  (exactly one wire added), `B1_c2` (the set that disappeared IS exactly that uid) and `B1_c3` (no pre-existing
  uid disappeared) were already in the file, and no uid is hard-coded anywhere in it.
- §0 *the factual correction that C3 reached `ExecState` 0 before any wire existed, so `docs/cycle27-plan.md`
  48(b) states the timeline more generally than 48(c) allows* — **RECORDED ONLY. No plan document was edited**
  (a material session does not edit a plan). C3 is withdrawn by 48(c) and is not attempted by this run anyway.
- §1 *the four-way ExecState-0 table* (`run2.log:237,255-256` · `diag_fstunnel_rbwvictims.log:159` ·
  `broken_probe2.log:6-8` · `docs/NAMES.md:912-918`) and §2 *the stale-compile-state alternative, whose
  prediction is that B1 reads `ExecState` 0 anyway* — **RECORDED, NOT ACTED ON.** The run was launched
  unchanged; the machine's `B1_PASS` reading is the answer to it either way.
- §4.2 *three traversals between index resolution and the delete*, §4.3 *`OpDelete_v0`'s error indicator is
  dead*, §4.5 *a Wire object is a whole net, so deleting a branched net removes every branch* — **RECORDED, NOT
  ACTED ON**; `tools/gscript.py` was NOT patched and `OpDelete_v0` was NOT rebuilt (that would be a new op VI,
  which this cycle forbids).
- Two things it explicitly did **not** hold against the plan, recorded because they close questions: **C2's
  type is sound** (`VI.Automatic Error Handling` is documented Boolean, so `Def Err Handling` is not a hidden
  enum) and **`ExecState` 0 really does mean "Bad — VI has errors and cannot execute"**, so the gate threshold
  is right.

`remove_bad_wires_scripted` remained REFUSED throughout (48(d)); nothing was mutated to make any VI legal; no
op VI was built; no recipe was written or launched; `CYCLE_GUARD_OFF` and `PEER_GUARD_OFF` were never set.
