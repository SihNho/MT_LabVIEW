# c60-cast-seed-execstate0

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.8363  in 26 / out 49081 / cache-create 264904 / cache-read 1799250  (641s, 23 turn(s))
- **date:** 2026-09-21 08:04:01
- **outcome:** ANSWERED (643s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the claim below. It is the explanation formed under pressure for the ONE failing gate in
`tools/bench/diag_s3b_l0_localname_v2.log` (`BGRUN END rc=1 after 101s`, 29 pass / 1 fail). Your job is to
find the strongest reason it is WRONG, to name an alternative explanation, to say what would falsify it, and
to name the CHEAPEST discriminating test. Do not confirm it.

Files you may read (read-only): `tools/bench/diag_s3b_l0_localname_v2.log`,
`tools/bench/diag_s3b_l0_localname_v2.py` (the diagnostic; the function at issue is `_s2_body()`),
`tools/bench/diag_s3b_l0_localname_v2.json`, `tools/recipes/build_oploopcast_v0.py` (the fleet's seed
mechanism of record, lines 4-8 and steps 6-7), `tools/recipes/build_opnodelabels_v0.py` (the donor's own
builder), `tools/gscript.py` (`create_control` :2360, `wire_control` :1928, `wire` :1340, `build_property`
:2194, `delete_object` :2240, `loop_cast` :626, `connect_terminals` :2415), `docs/toolkit-capabilities.md`,
`docs/NAMES.md`, `docs/cycle27-plan.md` Pre-decided 49 and 50.

== THE FAILING GATE, VERBATIM FROM THE LOG
  FAIL  S2_b10 ExecState == 1 after the indicator  *** THE OP'S PASS CRITERION ***  0

== WHAT WAS BUILT, in order, each line a reading from the same log
  S2_b1 build_property('VI Server:Local', [('6355400', False)]) -> Property #1025, error column '',
        Property census 7 -> 8; its terminal table carries `CtrlName` at i=4 as a SOURCE.
  S2_b3 create_control(Nodes[13].Terminals[0] = the `reference` SINK) -> ControlTerminal #1076, label read
        off the machine as 'reference', ControlTerminal 19 -> 20, ExecState still 1.
  S2_b4 that control was born WIRED (wire 1086 on `reference`); the wire was deleted by uid
        (gone [1086], no collateral).  *** ExecState reads 0 HERE, before the TMSC is touched at all. ***
  S2_b5 the TMSC's original `target class` wire 772 deleted by uid (gone [772], no collateral). ExecState 0.
  S2_b6 wire_control(['reference'] -> Function[0].`target class`): Wire 29 -> 30, error column '',
        `target class` row afterwards {'i': 2, 'wire': 1030}. ExecState 0.
  S2_b7 the cast output wire 645 fed exactly ONE sink (#235 Property Node `reference`); 645 deleted by uid;
        create_control on that orphaned sink -> ControlTerminal #1083, label 'reference 2'. ExecState 0.
  S2_b8 wire Function[0].`specific class reference` -> Property[0].`reference`: Wire 30 -> 31, error column
        '', `reference` row afterwards {'i': 0, 'wire': 1085}; the `CtrlName` row SURVIVED the wire.
        ExecState 0.
  S2_b9 create_indicator on `CtrlName` -> ControlTerminal #1102, one new panel label 'Control Name'.
        ExecState 0.  Final census: Node 16, Wire 32, Property 8, ControlTerminal 22.
  Nothing was saved, nothing was repaired, the unsaved copy was removed, the donor is byte-unchanged.

== THE CLAIM UNDER ATTACK
"The ExecState 0 is not evidence against the cast. It first appears at S2_b4 - before the TMSC is touched -
and is fully explained there by the new `VI Server:Local` property node standing with a BARE `reference`
input, which is a broken node in LabVIEW. Every later step left it at 0 simply because the graph was
unfinished until S2_b9. What is left unexplained is only the LAST reading: after b8 and b9 every terminal
this run touched is wired, so the VI should have returned to ExecState 1 and did not. The most likely
remaining cause is that a front-panel refnum CONTROL of class `Local` does not legally type
`To More Specific Class`'s `target class` - because the donor's own seed is NOT a control: this run
measured that NO node on that diagram produces wire 772 (0 producers) and that NO front-panel object carries
it either (`panel_wiring` returned 19 rows, none with wire 772), leaving a diagram CONSTANT as the only
remaining kind of object - i.e. the class-specifier constant `docs/toolkit-capabilities.md` calls 'the one
missing seed', which this fleet cannot create. On that reading the seed mechanism of record
(`build_oploopcast_v0.py:4-8`, 'any refnum WIRE of the wanted class types it') was reproduced only in form,
not in substance, and the `Local` cast is not reachable from a control."

== WHAT THE BUILD IS FOR (context, not part of the claim)
The deliverable is `claudeDev\OpLocalName_v0.vi`, a ONE-PROPERTY READER of a Local Variable's binding
(Traverse `Local` by index -> `Local.Control Name` 6355400 -> string out). No reader of a Local's binding
exists in this fleet at all; the eight pre-existing Locals in the main VI all return the VI's FILE NAME
through `Node.Label` 6359001, which is why the reader is being built.

== ALREADY RULED OUT (do not spend your answer on these)
1. "The donor is the wrong file / was modified": `OpNodeLabels_v0.vi` md5 `376ff12569008ebac25a524e0887030b`
   before AND after; the copy opened at `ExecState` 1 before any edit.
2. "The property ID does not resolve": `build_property('VI Server:Local', [('6355400', False)])` returned
   error column '' and produced a `CtrlName` SOURCE row, twice now (this run and
   `tools/bench/diag_s3b_l0_localname_run2.log:50-56`).
3. "Something was silently declined": every step above was verified BY EFFECT (uid sets, wire uids on named
   terminals, census diffs), not by a return code.
4. "The originals were touched / references leaked": four md5 pins unchanged before and after, refs
   12 opened / 12 closed / 0 live, the scratch deleted in the same run, `tools/recipes/` unchanged (158
   files before and after).
5. "Just run Remove Bad Wires": forbidden by the brief and by the project's standing rules; not called, not
   imported. Do not propose it.

== WHAT THIS SESSION MAY NOT DO WITH YOUR ANSWER
It is a MATERIAL session under this project's judgement/material split: it may not choose a route, switch
donors, or build an alternative op. So aim your answer at the DIAGNOSIS and at the cheapest DISCRIMINATING
TEST a later session could run, not at a redesign.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## The claim is REFUTED on its conclusion. Its key citation is a heading the cited file struck through.

---

### 1. The single strongest reason it is WRONG

**`docs/toolkit-capabilities.md` does not call the class-specifier constant "the one missing seed". It calls it that with a strikethrough, under a heading that says SOLVED, and the text underneath states the opposite of the claim.**

`docs/toolkit-capabilities.md:84-89`, verbatim:

> `### ~~The one missing seed~~ SOLVED 2026-09-14 15:1x without GUI — the typed-control seed (INDEX row 28)`
> "`To More Specific Class`'s `target class` accepts **any wire of the target type** (NI doc, confirmed by codex), not only a class-specifier constant. **A refnum CONTROL of the wanted class is made by `Terminal.Create Control` on the `reference` INPUT of a property node already configured to that class**…"

That sentence describes S2_b3 verb for verb. And it is not a proposal — it shipped and was measured:

- `docs/toolkit-capabilities.md:27` (INDEX row 28, `loop_cast`): *"**The first cast-free TYPED cast**: the TMSC's target class is a refnum CONTROL of that class"*, `test_oploopcast.log` **13/13**.
- `tools/recipes/build_oploopcast_v0.py:19` — step 7 `wire_control([L] -> TMSC 'target class')`, **predict: `ExecState 1`**.
- This run's own log confirms the artefacts exist: `OpLoopCast_v0.vi: True`, `OpWhileCast_v0.vi: True` (`diag_s3b_l0_localname_v2.log:73-74`).

So the claim **inverts its own source**. `build_oploopcast_v0.py:4-8` invented the control route *because* the constant is unmakeable; "the donor used a constant" is therefore irrelevant to whether a control works. "Reproduced only in form, not in substance" is backwards — the run reproduced the documented mechanism in substance, down to the label `reference`.

Two more supports collapse with it:

- **The hierarchy permits the cast.** `Local` ← `Node` ← `GObject` ← `Generic` ([Local class](https://labviewwiki.org/wiki/Local_class), [Node class](https://labviewwiki.org/wiki/Node_class), [GObject class](https://labviewwiki.org/wiki/GObject_class)). `Traverse for GObjects.vi` emits a GObject-rooted refnum, so GObject → `Local` is the same descendant downcast shape as the donor's own GObject → `Diagram`.
- **The seed control IS a legal `Local` refnum, and the log proves it.** At b3 that control drove the `VI Server:Local` property node reading `CtrlName` and the VI read **`ExecState` 1** (`log:88`). A non-`Local` refnum there would have invalidated `Control Name`.

**Bonus factual error:** the 0 does *not* first appear at b4. It appears at **b1** (`log:83`, `ExecState [S2 after build_property] = 0`), recovers to **1** at b3 (`log:88`), falls to 0 at b4 (`log:95`). That clean 0→1→0 toggle supports the bare-reference half *better* than the claim states — and it is the same reading that kills the claim's conclusion.

### 2. Alternative explanations of the same evidence

**(A) There is no clean `ExecState 1` checkpoint after b4, so b5–b8 are each unmeasured.** Everything from b4 on was read on a VI already at 0. "Every later step left it at 0 simply because the graph was unfinished" is an assumption the run's ordering made untestable — any of b5–b8 could have added a second, masked breakage. The least-examined is **b7**, the vestigial-chain detach (delete 645, `create_control` on `#235.reference`), which touches neither `Local` nor the seed.

**(B) "The wire landed" was never "the wire is good."** Gates b6/b8 pass on empty error column + non-zero wire uid. `tools/gscript.py:2415`: **"Type mismatches make a broken wire."** A broken wire has a uid and sits on the terminal row — so that evidence cannot distinguish a good seed from a bad one in either direction.

**(C) `ExecState` is the wrong instrument for this question, by this project's own measurements.** `docs/cycle27-plan.md:1465-1468` (Pre-decided 42(c), cycle 55): **"`ExecState` IS NOT A TYPE DISCRIMINATOR AND MUST NEVER BE USED AS ONE"** — it fell 1→0 on the type-**matched** leg. `docs/NAMES.md:912-918`: an ExecState-1 scratch read 0 after an operation that broke nothing. `docs/cycle27-plan.md:151-155` (14a): byte-identical files read 0 cold, 1 warm. The claim converts one `ExecState 0` into a verdict about a *type* relationship — precisely the forbidden use.

**(D) The one real difference from the validated recipe, which the claim did not name.** In `toolkit-capabilities.md:90-93` the seed is minted on a scratch copy, `copy_into`'d, and the minting node deleted. Here `#1025` is both the seed's birthplace and the cast's consumer (control → `target class` → TMSC → `#1025.reference`). Unexercised configuration — but that is a claim about construction order, not about controls.

### 3. What would falsify the claim

1. `OpLoopCast_v0.vi` at `ExecState` 1 with its TMSC `target class` wire carried by a **panel row**.
2. The b7 detach, run alone on a fresh copy, reading `ExecState` **0**.
3. An ordered `Is Broken?` pass at b9 showing wire **1085** broken while **1030** reads False.
4. No broken wire anywhere at b9 — then the broken object is a node.

### 4. Cheapest discriminating test

**Three calls, throwaway byte copy of `OpNodeLabels_v0.vi`, no new op, no save, no `Local`, no property node, <20 s — isolate b7:**

1. `exec_state(copy)` → expect **1** (also discharges 14a: the instance is warm).
2. `delete_object(copy, "Wire", index_of(645))`; `create_control(copy, Nodes[i of #235], 0)`.
3. `exec_state(copy)`.

**Reads 0** → claim dead: the final 0 is explained before the cast is involved. **Reads 1** → claim survives; next single-variable probe is b5+b6 alone (delete 772, `create_control` on `target class`, read `ExecState`) — still no `Local`.

**Free prior, read-only, ~10 s, same pass:** point the S1_a1–S1_a4 procedure already written in `diag_s3b_l0_localname_v2.py` at `claudeDev\OpLoopCast_v0.vi` and read which object carries its `target class` wire. A panel control there refutes the general form with zero edits.

⚠️ Do **not** reach for `Wire.Is Broken?` first — `docs/cycle27-plan.md:144-146` records it cannot be run read-only, and `docs/NAMES.md:912-918` measured that read turning an ExecState-1 scratch into 0. If used, ordered second pass only (42(b)).

### Where the evidence does not settle it

Nothing in this run identifies **which object is broken**. Four candidates stay live: wire 1030, wire 1085 / node `#1025`, the b7 chain, and "no structural break at all". I can refute the cause the claim names; I cannot name the real one from this log — and neither can the claim. The measurement that would have settled it (an ordered broken-object read, or a single-variable ordering) was not taken.

I could not write the plan file — `Write` is disabled in this session, which is correct for a read-only peer role. The review above is the whole deliverable.

**Sources:** [Local class](https://labviewwiki.org/wiki/Local_class) · [Node class](https://labviewwiki.org/wiki/Node_class) · [GObject class](https://labviewwiki.org/wiki/GObject_class) · [VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)

## Sources

(extract from answer)

## What was done with it

**RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b) grain).** This is a MATERIAL session; accepting or rejecting a
review, choosing a route and changing a plan are judgement acts. What follows is only what was DONE.

**ACTED ON — the two measurements it named as free / cheapest, and nothing else.** The devil's-advocate rule
requires a failed prediction to end in a discriminating test, so the review's §4 was executed verbatim as a
read-mostly probe that builds nothing, saves nothing and creates no op VI:
`tools/bench/diag_c60_castseed_probe.{py,log,json}` (AST OK `tools/bench/c60d_astcheck.log`,
`BGRUN END rc=0 after 3s`, **19 pass / 0 fail**).

1. **Its "free prior, read-only" test — and it REFUTES this session's premise on the machine, not on a
   citation.** `claudeDev\OpLoopCast_v0.vi` opens at `ExecState` **1**, its single TMSC #683 takes `target
   class` from **wire 333, and wire 333 is carried by a FRONT-PANEL CONTROL** — `panel_wiring` row
   `{'label': 'reference', 'indicator': False, 'uid': 297, 'is_source': True, 'wire': 333, 'term_err': 0,
   'wire_err': 0}`, with **0 node producers** (`diag_c60_castseed_probe.log:50`). A shipped, unbroken op in
   this fleet is seeded by exactly the kind of object this session's claim said could not seed one, and it
   even carries the same machine-given label `'reference'`. The review's §1 is therefore confirmed by
   measurement as well as by its citation.
2. **Its "cheapest discriminating test" — b7 isolated, and it reads the branch the review called "claim
   survives".** On a throwaway byte copy of `OpNodeLabels_v0.vi` (never saved, deleted in the same run,
   donor byte-unchanged): `ExecState` **1** untouched → delete the cast output wire 645 by uid
   (`gone [645]`, no collateral) → **0** → `create_control` on the single orphaned sink `#235.reference`
   (new ControlTerminal #1039, label `'reference'`) → **1** (`:74-80`). **The b7 detach is exonerated: it
   returns the VI to `ExecState` 1 on its own.**

**NOT ACTED ON.** Its §4 second step (the b5+b6-alone probe, offered only if b7 read 1 — which it did) was
**not run**: taking a review's conditional next step is accepting the review, which is judgement's call.
Its §3 falsifier 3 (an ordered `Is Broken?` pass on wires 1030 / 1085) was **not run** — the review itself
warns it cannot be read read-only and perturbs `ExecState` (`docs/NAMES.md:912-918`). No plan document was
edited, no `Pre-decided` line was written, `docs/toolkit-capabilities.md:84-93` was **not** amended even
though the review shows this session mis-cited it, no op VI was built or repaired, nothing was saved, and no
route was chosen or recommended. `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` were neither
imported nor called anywhere in this cycle; `allow_broken` was never True.

**WHAT STANDS UNRESOLVED, in the review's own words:** *"Nothing in this run identifies which object is
broken. Four candidates stay live: wire 1030, wire 1085 / node `#1025`, the b7 chain, and 'no structural
break at all'."* One of those four — the b7 chain — is now measured out.
