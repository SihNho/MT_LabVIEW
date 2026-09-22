# c79-rowd-writer

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.9166  in 18 / out 40945 / cache-create 236321 / cache-read 944181  (550s, 18 turn(s))
- **date:** 2026-09-22 09:47:55
- **outcome:** ANSWERED (554s)
- **why asked:** MANDATORY FAILED-PREDICTION REVIEW (CLAUDE.md §5). Pre-decided 111 asserted that
  (sink `FlatSequenceInnerTunnel #7468` LeftTerm #7488, source `Diagram #686`/`Nodes[21]`/`t1`) was an
  EXECUTABLE address pair for a writer already on disk; `tools/bench/c78_rowd_writer.log` measured that
  no writer in the fleet takes a uid-addressed sink, so `tools/recipes/build_d1_m3a3.py` halts at its
  own gate W1. Asked BEFORE the expensive construction the judgement call ("Row D gets a new writer
  op") would have started.
- **verdict:** ANSWERED — accepted in part; the build was HALTED, not started (see "What was done with it")

## Question

# REFUTE THIS: "Row D needs a NEW writer op, and OpFsInnerTunnelConnect_v0 is the smallest safe shape"

You are the failed-prediction reviewer. A prediction of ours failed; the explanation we formed under
pressure is below. **Attack it.** Your job is to find the cheapest route we have MISSED, or to show the
claim is wrong. Do not confirm.

## The situation, in one paragraph

We are restructuring a LabVIEW VI by VI Scripting over COM (a behaviour-preserving refactor: scheduling
may change, the computation may not). One remaining wire ("Row D") carries a VISA session handle out of
the OLD `WhileLoop #637` and must instead come out of the NEW `WhileLoop #23032`. Concretely:

- **SINK** (where the wire must land): the object `FlatSequenceInnerTunnel #7468`, specifically its
  **`LeftTerm` terminal, uid #7488**, which today carries wire 7506. (We delete wire 7506 first; a
  `Terminal.Connect Wire` into an ALREADY-WIRED sink is a measured silent no-op for us, so delete
  precedes connect.)
- **SOURCE**: `WhileLoop #23032`'s border terminal — addressable today as `Diagram #686`
  (Traverse('Diagram') index 19), `Nodes[21]`, `Terminals[1]`, name `'Outgoing Handle'`, `Is Source?`
  True, currently BARE.
- The writing verb is `Terminal.Connect Wire` **6349C03**, and it is **invoked ON THE SINK TERMINAL**
  (`Wire Source` = the source terminal, a GObject refnum). So any writer must be able to HOLD a
  reference to the sink terminal.

## The prediction that FAILED

Our plan asserted that the pair (sink #7488, source Nodes[21]/t1) was an EXECUTABLE address pair for a
writer we already own. The machine says the VERB does not exist in that shape:

- **Measured** (`tools/bench/c78_rowd_writer.log`): all FOUR op label maps on disk declaring method
  `6349C03` — `opconnectfromwire_v0`, `opconnectnested`, `opconnectnested_v1`, `opconnectnested_v2` —
  address their SINK as (`index`, `index 2`, `index 3`) = (diagram index, `Nodes[]` index,
  `Terminals[]` index). The count of writers whose sink is addressed **by a UID** is **0**.
  (`OpConnectFromWire_v0` takes its SOURCE from a wire uid, but its SINK is still the index triple.)
- **Measured** (`tools/bench/diag_c77_rowd_addr.log`, 5 gates pass / 0 fail, read-only on a scratch copy):
  `find_node` MISSES all three `FlatSequence` objects in the VI (#43914 nested, #12938 and #681
  top-level) across 173/173 diagrams, 635 nodes, 0 scan errors — the miss tracks the CLASS. In the VI
  Server class hierarchy a `FlatSequence` is a direct child of **`GObject`**, never of `Node`, so it is
  never a `Nodes[]` member and **no `Nodes[]`/`Terminals[]` address for #7468 or #7488 can exist**.
  `Diagram #686` has 27 `Nodes[]` rows and #681 is in none of them; `owner_of(#681)` is
  `TopLevelDiagram #536`, not `Diagram`.
- **Measured, and this is the opening**: our READER `OpFsInnerTunnelTerm_v0` (38/38 functional,
  `tools/bench/build_opfstunnelterm_v2_run1.log:160-161`) DOES reach the sink terminal by uid today:
  on uid 7468 it returns, every error column empty, `LeftTerm #7488` (wire 7506) and `RightTerm #7471`
  (wire 7448), with a self/cast echo of `'FlatSequenceInnerTunnel' #7468`. It also answers on an
  unrelated FSIT #123, so the capability is of the CLASS, not of the one target. It declares NO
  `method` key (`kind: IN`) — it is a reader only.

## The conclusion we drew, which you must attack

> Row D requires a NEW writer op, `OpFsInnerTunnelConnect_v0`: inputs = the inner tunnel's **uid** + a
> side selector (Left/Right) + the SOURCE terminal in the existing proven `(diagram, Nodes[],
> Terminals[])` index form. Body = read `FlatSequenceInnerTunnel.LeftTerm` / `.RightTerm` (the same
> property ladder `OpFsInnerTunnelTerm_v0` already uses) to obtain the sink TERMINAL reference, then
> invoke `Terminal.Connect Wire` 6349C03 **on that sink terminal** with the source terminal as
> `Wire Source`. It would be built additively, modelled on `OpStopFromNode_v0`, which already takes its
> SINK from a property read (`WhileLoop.Loop End Ref` 6362C00) and its SOURCE from a
> `Loop.Diagram → Nodes[] → IA → Node.Terms[] → IA` ladder.

## ALREADY RULED OUT — do not propose these

(a) **A `Nodes[]`/index address for #7468 or #7488** — measured impossible above (class, not owner).
(b) **An owner walk** from the tunnel up to a reachable structure — our `OpOwnerChain_v1` terminates
    SILENTLY when the owner class is `FlatSequenceFrame`: ClassName comes back but `owner_uid` is 0,
    `error 1055: Property Node`, cast-class echo empty (`docs/toolkit-capabilities.md:61`).
(c) **A GUI fallback** (clicking the wire in the LabVIEW editor) — forbidden for this work by a standing
    project decision; GUI is permitted only where scripting is verified unreachable AND the project
    decision allows it, and here it does not.
(d) **Re-pointing Row D at a different sink, or inserting/moving a structure** (e.g. adding a tunnel, a
    Local variable, a shift register, or moving the FlatSequence) — that is a STRUCTURAL MUTATION of the
    original's computation, refused by our rule 1a ("never change the original's computation; only
    scheduling may change").
(e) The NI facts already archived at `archive/peer/2026-09-22-c76b-m3a3-run2-failpred.md:104,132`
    (the class hierarchy and the `Nodes[]` membership rule) — do not re-derive them; refute them only
    with a citation that contradicts them.

## The two questions, answer BOTH explicitly

1. **Is there a computation-preserving route that writes this ONE wire using the ops that EXIST on disk
   today** (`OpConnectNested_v0/v1/v2`, `OpConnectFromWire_v0`, `OpStopFromNode_v0`,
   `OpFsInnerTunnelTerm_v0` (reader), `OpWireSource_v5`, `OpTunnelRead_v0`, `OpCreateConstOnTerm_v0`,
   `OpConnectCtl_v0`, `OpWireSR_*`) — with NO new op VI? If yes, name it concretely: which op, which
   inputs, why its sink reference resolves to #7488. **If such a route exists we will STOP and not
   build.**
   Consider in particular, and say why each does or does not work:
   - `Terminal.Connect Wire` invoked on the SOURCE terminal instead, with the sink as `Wire Source`
     (i.e. reversing which end the invoke sits on);
   - `Wire.Terms[]` 6371003 / `Wire.Is Broken?` 6371004 routes that reach a terminal from a WIRE uid,
     as `OpConnectFromWire_v0` does for its source side — can the same trick address a SINK?
   - `Tunnel.Inside Terminals[]` 6356000 / `Tunnel.Outside Terminal` 6356001, which our
     `OpTunnelRead_v0` uses by uid cast — does either yield a writable sink handle for a
     `FlatSequenceInnerTunnel`?
   - any documented NI method (e.g. on `Diagram`, `Structure`, `FlatSequence`, `Wire`) that creates a
     wire from a SOURCE terminal to a target object without needing a sink-terminal refnum.
2. **If a new op IS required, is `OpFsInnerTunnelConnect_v0` as described the SMALLEST ADDITIVE shape,
   or is something smaller/safer available?** E.g.: extending an EXISTING op additively (adding a
   uid-addressed sink ladder to `OpConnectFromWire_v0` rather than making a new VI); or a more GENERAL
   op (`OpConnectByUid`: sink addressed by a terminal UID directly via `UID to GObject Reference.vi` →
   cast to `Terminal`, which would serve every future uid-addressed sink, not just FSIT). Say which you
   would build and why, including the risk each carries.

## Output contract

Give me, in this order and nothing else:
- **STRONGEST REASON THE CONCLUSION IS WRONG** (one paragraph).
- **ALTERNATIVE EXPLANATION / ALTERNATIVE ROUTE** — concrete, or "none found, and here is the search I ran".
- **WHAT WOULD FALSIFY** the claim that no existing op can write this sink.
- **CHEAPEST DISCRIMINATING TEST** — a read-only or scratch-copy measurement, naming the exact op and
  inputs, that settles it in under ~2 minutes.
- **VERDICT**: `EXISTING-ROUTE: <name it>` or `NEW-OP-REQUIRED: <the smallest shape you would build>`.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## STRONGEST REASON THE CONCLUSION IS WRONG

The whole chain rests on one sentence that was **adopted, not measured** — and the source it was adopted from does not say it. `tools/bench/c78_rowd_writer.log:19` makes the load-bearing move ("6349C03 is INVOKED ON THE SINK TERMINAL … So a writer can only reach a sink it can hold a REFERENCE to") and cites `docs/NAMES.md:245` and `:847`. Open `:847` and it reads *"Wiring rule (**labviewwiki, adopted**): `Terminal.Connect Wire` 6349C03 is invoked on the SINK"*. I fetched that wiki page: it says only *"Connects a wire to the terminal. The wire source can be either another terminal or a node"*, and it **does not state which end the method is invoked on, nor that `Wire Source` must be a source terminal** ([Terminal class/Connect Wire method](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)). The one genuine local measurement, `tools/gscript.py:2411-2412` (2026-09-06), measured what happens to an already-wired **source** vs an already-wired **sink** — it never varied the invoke position, because every op in the fleet invokes on the sink by construction. So "the verb does not exist in that shape" is an inference from a convention, and it is the only thing standing between Row D and an op that is already on disk: **`OpConnectFromWire_v0` already holds a live, uid-addressed Terminal reference to #7488 whenever wire 7506 exists** (`Wire.Terms[]` 6371003 on uid 7506 returns both endpoints; `tools/bench/diag_c77_rowd_addr.log:85` shows the other endpoint is #637 t10, so #7488 is the second element). The census line "writers whose SINK is addressed by a UID: 0" (`c78_rowd_writer.log:33`) counts **the word the label map uses for that reference**, not the capability — `opconnectfromwire_v0_labels.json:11,17` calls it `wire_uid`/`wire_terms_prop` and files it under SOURCE purely because of where the existing op puts the wire.

## ALTERNATIVE EXPLANATION / ALTERNATIVE ROUTE

**The alternative explanation of the same evidence:** four label maps address their sink by an index triple not because `Connect Wire` requires it, but because all four descend from one donor (`OpConnect2_v0` → `OpConnectNested_v0` → `_v1` → `_v2` → `OpConnectFromWire_v0`, `docs/toolkit-capabilities.md:67-70`) whose sink ladder nobody has ever had a reason to replace. "Zero writers address a sink by uid" is a fact about our inheritance tree, not about LabVIEW.

**Concrete route to test before building anything — zero new ops:** call the existing `connect_from_wire(...)` wrapper (`tools/recipes/build_opconnectfromwire_v0.py:381`) with the two roles **swapped**: `wire_uid = 7506`, `term_index` = the index of #7488 in `Wire.Terms[]`, and sink triple = `(sink_diag=19, sink_node=21, sink_term=1)` — the NEW loop's `Outgoing Handle`, measured BARE at `diag_c77_rowd_addr.log:90-91`. The Invoke then sits on a bare terminal and receives #7488 as `Wire Source`. If `Connect Wire` resolves direction from the terminals rather than from the invoke position, Row D is written by an op that shipped on 2026-09-17.

**Now the four bullets the brief asked about, each answered:**

- **Invoking on the source instead** — this is the route above. Untested here, not excluded by any measurement we own, and the only thing that can make it fail is a direction check nobody has run.
- **`Wire.Terms[]` 6371003 to reach a sink** — **yes, and this is the point**: the property returns *all* terminals of a wire, not just its source. `OpWireSource_v5`'s documented method is to *"walk `term index` until error 1055; require exactly one terminal with `Is Source?` TRUE"* (`docs/toolkit-capabilities.md:60`) — the rows it discards are sinks. #7488 is one of them, today, on wire 7506.
- **`Tunnel.Inside Terminals[]` 6356000 / `Outside Terminal` 6356001** — **NO, definitively, and this one is dead by citation**: `FlatSequenceInnerTunnel` is `Generic → GObject → FlatSequenceInnerTunnel`; it is **not a `Tunnel`** and has no methods of its own ([FlatSequenceInnerTunnel class](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class)). `OpTunnelRead_v0` casts to `Tunnel` (`toolkit-capabilities.md:72`), so it cannot address #7468 at all. Its real properties are **`Left Terminal` 1C3A9000 / `Right Terminal` 1C3A9001** — which is exactly what `OpFsInnerTunnelTerm_v0` already reads.
- **A documented NI verb that wires without a sink refnum** — **none found.** The nearest is `Create Described Wire`, and NI's own prescription for an occupied terminal is *read `Joints[]`, delete the wire, re-create it with `Create Described Wire`* — a **Terminal method**, so it needs the same reference ([Script connect existing loose wires to case tunnels](https://forums.ni.com/t5/LabVIEW/Script-connect-existing-loose-wires-to-case-tunnels/td-p/4195933)). `Node.Connect Wires` is name-pair based and both ends must be Nodes ([Node class/Connect Wires method](https://labviewwiki.org/wiki/Node_class/Connect_Wires_method)) — FSIT is neither. And ruled-out (a) survives: `FlatSequence` really is `Generic → GObject → FlatSequence` ([FlatSequence class](https://labviewwiki.org/wiki/FlatSequence_class)). I could not break that one.

**On question 2 — the proposed shape is wrong twice over, even if a new op is required.** (i) The donor is wrong: `OpStopFromNode_v0`'s source ladder is `Loop.Diagram → Nodes[]`, i.e. anchored *inside the loop body*, but Row D's source is the loop **node's own border terminal** on Diagram #686. The correct donor is `OpConnectNested_v2`, whose source half is already `Traverse('Diagram')[index 6] → TMSC → Nodes[] → Terms[]` (`toolkit-capabilities.md:68`) — and replacing its *sink* head with a uid head is the **exact mirror of `OpConnectFromWire_v0`'s own W2–W11 build, which passed 42/1**. (ii) The shape is bigger than it needs to be: `OpConnectByUid` (uid → `UID to GObject Reference.vi` → TMSC(**Terminal** seed) → the Invoke's `reference`) drops the property node *and* the Left/Right side selector, and the Terminal-typed seed is free — `create_control` on the Invoke's own `reference` input, the same trick that made `OpConnectNested_v1`'s seed. It serves every future uid-addressed sink. Its one unmeasured assumption is whether `UID to GObject Reference.vi` resolves a **terminal** uid (we have only proven it on a tunnel uid, #7468, and on wire uids).

## WHAT WOULD FALSIFY

The claim "no existing op can write this sink" dies the moment `Connect Wire`, invoked on a **bare source** terminal with a **sink** terminal wired to `Wire Source`, produces a wire whose single `Is Source?` TRUE terminal is the one we invoked on. It survives if that call returns a direction error (something like "the source terminal is not a source"), or — worse and the case to watch for — if it *silently branches wire 7506*, giving a new wire whose source resolves to `WhileLoop #637` instead of `#23032`. That second outcome looks like success on a wire-delta check and is a rule-1a computation change; it must be read with `OpWireSource_v5`, not with a wire count.

Separately, my sub-claim that `OpConnectByUid` is the smaller build dies if `UID to GObject Reference.vi` cannot resolve uid 7488.

## CHEAPEST DISCRIMINATING TEST

One script, one scratch copy of the bed, ~2 minutes, nothing new built (the `bare()`/T2 pattern in `build_opconnectfromwire_v0.py:556-633` is the template):

1. `wire_source_owner(SCRATCH, 7506)` → record each `term index`, its `Is Source?` and owner. Take `i*` = the row that is **not** the source (owner `FlatSequenceInnerTunnel` #7468). *(≈10 s, read-only — this also supplies the `term_index` any later route needs.)*
2. `connect_from_wire(SCRATCH, wire_uid=7506, term_index=i*, sink_diag=19, sink_node=21, sink_term=1)` — the swapped call. Read all four returns: op `error out`, the op's own ordered `Is Broken?` / `UID 2`, wire delta, `ExecState`.
3. `wire_source_owner(SCRATCH, <the new wire>)` → **gate on the source terminal's owner being `WhileLoop #23032`, never on wire delta.** Owner `#637` = the silent-branch failure mode, and is a FAIL.
4. Same run, free: set `UID 3 = 7488` with the sink triple out of range (e.g. `sink_node=9999`) and read **`err_uidvi`** alone. Empty ⇒ terminal uids resolve ⇒ build `OpConnectByUid`; error ⇒ build the FSIT-ladder op.

Step 2 decides Q1; step 4 decides Q2's shape. Both are on a dated scratch, the five md5 pins are read before and after, and nothing touches the bed.

## VERDICT

**NEW-OP-REQUIRED — but not yet, and not that op.** Under the *strict* reading of `Connect Wire` the conclusion is right and no op on disk can write #7488; but that reading is an adopted convention whose cited source does not contain it, and the two-minute test above is cheaper than any build. If step 2 passes: `EXISTING-ROUTE: OpConnectFromWire_v0 with the roles swapped (wire_uid=7506 → Wire Source, sink triple = Diagram[19]/Nodes[21]/Terminals[1])`. If it fails, the smallest additive shape is **`OpConnectByUid` — `OpConnectNested_v2` + `UID to GObject Reference.vi` + one TMSC on a Terminal seed made by `create_control` on the Invoke's own `reference`** (fall back to `OpFsInnerTunnelConnect_v0` with `Left Terminal` 1C3A9000 only if step 4 shows terminal uids do not resolve). Not `OpStopFromNode_v0` as donor — its source ladder cannot address a loop's own border terminal.

**Sources:** [Terminal class/Connect Wire method](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method) · [FlatSequenceInnerTunnel class](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) · [FlatSequence class](https://labviewwiki.org/wiki/FlatSequence_class) · [Node class/Connect Wires method](https://labviewwiki.org/wiki/Node_class/Connect_Wires_method) · [Script connect existing loose wires to case tunnels — NI](https://forums.ni.com/t5/LabVIEW/Script-connect-existing-loose-wires-to-case-tunnels/td-p/4195933) · [Navigating from a Wire to a Node Using VI Scripting — NI](https://www.ni.com/docs/en-US/bundle/labview/page/navigating-from-a-wire-to-a-node-using-vi-scripting.html)

## Sources

(extract from answer)

## What was done with it

**CLASSIFIED: ANSWERED, ACCEPTED IN PART — the build it was gating WAS NOT STARTED.** This was the
failed-prediction review of Pre-decided 111 (it asserted an executable address pair for Row D; the
machine measured that no writer on disk takes a uid-addressed sink). The cycle-69 material brief set an
explicit halt: *"If the review names a concrete alternative route that works with existing ops, STOP and
report it — do not build."* **It named one** (`OpConnectFromWire_v0` with the roles swapped:
`wire_uid=7506` → `Wire Source`, sink triple = `Diagram[19]/Nodes[21]/Terminals[1]`), so
`OpFsInnerTunnelConnect_v0` was **not built**, `tools/recipes/build_d1_m3a3.py`'s `WRITERS` table and
gate W1 were **not changed**, and **LabVIEW was not opened at all** in this session. The bed
`claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e…` is untouched.

What is ACCEPTED as measured fact, here and now:

- **The load-bearing sentence is a convention, not a measurement.** `docs/NAMES.md:847` says
  "Wiring rule (**labviewwiki, adopted**)"; the peer fetched that page and it does not state which end
  `Terminal.Connect Wire` 6349C03 is invoked on. So `c78_rowd_writer.log:19`'s "so a writer can only
  reach a sink it can hold a reference to" is an inference from our own inheritance tree
  (`OpConnect2_v0 → OpConnectNested_v0 → _v1 → _v2 → OpConnectFromWire_v0`, one donor lineage), not a
  fact about LabVIEW. **This does not overturn the W1 measurement itself** — all four maps really do
  take the index triple — it overturns what that measurement was taken to prove.
- **`Tunnel.Inside Terminals[]` / `Outside Terminal` is DEAD BY CITATION** and must not be tried again:
  `FlatSequenceInnerTunnel` is `Generic → GObject → FlatSequenceInnerTunnel`, **not** a `Tunnel`
  (labviewwiki), so `OpTunnelRead_v0`'s cast cannot address #7468. Its real properties are
  `Left Terminal` 1C3A9000 / `Right Terminal` 1C3A9001 — what `OpFsInnerTunnelTerm_v0` already reads.
- **Ruled-out (a) SURVIVED the attack**: `FlatSequence` really is `Generic → GObject → FlatSequence`,
  so no `Nodes[]` address for #7468/#7488 exists. The peer states it could not break this.
- **No documented NI verb wires without a sink refnum.** `Create Described Wire` is a `Terminal` method
  (same reference problem); `Node.Connect Wires` needs both ends to be `Node`s.
- **The brief's proposed shape is wrong twice over even if a new op is needed** (accepted as a finding,
  not acted on): the donor should be `OpConnectNested_v2` (its source half already addresses a loop's
  own BORDER terminal on `Diagram #686`), not `OpStopFromNode_v0` (whose source ladder is
  `Loop.Diagram → Nodes[]`, anchored INSIDE the body); and `OpConnectByUid` (uid →
  `UID to GObject Reference.vi` → TMSC on a **Terminal** seed → the Invoke's `reference`) is smaller
  than `OpFsInnerTunnelConnect_v0` — it drops the property node and the Left/Right side selector and
  serves every future uid-addressed sink.
- **The failure mode to gate on** (accepted, carried forward): a swapped `Connect Wire` could *silently
  branch* wire 7506, producing a wire whose source resolves to `WhileLoop #637`. That passes a
  wire-delta check and is a rule-1a computation change. Any test of this route must gate on
  `OpWireSource_v5`'s source-terminal OWNER being `WhileLoop #23032`, never on a wire count.

**NOT DONE, and deliberately — it is the judgement session's call:** the peer's own cheapest
discriminating test (4 steps, ~2 min, a dated scratch copy of the bed) was **not run**. It mutates a
scratch through an op in a way the fleet has never used, and its outcome selects between three designs
(existing-op route / `OpConnectByUid` / `OpFsInnerTunnelConnect_v0`) — a design decision, and the brief
had already halted this session. It is carried as the OPEN line of the cycle-69 material report.

**JUDGEMENT DISPOSITION CLOSED 2026-09-22 — ACCEPTED IN PART, CARRIED BY `docs/cycle27-plan.md` Pre-decided
115–118.** Per candidate and per finding:

- **ACCEPTED — Pre-decided 115**: the "invoked on the SINK" sentence is an ADOPTED CONVENTION, not a
  measurement. `docs/NAMES.md` is annotated accordingly: the wiki page the line cites does not say which end
  the method is invoked on, the belief traces to one donor lineage, and the W1 census proves *"no writer in the
  fleet takes a uid sink"*, not *"this wire cannot be written"*. The W1 measurement itself is NOT disputed.
- **ACCEPTED — Pre-decided 116, route A first**: `OpConnectFromWire_v0` with the roles swapped (`wire_uid =
  7506` + the `Wire.Terms[]` index of #7488 as the SOURCE half; sink triple = the NEW loop's BARE
  `Diagram[19]/Nodes[21]/Terminals[1]`) is tried FIRST, on a dated scratch copy, by the review's own ~2-minute
  test, because it needs nothing built. If it passes, Row D proceeds on it in the same dispatch and NOTHING NEW
  IS BUILT.
- **ACCEPTED BUT DEFERRED — Pre-decided 116, route B**: `OpConnectByUid` (uid → `UID to GObject Reference.vi`
  → TMSC on a **Terminal** seed → the Invoke's `reference`, donor `OpConnectNested_v2`, NOT `OpStopFromNode_v0`)
  is agreed to be the smaller and more general shape, and its unmeasured assumption (whether that VI resolves a
  TERMINAL uid) is its first gate. It is expensive construction: it stops for a FRESH CYCLE and is not
  improvised at the end of a dispatch.
- **REFUTED/WITHDRAWN — candidate C, `OpFsInnerTunnelConnect_v0`**: the shape this review was dispatched to
  attack is withdrawn on the review's own reasoning (wrong donor, needlessly specific), and was never built.
- **ACCEPTED — Pre-decided 117**: the branch hazard is gated on OWNER IDENTITY, never on a count. A swapped
  connect could silently branch wire 7506 into a wire whose source is still owned by the OLD `WhileLoop #637`
  — a rule-1a computation change that passes every count-shaped gate — so `OpWireSource_v5` must report the
  source terminal's owner as `WhileLoop #23032` on the ordered idempotent second pass.
- **ACCEPTED — Pre-decided 118**: the dead ends are recorded in `docs/NAMES.md` so they are not re-tried —
  `Tunnel.Inside Terminals[]` 6356000 / `Tunnel.Outside Terminal` 6356001 can never address #7468 (a
  `FlatSequenceInnerTunnel` is not a `Tunnel`; its real properties are `Left Terminal` 1C3A9000 / `Right
  Terminal` 1C3A9001), `Node.Connect Wires` needs both ends to be `Node`s, and `Create Described Wire` is
  itself a `Terminal` method.
- **The review's ruled-out (a) SURVIVED its own attack** and is unchanged: `FlatSequence` is
  `Generic → GObject → FlatSequence`, so no `Nodes[]` address for #7468/#7488 exists (the same fact as
  Pre-decided 110).

The peer's cheapest discriminating test remains the NEXT executable step and is still unrun as of this
disposition; nothing in `tools/recipes/`, `tools/gscript.py` or any `.vi` was changed on the strength of this
review.
