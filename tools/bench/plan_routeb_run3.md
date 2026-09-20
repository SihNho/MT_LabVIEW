# Route B run 3 — implementing the two judgement decisions, and nothing else

Changed file: `tools/recipes/build_d1_routeb_v0.py` (edited 2026-09-17 17:06, not yet run).
New diagnostic: `tools/bench/diag_sr_transport.py` (read-only, not yet run).
Prior state: run 2 = 84 pass / 2 fail, ledger **63 WIRED / 0 FAILED / 3 NO-ROUTE**
(`tools/bench/build_d1_routeb_v0_run2.log:408`), `ExecState 0`, nothing saved.

## What the judgement session decided (session brief, 2026-09-17), and what I am building

**(1) `#1359` t1 and `#29874` t3 get two lock-stepped queues `Q_sr1` / `Q_sr2`** — enqueued in loop 1.1 each
iteration with the frame, dequeued in 1.2 in the same iteration as `Q_work` (`docs/stage2-assembly-step-c.md`'s
paired producer/consumer shape, 162/162 in replay). Their source is a `LeftShiftRegister` of `#637` that STAYS
on 1.1 while both sinks move into 1.2, so a direct wire between two sibling loops is illegal.
MEASURED basis: `tools/bench/d1_tunnel_sources.json` — the source terminal of `w9097` / `w28039` is owned by
`LeftShiftRegister` **#9025** / **#29512**, "neither a node on diagrams (19, 43, 0) nor a LoopTunnel".

Implementation, per row (`build_d1_routeb_v0.py`, function `sr_queue` inside `s3w`):
* `Obtain` on `Diagram #686` (outside both loops), element TYPE from a NAMED node output;
* `Enqueue` inside 1.1's body (`Diagram #639`), tunnel auto-created (`docs/NAMES.md:762`);
* the enqueue's `element` **branched off the LEFT register's own inside wire** with `OpConnectFromWire_v0`;
* `Dequeue` inside 1.2's body; its `element` → the sink by INDEX with `OpConnectNested_v1`;
* `Release` outside both loops.

**RULE 1a, the part I think is the crux:** what `#1359` t1 consumed is the LEFT register's OUTPUT — the PREVIOUS
iteration's value. Enqueueing from the node that WRITES the partner RIGHT register would advance the value by one
iteration while every structural gate stayed green. So that node is used ONLY as the queue's TYPE source (a type
carries no value) and the VALUE is branched off the left register's own wire.

**(2) `#2222` t0 ← control `Z/dZ` (uid 47), UNNAMED sink** (`from_ctl_unnamed`): `wire_control` is name-addressed
on both ends. Use the control's OWN wire if it has one on this copy (measured per run); otherwise create a
TEMPORARY named sink (a bare `Equal?` via `OpCreateEqual_v0`, 23/0), `wire_control` into its `x`, branch off that
wire by index with `OpConnectFromWire_v0`, delete the temporary, and RE-READ the sink.

## The facts the build does not have, and how it gets them

`queue_node('obtain', …)` takes the element TYPE from a NAMED OUTPUT TERMINAL of an existing node
(`tools/gscript.py:1068-1074`), and `STATUS.md`'s NEXT says route B §2b "never says which terminal each of the 8
queues takes". `tools/bench/diag_sr_transport.py` measures it read-only on a pristine copy in the same runner
(P1–P6: the two registers and their partners, the single source terminal of each partner's inside wire, its
NAME and Traverse class/index, `Z/dZ`'s net, `#2222` t0's state) and writes `tools/bench/sr_transport.json`,
which `sr_queue` reads. Nothing is cached across the two: every address is re-read live at wiring time and the
run REFUSES the row if the register index drifted.

## Stated in advance: this CANNOT reach `ExecState 1`

`s1q` (the 8 queues) and `s4b` (the three sentinel `Equal?`s) are both still SKIPPED — the element types of the
other six queues are an undesigned row and the sentinels depend on them — so 1.2 / 1.5 / 1.7 keep UNWIRED
conditional terminals, which is a broken VI by construction. Run 3's target is the LEDGER gate (**0 FAILED,
0 NO-ROUTE**) plus the new gate "both SR queues built", not the save.

## Also in this run (bug found while editing, not a new feature)

`s3w`'s RETARGET name check appended `(tag, …)` before `tag` was assigned — a latent `NameError` run 2 never
reached because no row mismatched. `tag` moved above the block.

## The questions I want attacked

1. Has this cross-loop transport already been built, measured or REFUTED in our own files under another name?
2. Is branching the enqueue's `element` off the LEFT register's inside wire actually value-preserving, or is
   there an ordering hazard (the enqueue and the register's writer race within the same iteration)?
3. Does a `queue_node('obtain', …)` typed from the partner-writer's output give the SAME type the register
   carries, or could a coercion make it merely compatible?
4. Is a bare `Equal?` with no source wiring something `OpCreateEqual_v0` can create at all, and is deleting a
   temporary sink safe when the branch and the temporary's segment belong to ONE net?
5. What existing helper already does any of this, so the new code is redundant?
