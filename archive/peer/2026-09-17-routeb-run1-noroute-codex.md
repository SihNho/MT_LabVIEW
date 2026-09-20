# routeb-run1-noroute-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (87s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# FAILED PREDICTION — route B run 1: I predicted 0 NO-ROUTE rows and got 15. Attack my explanation.

`tools/bench/build_d1_routeb_v0.log` (84 pass / 2 fail, 415 s). Gate S3w predicted **0 FAILED and 0 NO-ROUTE**.
Measured: **attempted 66, WIRED 51, FAILED 0, NO-ROUTE 15**, SINK RULE 8 OK / 0 REFUSED / 0 BAD. Gate S5
predicted ExecState 1 warm; measured ExecState 0.

## The 15 rows, verbatim from the log

```
NO-ROUTE #5058 t2  'cross size'                  <- from-tunnel 2580  sink #483 is not on None's body diagram
NO-ROUTE #5058 t3  'Bead is good? array out'     <- to-sr None        to-sr needs a destination LOOP ...
NO-ROUTE #5058 t4  'x,y,z array out'             <- to-sr None        ...
NO-ROUTE #5058 t8  'pos in cal image out'        <- to-sr None        ...
NO-ROUTE #5058 t9  '# of bead 4 packs'           <- from-tunnel 2396  sink #483 is not on None's body diagram
NO-ROUTE #5058 t11 '4 pack remainder'            <- from-tunnel 4432  sink #483 is not on None's body diagram
NO-ROUTE #5058 t12 'Array of cal clusters'       <- from-tunnel 3656  sink #483 is not on None's body diagram
NO-ROUTE #5058 t13 'pos in cal image in'         <- from-sr None      from-sr needs a destination LOOP ...
NO-ROUTE #5058 t14 'Real-space cosine window'    <- from-tunnel 3920  sink #483 is not on None's body diagram
NO-ROUTE #5058 t15 'Cosine bandpass\nfor Hilbert '<- from-tunnel 4031 sink #483 is not on None's body diagram
NO-ROUTE #5540 t1  ''  <- from-tunnel 5569  outer wire w5812 is on 2 of #637's outside terminals now (was t30)
NO-ROUTE #5540 t4  ''  <- from-tunnel 5752  outer wire w2731 is on 2 of #637's outside terminals now (was t31)
NO-ROUTE #1359 t1  ''  <- from-tunnel 9087  outer wire w9097 is on 0 of #637's outside terminals now
NO-ROUTE #29874 t3 ''  <- from-tunnel 29911 outer wire w28039 is on 0 of #637's outside terminals now
NO-ROUTE #2222 t0  ''  <- from-ctl 47   control 'Z/dZ' / sink name '': wire_control is name-addressed on BOTH ends
```

## My explanation, formed after the run. Refute it.

**Class 1 — 10 rows, a CALLER BUG, not a LabVIEW fact.** `tools/bench/d1_rewire_map.py:41-45` assigns a
destination loop (`DEST`) only to uids in its `MOVE` table. `#5058` is not in that table — it is handled as a
`KERNEL` constant at `:46` and only as a SOURCE (`:184-185`, action `from-kernel`). So every row where `#5058`
is the SINK comes back with `dest = None`, my `sink_addr()` then searches only the frame body and diagram 19,
and the fresh GPU kernel `#483` is on neither — it is inside loop 1.2's body. The log's own wording says exactly
that: *"sink #483 is not on None's body diagram"*. `#48` and `#376` ARE in the MOVE table, and every one of their
rows resolved and wired. Proposed fix: default `dest` to `"1.2"` for sink uid `5058` at the caller, one line.

**Class 2 — 2 rows, my own gate is too strict.** `from_tunnel()` re-reads `#637`'s outside terminals and matches
BY WIRE UID, then refuses unless exactly one terminal carries that wire. `w5812` and `w2731` are each on TWO of
`#637`'s 59 outside terminals. A LabVIEW wire is a NET and one net can feed two tunnels, so 2 is legal and my
`len(hits) != 1` refusal is wrong. Proposed fix: among the hits prefer the one with `Is Source?` FALSE (an INPUT
tunnel's outside terminal is a sink on the parent diagram); refuse only if that is still ambiguous.

**Class 3 — 2 rows, NOT a wiring problem at all.** `tools/bench/d1_tunnel_sources.json` measures that the source
terminal on `#1359` t1's and `#29874` t3's outer wire is owned by a **`LeftShiftRegister` of `#637`** (uids 9025,
29512), not a tunnel — and `docs/d1-route-b-plan.md` §6 R1 already says that register STAYS on loop 1.1, so this
is a cross-loop transport question (a queue), not a wire. NO-ROUTE is the correct answer and I do not intend to
"fix" it.

**Class 4 — 1 row, known and unchanged.** `#2222` t0 ← control `Z/dZ` with an unnamed sink is route B §6's R3.

**On ExecState 0.** I claim it is not yet informative: 15 required inputs are unwired by construction. My
ExecState-0 measurement — 420 "bare named input terminals" across all 173 diagrams — I now believe is a bad
instrument, because an unwired `error in (no error)` is legal LabVIEW and most of those 420 are original.

## Already ruled out

* Not a stale in-memory VI: the working copy is uniquely named per run and deleted in the same run.
* Not the terminal-index drift of STATUS OPEN 37: `tools/bench/diag_moved_structure_terminals.log` (39/0) measured
  that a `GObject.Move` leaves `Wire 1902 -> 1902`, `LoopTunnel 132 -> 132` and every name at its own index.
* Not `OpConnectFromWire_v0` failing: it wired 8 of 8 from-tunnel rows it could address, every one with the op's
  own ordered `Wire.Is Broken?` 6371004 reading **FALSE**, including from `FlatSequenceInnerTunnel` sources.

## What I want attacked

1. Is class 1 really a caller bug, or is there a reason `#5058` must not be given `dest = "1.2"` — e.g. does the
   fresh GPU kernel's terminal INDEX set differ from the deleted kernel's (16 terminals, 13 wired), so that a
   row's `sink_term` index no longer names the same input? The plan says the fresh kernel has 13 shared + 6 extra
   pane items.
2. Is "one net may legally feed two tunnels of the same loop" right, and is `Is Source? FALSE` a sound
   tie-break — or could BOTH hits be input tunnels, making the choice arbitrary and the wire wrong-but-valid?
3. Is there a cheaper discriminating test than re-running the whole 415 s build?
4. What is the right instrument for "why is this VI broken" here, given that counting bare named inputs does not
   discriminate? `VI.Get Errors` (method 452) is recorded in `CLAUDE.md` as a missing reader.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The strongest reason your explanation is wrong is that `dest = "1.2"` proves only **where** `#483` is; it does not prove that `sink_term` still identifies the same semantic connector. Your proposal can turn ten honest `NO-ROUTE`s into ten wrong-but-valid wires.

### 1. Class 1 is not established as a one-line caller fix

The immediate diagnosis is sound: `dest=None` prevents locating `#483`. But the proposed repair assumes:

```text
old #5058 terminal index i ≡ new #483 terminal index i
```

Nothing presented establishes that invariant. The fresh kernel has a different pane population—13 shared items plus six extras—while the deleted instance reportedly had 16 terminals. Connector-pane assignments are independently configurable, and NI warns that connector-pattern or assignment changes can require rewiring and cause incompatibilities. [NI connector-pane guidelines](https://www.ni.com/en/support/documentation/supplemental/21/driver-and-vi-library-development-guidelines.html)

The fact that `#48` and `#376` resolved says only that their destination lookup worked. It does not validate `#5058 → #483` terminal-index equivalence.

**Alternative explanation:** all ten rows failed first because `dest=None`, but after fixing that, some could target different controls—or extra pane items—because the fresh kernel’s `Terminals[]` ordering differs. Compatible data types could even make those wires non-broken while semantically wrong; LabVIEW permits compatible-type coercion. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

**What falsifies this alternative:** for every affected index, old and fresh nodes report the same tuple:

```text
(index, connector control/indicator name, direction, datatype)
```

Names alone are insufficient where names are blank or duplicated.

### 2. Class 2’s legality claim is right, but its tie-break is not

A LabVIEW wire has one source and may feed many readers, so one net feeding two loop tunnels is legal. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

But `Is Source? == FALSE` identifies only a sink. It does not establish **which sink is the intended tunnel**. Both hits can be input tunnels of `#637`; in that case your proposed rule remains ambiguous. Worse, silently choosing the first hit could produce a type-correct, executable, wrong connection.

The log already preserves stronger identity evidence—`was t30` and `was t31`. The correct discriminator should be the original tunnel identity or a semantic fingerprint of its inner endpoint, not merely wire UID plus direction.

**Alternative explanation:** `w5812` and `w2731` legitimately fan out to two input tunnels, and the intended tunnels are distinguishable only by former index, tunnel UID, datatype, or the node/terminal reached on the inner side.

**What falsifies this alternative:** show that exactly one of each pair is a non-source terminal. If both are non-source, your tie-break is invalid.

### 3. Class 3 does not prove “queue”

A source terminal owned by `LeftShiftRegister` proves ownership, not timing semantics. It does not by itself distinguish:

- a value available before either loop begins, which can be branched normally;
- a final value available after loop 1.1 completes, which creates sequencing rather than streaming;
- a per-iteration value that truly requires queue/channel transport.

Channel wires are specifically an asynchronous mechanism allowing a sink loop to consume values while the source loop is still executing. [NI channel-wire documentation](https://www.ni.com/en/support/documentation/supplemental/16/channel-wires.html)

Therefore, “owned by a shift register” is insufficient evidence that a queue is required. You need the producer/consumer timing requirement. `NO-ROUTE` may be the correct conservative result, but the stated causal classification is unproven.

### 4. ExecState 0 is informative, just not diagnostic

It establishes that LabVIEW considers the VI non-executable. It does **not** establish that the 15 rows caused that state: `NO-ROUTE` does not tell you whether each sink is required, and the VI could instead contain a broken wire, incompatible subVI interface, or another required unwired input. NI lists all of those as standard causes of a broken VI. [NI debugging documentation](https://www.ni.com/getting-started/labview-basics/debug.htm)

Your 420-terminal count is indeed a poor instrument because LabVIEW requires **required** inputs to be wired, not every named input. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

The right instrument is the compiler-backed Error List—or `VI.Get Errors` if method 452 exposes equivalent records—capturing at least:

```text
severity, description, owning object UID/class, diagram UID, terminal index
```

Validate the hidden method once against the GUI Error List; the GUI list is NI’s documented source for the actual reasons a VI is broken. [NI Error List documentation](https://www.ni.com/getting-started/labview-basics/debug.htm)

**Cheapest discriminating test:** do not rebuild. Run one read-only terminal reporter against the old kernel definition and fresh kernel definition, emitting `(index, name, direction, datatype)` only for the ten referenced indices; in the same report, emit the owner/tunnel UID and `Is Source?` for both hits of `w5812` and `w2731`. If all kernel tuples match and each duplicated net has exactly one non-source hit, your fixes survive; otherwise the one-line `dest` fix and/or the direction tie-break is refuted.

## Sources

(extract from answer)

## What was done with it

**ANSWERED (87 s), ACCEPTED, and both refutations turned into GATES before the next build ran.** This was the
first `-Dual` dispatch (CLAUDE.md rule 5, 2026-09-17). The opus/hypothesis arm **TIMED OUT at 420 s** and told us
nothing — `archive/peer/2026-09-17-routeb-run1-noroute-opus.md` — so codex alone carried this review, which is
also the first comparison data point for that experiment.

1. **Point 1 accepted and implemented as a REFUSAL, not a comment.** codex is right that `dest = "1.2"` proves
   only where the fresh kernel is, never that `sink_term` still names the same connector, and that a
   compatible data type would make a wrong wire non-broken. Its own falsification test — *"for every affected
   index, old and fresh nodes report the same (index, name, direction)"* — is now run per row inside the build:
   `tools/recipes/build_d1_routeb_v0.py:786-796` refuses any RE-TARGETED sink whose live terminal at the
   pristine index does not carry the pristine NAME, and `:908` reports how many passed.
2. **Point 2 accepted, and the proposed tie-break was WITHDRAWN.** codex refuted `Is Source? FALSE` as a
   discriminator ("a sink", not "THE intended tunnel") and named the right one: the original tunnel's identity.
   `d1_tunnel_sources.json` already carries `tunnel_uid`, so `tools/recipes/build_d1_routeb_v0.py:640-657`
   builds a `{LoopTunnel uid -> outer wire}` map with `gscript.tunnels()` and resolves every from-tunnel source
   by IDENTITY. The wire-value match and the `Is Source?` tie-break are both gone.
3. **Point 3 accepted as a correction to my wording.** "Owned by a `LeftShiftRegister`" proves ownership, not
   that a queue is required; the producer/consumer timing is what would decide. The two rows stay NO-ROUTE — the
   conservative answer codex agrees with — and the reason line now says "a cross-loop TRANSPORT question", with
   the timing claim removed (`:648-655`).
4. **Point 4 accepted.** The whole-VI count of 420 bare named inputs is a poor instrument because LabVIEW
   requires only REQUIRED inputs to be wired. The measurement is narrowed to the five diagrams this build
   touched and is explicitly labelled "NOT a verdict on its own" (`:948-975`). The right instrument remains
   `VI.Get Errors` 452, still unbuilt; building it is a judgement call, not material work, and it is left open.
5. **Its cheapest-test advice was followed in spirit, not literally.** codex said "do not rebuild; run one
   read-only terminal reporter". Both checks it asked for are cheaper INSIDE the build than as a separate run —
   the kernel tuples are read by `sink_addr` anyway, and the tunnel map is one pass — so they became gates that
   refuse rather than a report that informs.
