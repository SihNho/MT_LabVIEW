# routeb-run1-noroute-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** TIMEOUT (420s)
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

(no answer within 420s — job stopped)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
