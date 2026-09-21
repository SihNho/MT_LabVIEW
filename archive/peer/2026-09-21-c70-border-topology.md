# c70-border-topology

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.5710  in 24 / out 45634 / cache-create 165270 / cache-read 1417620  (599s, 21 turn(s))
- **date:** 2026-09-21 22:59:29
- **outcome:** ANSWERED (603s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

We wired two rows across a LabVIEW loop border with VI Scripting and then failed our own acceptance gates. We want the strongest case that our NEW explanation is also wrong.

PREDICTION (ours, written before the run): after a correct border write, (i) the source wire would show a NEW sink terminal owned by the auto-created `LoopTunnel` T, and the new sink wire would show T as its single source — "T is a sink on the source wire and the source of the sink wire"; and (ii) a two-sided consumer gate walking ONE tunnel hop would find the downstream consumer `#12673`.

OBSERVED (`tools/bench/build_d1_m3a1.log`, this run, both writes returned `op_error ''` and `Is Broken? False`):
- Row t1, source wire 9649: its SINK terminals went `[('LoopTunnel',9641),('',0)] -> [('',0)]`. The pre-existing tunnel sink DISAPPEARED and no new LoopTunnel sink ever appeared. After the junk purge, wire 9649 reads sinks `[('SelectorTunnel',9623),('',0)]` and SOURCE `[('LoopTunnel',24035)]`. The new sink wire 24009 has exactly one source terminal of any class: `[('LoopTunnel',24035)]`. So tunnel 24035 is the SOURCE OF BOTH wires.
- Sixth row, source wire 23955: it loses its `RightShiftRegister 23868` sink and gains none; the sink wire 9113 has exactly one source, `LoopTunnel 24018`.
- The consumer gate failed `NEITHER`: it walked `LoopTunnel #24154` (out_wire 24130, in_wires [24226]) and `12673` was absent. The real path is TWO hops: `24226 -> 24154 -> 24130 -> 24018 -> 9113 -> 12673`.
- Node census 632 rows throughout; the seven moved nodes read fully wired (`#10407` 7/7, t1 = w24009, t6 = w24226); the only bare terminals are four shift-register OUTER terminals. And yet `ExecState` = 0, and the save was refused with `RuntimeError: refusing to save a BROKEN VI`.
- Both writes minted a junk `Invoke` node bearing uid 9649 — including the sixth row, whose source net was 23955 and which never addressed wire 9649.

OUR NEW EXPLANATION, which we want attacked:
(1) When `OpConnectFromWire_v0` writes across a loop border, LabVIEW keeps the pre-existing wire uid on the INNER segment and mints the outer segment as a new object, so the tunnel ends up as the SOURCE of both segments. The acceptance test should therefore be: the new sink wire has exactly ONE source terminal, owned by a `LoopTunnel` T (count every source terminal of every class BEFORE filtering), and the value's origin is confirmed by walking OUTWARD from T through however many tunnel hops it takes to reach the intended source terminal.
(2) The consumer gate and that origin test are the SAME N-hop walker, called twice; one-hop walks are what failed here and a sink-side-only `wire_delta` is what failed the cycle before.
(3) The minted `Invoke` node's uid 9649 is a CONSTANT OF THE OP, not a recycled live uid, because it appeared identically on a write that never touched wire 9649. We are retiring the worry that uid-keyed censuses of pre-existing objects are unsafe.
(4) A build stage whose defined end state is a broken VI can never leave a saved file (our Save refuses a broken VI because `SaveInstrument` blocks forever on one), so the stage BOUNDARY must be re-cut to end where the VI is whole, rather than the script being decomposed further.
(5) `ExecState` 0 with only four bare shift-register outer terminals is unexplained; we intend to read it with `Wire.Is Broken?` over every wire rather than infer it again.

ALREADY RULED OUT (do not spend the answer on these): re-tuning the expected `wire_delta` number (the previous review showed it reads the sink side only); a same-named source terminal on a different net (forbidden as a rule-1a value substitution); looking the sixth row's sink up by the string `Q_focusback` (measured: no such terminal name — the terminal is named `"position [internal units]"`).

WHAT WE WANT: the strongest reason each of (1)-(5) is wrong; an alternative explanation for the disappearing sink terminal on wire 9649 in particular; what would falsify (1); and the cheapest discriminating test we could run on this bed. If (1) is a third theory-derived acceptance test dressed as a measurement, say so and say what we should measure instead.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. The single strongest reason the new explanation is wrong

**`OpWireSource_v5(UID 2 = 9649)` was not reading wire 9649 after the write. Your own log says so, in a column the gate never looked at.**

`recip` is `Terminal.Wire` — each terminal's own back-pointer to the wire it belongs to (`tools/recipes/build_opconnectfromwire_v0.py:440`, `recip=int(vi.GetControlValue(lab["recip_wire"]))`).

- **Before** the write, every row of wire 9649 reports `recip=9649` — self-consistent (`tools/bench/build_d1_m3a1.log:1061-1063`).
- **After** the write, immediately: `1 row(s), 0 with a REAL owner` (`:1070-1071`).
- **After the purge**, the "source wire 9649" walk returns three rows, and **every one of them reports `recip=24009`** (`:1096-1098`).
- The "sink wire 24009" walk taken seconds later returns rows that are *identical, field for field* (`:1100-1102`).

So there are not two segments sharing a source tunnel. There is **one wire, 24009, read twice under two names.** "Tunnel 24035 is the SOURCE OF BOTH wires" is the signature of a reader that lost its object, and (1) promotes that artefact into the acceptance test. The A3-ID gate at `:1079` and `:1105` failed *correctly*; rewriting the gate to accept the observation is the wrong direction of fit.

Secondary, and independently fatal to (1)'s stated mechanism: **the sixth row minted no new sink wire at all.** `connect_from_wire(wire=23955, …)` returned `UID 2: 9113` (`:1147`), and 9113 is a **pre-existing** uid — it was already on the bed before the write, carrying two sinks (`RightShiftRegister 4256`, `SelectorTunnel 12673`) and **no source** (`:1129-1131`). After the write it has the same uid, the same two sinks, `recip=9113` throughout, plus a new source terminal `LoopTunnel 24018` (`:1151-1155`). Nothing was "minted as the outer segment"; a sourceless wire acquired a source. The t1 row differed only because `#10407 t1` carried wire 0 (`:1065`), so a wire had to be created there. (1) generalises from one of two rows and contradicts the other.

## 2. Alternative explanations of the same evidence — including the disappearing sink on 9649

**A. The reader returns a null on an unresolvable uid, and the wire was simply consumed.** `1 row(s), 0 with a REAL owner` appears twice: for 9649 right after its write (`:1071`) and for 23955 right after *its* write (`:1150`). Wire 23955's "loss" is not "it lost the `RightShiftRegister 23868` sink and gained none" — it lost **its own source too** (`SelectorTunnel 2017`, `:1142`) and every other terminal (`:1156`, `[('',0)]`, source terminals `[]`). A wire with zero terminals is not a wire in a 632-node VI that still compiles the same way it did a second earlier. One signature, two rows, one cause: **the uid stopped resolving.** That is the whole of the "disappearing sink terminal", with no LabVIEW segment-naming policy required.

**B. The reader echoes a stale answer.** The post-purge read of "9649" is byte-identical to the preceding read of 24009. Note the call order: `9649 after write` → `24009 after write` → purge → `9649 after purge` → `24009 after purge`. The fourth answer equals the second. This project has already been bitten by exactly this failure mode — `add_shift_reg` "ran, returned a uid and a clean error, and CREATED NOTHING" until `ensure_loaded` was forced (`tools/gscript.py:704-708`), and STATUS still lists nine verbs that never reach `ensure_loaded` and "can decline in the same silence". A and B are not distinguished by anything in this run; test 2 below separates them for one call.

**C. Deferred edit.** The read at `:1070` is 0.34 s after the write; the read at `:1096` is after a 1.27 s purge (`:1091`). The object graph may simply not be settled at the first read. Also not distinguished by this run.

None of A, B or C needs "LabVIEW keeps the uid on the inner segment". (1) is the only explanation on the table that requires a new belief about LabVIEW.

## 3. What would falsify (1) — and what already has

(1) asserts *the pre-existing wire uid is kept on the inner segment*. Two observations already on file contradict it:

- **Immediately after the t1 write, uid 9649 belonged to an `Invoke` node**, not to any wire: 6 terminals, `reference` / `Method` / `error in`, all `errs=[…,1055]`, at position (4593, 2718) (`:1081-1089`). A uid cannot be "kept on the inner segment" while naming a node.
- **The sixth row's inner wire is 9113, a uid older than the write** (`:1129`, `:1147`). No minting, no uid transfer.

The clean falsifier for the remaining ambiguity is **test 3** below: read the outer segment's uid from a terminal that was never recycled. If `FlatSequenceInnerTunnel 9655` now carries wire 9649, the uid survived on the **outer** segment — (1) is wrong about which segment and the "source of both" reading is a reader fault. If it carries 24009, one wire crosses the border and the two-segment model is moot. If it carries a third uid, 9649 was destroyed and (3) dies with it.

## 4. Claim (3) is refuted by the log that was cited to support it

**The junk `Invoke` node's uid is not a constant.** In this one run it is `23522` (`:44`, `:68`, `:92`, `:116`, `:140`), then `23786` (`:164` onward, eight consecutive create/purge cycles), then `9649` (`:1081`), then `9649` again (`:1160`) — **at a different position, (2639, 933) versus (4593, 2718)**, so it is not even the same node. The run's own measurement line says it: `MINTED UID == THE LIVE SOURCE NET 23955 : False` (`:1173`).

Read in order, this is a textbook uid allocator: the same freed uid (23786) is handed back eight times in a row, and the only time a *low* uid appears is immediately after a low uid was freed — the t1 write consumed wire 9649, the junk node took 9649, the purge freed it again, and the sixth row's junk node took it again. **The sixth row minting 9649 is the strongest evidence FOR recycling, not against it.** The inference in (3) runs backwards.

NI documents the behaviour: *"If you delete an object, LabVIEW might assign the UID for that deleted object to a different object in the future… check the Class Name property or Control class/Label property of the object in addition to the UID."* ([LabVIEW Wiki, GObject class/UID property](https://labviewwiki.org/wiki/GObject_class/UID_property)) That is precisely the identity check this fleet does not perform. Retiring the uid-safety worry is the single most expensive thing in this brief — and note that `#10407 t6`'s own net changed uid (23955 → 24226) as a side effect of a write whose sink was `#12589 t1`, so uid churn is not confined to the addressed objects.

## 5. Claim (4) is false by this project's own code — and it collides with a standing user rule

`gscript.save(target, allow_broken=True)` diverts a broken VI to `gui_save()` (`tools/gscript.py:2087-2089`), whose docstring reads: *"COM `SaveInstrument` blocks forever on a VI whose ExecState is 0, **but the editor's own File > Save handles one fine** (the file shrinks, because a broken VI carries no compiled code — benign, the diagram is intact)"* (`:1998-2011`). `tools/recipes/build_d1_routeb_v7.py:311` already uses `allow_broken=True` for exactly this case. The `RuntimeError` in the log is **your own guard's default**, not LabVIEW's refusal. The recipe called `save()` without the flag.

So the premise "a build stage whose defined end state is a broken VI can never leave a saved file" is wrong, and the conclusion drawn from it — re-cut the boundary rather than decompose — inherits nothing but the error. Worse, the prescription is unreachable for this stage by construction: `ExecState` was already 0 after the **first node move** (`:653-654`), and the two shift registers are wired in M3a-2 by design (`:367`, `tools/gscript.py:683-687`). "End where the VI is whole" therefore means merging M3a-1 and M3a-2 into one larger stage — the exact opposite of the rule this cycle exists to obey (*"A step is not done until it has left a file… The user must always have something to open"*, CLAUDE.md, 2026-09-19). Sixteen `no intermediate file is written at this boundary` lines in one run is the violation; `allow_broken=True` is the fix that was already built and not called.

## 6. Claim (5): `ExecState` 0 is over-explained, and `Wire.Is Broken?` cannot see any of it

Three recorded causes, none of them mysterious:

- `ExecState` went 0 at step **02**, after the first node move — before any shift register existed and before any border write (`:653-654`). Moving a node across a structure border severs its wires.
- Both new registers come back **untyped with both sides unwired**, which the toolkit documents as breaking the VI *by design*: *"an unwired register breaks the VI (ExecState 0) until they are wired — that is correct, not a failure"* (`tools/gscript.py:683-687`, echoed at `:367`).
- The bare terminals are named in the census: `BARE node #23868 'VISA SR right outer' … state=BARE (WireUID 0)` (`:541`).

`Wire.Is Broken?` reports **wire** state only; "a required block diagram terminal is unwired" is a separate broken-VI class that never produces a broken wire ([NI Community, *Unwired or bad terminal*](https://forums.ni.com/t5/LabVIEW/Unwired-or-bad-terminal/td-p/2772804); [LabVIEW Wiki, *Wire class/Is Broken?*](https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property)). It already returned `False` for the one wire you wrote (`:1068`). A sweep over every wire is *predicted to return zero broken wires and explain nothing* — a build spent confirming the instrument cannot see the fault. If a reason-for-break reader is still wanted, it is the Error List, and `VI.Get Errors` (452) is already established as absent from the exported ActiveX interface.

## 7. Claim (2): right direction, wrong end of the wire

An unbounded outward walk has no failure mode, which is how the previous gate died (`wire_delta == 3`, withdrawn at `:1106`). A walk that accepts "however many hops it takes" will also succeed through a chain that passes somewhere unintended.

And A4 does not need a walker at all. The consumer-side read is already in the log: `#12673` is a sink of wire 9113, whose single source is `LoopTunnel 24018` (`:1151-1155`). **Anchor the gate at the consumer, zero hops.** Provenance still needs an outward walk, but then: follow only *unique* source terminals (fail, never search, on ambiguity), terminate at the first non-tunnel terminal, and assert that terminal's `(owner uid, name)` equals a value **predicted before the run**. Hop count becomes an output, not a criterion.

## 8. Yes — (1) is a third theory-derived acceptance test dressed as a measurement

The receipts are in one run: `A3 wire_delta 1 (expect 3)` fails (`:488`) → A3 is withdrawn as an acceptance test (`:1106`) → `A3-ID` (Pre-decided 70) fails twice in the same run (`:1079`, `:1105`) → (1) proposes a third rule, written after seeing the third result, each one looser than the last. Three gates in three cycles, every one authored after the observation it had to accommodate.

**Measure this instead.** The only invariant rule 1a cares about is *the sink receives the value produced by the intended source terminal.* Everything in (1) — how many wire objects were minted, which uid was kept, whether a tunnel appears on one list or two — is implementation detail that should never have been promoted to a gate. Add one thing that is not a topology theory: **an identity precondition on the reader itself** — `recip == queried_uid` on every `OpWireSource_v5` row, plus the class check NI's own UID guidance asks for. That precondition fails on `:1096-1098`, which means this cycle's central observation would never have been believed.

## 9. The cheapest discriminating test

**One op call, no mutation, no build: query a uid that cannot resolve** — the just-purged junk uid, or `2147483647` — and read what `OpWireSource_v5` returns.

- Returns `1 row(s), 0 with a REAL owner` → that signature means *"uid did not resolve"*. Both "disappearing sink" observations (`:1071` for 9649, `:1150` for 23955) are reader nulls, explanation A holds, and (1), (3) and the disappearing-sink puzzle all collapse together.
- Returns the previous call's answer → explanation B, the reader echoes stale state, and **every identity conclusion in this cycle is void**, including the ones that passed.
- Returns a clean error → the reader is sound, and the two null reads are real LabVIEW state, which makes explanation C (deferred edit) the live one; separate it by re-reading the same uid twice, one second apart, with no edit in between.

Two follow-ups, one read each, both on the existing bed: **(i)** read the wire carried by `FlatSequenceInnerTunnel 9655` (t1) and `SelectorTunnel 2017` (t6) — the source terminals whose uids were never freed, so they cannot be recycled — which yields the outer segment's true uid and falsifies or confirms (1) outright; **(ii)** read the POS right shift register's inside terminal (the reader used at `:537`/`:1016`) to see whether it carries the new net 24226, which would show the sixth row lost nothing at all and that `:1156` is entirely a reader artefact.

**Free, before any of that:** re-read `:1096-1098` against `:1100-1102`. Pre-decided 71 is already answered on file, in the negative, and it cost nothing to find.

**What would change my mind:** test (i) returning wire uid 9649 from terminal 9655 — an un-recycled route showing the old uid alive on a real wire — plus a non-null, non-echoing answer to the unresolvable-uid probe. That combination would make "the uid survived a border split" a real observation rather than a reading error, and I would then argue only about *which* segment it survived on.

Sources: [LabVIEW Wiki — GObject class/UID property](https://labviewwiki.org/wiki/GObject_class/UID_property) · [LabVIEW Wiki — Wire class/Is Broken? property](https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property) · [NI Community — Unwired or bad terminal](https://forums.ni.com/t5/LabVIEW/Unwired-or-bad-terminal/td-p/2772804) · [NI — Save:Instrument method](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/saveinstrument.html)

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN FULL by the judgement session (cycle 56 close, 2026-09-21).** All five points stand; four of this
cycle's own conclusions are withdrawn on the strength of them. One line per point, with the citation each was won
with:

1. **ACCEPTED — the "tunnel 24035 sources both wires" observation is a READER ARTEFACT, not a topology fact.**
   Both the 9649 walk and the 24009 walk carry `recip=24009` on the post-purge read
   (`tools/bench/build_d1_m3a1.log:1096-1098` vs `:1100-1102`), so one wire was read twice under two names —
   which means **A3-ID failed CORRECTLY**, not spuriously. Pre-decided 78 (the re-derived border acceptance test)
   is **WITHDRAWN**; it is replaced by `docs/cycle27-plan.md` Pre-decided 84 (the withdrawal) + 85 (the rule-1a
   invariant plus an identity precondition `recip == queried_uid` on every `OpWireSource_v5` row).
2. **ACCEPTED — A4 anchors at the CONSUMER and needs ZERO hops.** `#12673` is already a sink of wire 9113 whose
   single source is `LoopTunnel 24018` (`:1151-1155`), so no outward walk is written; an unbounded walk has no
   failure mode, which is exactly how `wire_delta == 3` died (`:1106`). Hop count becomes an OUTPUT, never a
   criterion. Recorded as `docs/cycle27-plan.md` Pre-decided 90 (amending 79).
3. **ACCEPTED — the minted uid is NOT a constant of the op, so the uid-safety question is RE-OPENED, not
   retired.** The minted values across this project's calls are 23522 / 23786×8 / 9649 / 9649 again at a different
   position, and `:1173` reads `MINTED UID == THE LIVE SOURCE NET 23955 : False` — a uid allocator recycling freed
   uids, not a fixed signature. Pre-decided 80 is **WITHDRAWN** (replaced by Pre-decided 87); **Pre-decided 71 is
   NOT retired.**
4. **ACCEPTED, and it is this cycle's most valuable finding — the broken-VI save already has a route, so the
   stage CAN leave a file.** `gscript.save(target, allow_broken=True)` exists and diverts a VI at `ExecState` 0 to
   `gui_save()` (`tools/gscript.py:2087-2089`; already used by `tools/recipes/build_d1_routeb_v7.py:2276`,
   documented at `:311`). The `RuntimeError: refusing to save a BROKEN VI` that ended two cycles was our own
   guard's DEFAULT, not a LabVIEW boundary — so **no boundary is re-cut** and the 2026-09-19 "a step is not done
   until it has left a file" rule is satisfied by one flag. Pre-decided 81 is **WITHDRAWN**, replaced by
   Pre-decided 88.
5. **ACCEPTED — `Wire.Is Broken?` reports WIRE state only and cannot see an unwired required terminal**, so the
   proposed broken-wire sweep is predicted to return nothing and explain nothing; and `ExecState` 0 has been the
   **expected** state since the first node move at `:653-654` (an untyped, both-sides-unwired shift register breaks
   the VI by design, `tools/gscript.py:683-687`). Pre-decided 82 is **WITHDRAWN**, replaced by Pre-decided 89.

**The named cheapest discriminating test is ADOPTED as the NEXT CYCLE'S FIRST ACT** (`## 9` above): one
`OpWireSource_v5` query on an unresolvable uid — the just-purged junk uid and `2147483647` — plus one live uid read
twice 1 s apart with no edit between. No mutation, no build, gates on HYGIENE only. Written into
`docs/cycle27-plan.md` Pre-decided 86 and into STATUS.md `## NEXT`. Its three outcomes are pre-assigned to three
different cycles, including the branch in which **every identity conclusion of the last three cycles is VOID**.

Cost: claude `-Role hypothesis`, opus / effort max, ANSWERED, **$3.57**. It also discharges `guard_peer` for
`tools/bench/build_d1_m3a1.log` (`BGRUN END rc=1`) — do not buy a second review for that log.
