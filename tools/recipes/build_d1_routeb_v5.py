r"""ROUTE B — build D1 by dropping the three subVIs FRESH inside a copy, moving only what has no creator.

`docs/d1-route-b-plan.md` written as one long script. Route A is CLOSED (`docs/d1-build-plan.md` §11t); this is
B's first BUILD, and it is the first run in this project that has an answer for all four addressing shapes at once.

PRIOR ART — checked before a line was written; everything below is REUSED, not rebuilt
--------------------------------------------------------------------------------------
`docs/toolkit-capabilities.md`, `grep "^def " tools/gscript.py` (97 functions) and `ls tools/recipes tools/bench`
say every mechanism this build needs already exists. NO NEW OP VI IS CREATED HERE. Specifically reused:

* `tools/recipes/build_d1_v0.py` — `move_in` (:318), `owner_of` (:338), `diag_index` (:357), `wmap`/`terms_of`
  (:364,:375), `sr_census` (:383), `bare_named_sinks` (:482), `TIFF_DELETE` (:474), `loop_end_ref` (:820),
  `class_index` (:946), `SHIFT_REGS` (:282), `QUEUES`/`SENTINELS` (:264,:272). Imported, never re-typed.
* `tools/bench/d1_rewire_map.py` — the OFFLINE resolver, 109/109 on route A's cut list. B feeds it the SAME
  shape of cut list, so the classification (`same-loop` · `from-kernel` · `from-const` · `from-ctl` · `from-sr` ·
  `to-sr` · `from-tunnel` · `source-side`) is unchanged and comparable run to run.
* `gscript`: `loop_in('while')` (:1101), `drop_subvi` (:1171), `queue_node` (:1068), `add_shift_reg`/`wire_sr`
  (:619,:659), `wire`/`wire_control` (:1284,:1871), `node_terms` (:816), `node_labels` (:533), `panel_wiring`
  (:772), `exit_while` (:1029), `remove_bad_wires_scripted` (:2418), `set_index_mode` (:1798).
* the four writers, all BUILT and SAVED: `OpConnectNested_v1` (cross-diagram by index, cold 7/0),
  `OpCreateConstOnTerm_v0` (22/0), `OpStopFromNode_v0` + `OpCreateEqual_v0` (23/0),
  **`OpConnectFromWire_v0`** (`tools/recipes/build_opconnectfromwire_v0.py`, run 2 42/1) — the writer whose
  `Wire Source` is a WIRE-terminal reference, which is the only thing R1's 16 rows ever needed.

WHAT IS NEW HERE, and it is a CALLER technique rather than an op
----------------------------------------------------------------
1. **A `ControlTerminal` uid resolver — `probe_move_ctlterm_v0`'s BY-EFFECT route, run on a THROWAWAY copy.**
   ⚠️ REWRITTEN 2026-09-17 after `archive/peer/2026-09-17-priorart-priorart-routeb-build.md` A3/A1/A4/B1. My
   first route was `panel_wiring(label) -> wire` then `OpWireSource_v5(wire) -> the source terminal's owner`,
   gated on `owner_class == 'ControlTerminal'`. **That gate can never fire.** `OpWireSource_v5` reads
   `Generic.Owner` **6327806** (`docs/toolkit-capabilities.md:48`), and a ControlTerminal's Owner is its
   **DIAGRAM** — measured on this very object: `tools/bench/probe_move_ctlterm_v0.log:47`
   `OBSERVED uid 642 -> owner 'Diagram' uid 639 | self 'ControlTerminal'#642`. `docs/d1-build-plan.md:787-788`
   said so in advance and named the property a real reader would need, `ControlTerminal.Control` **6353000**,
   which `docs/vi-server-ids.json:145` marks **UNVERIFIED** and nothing builds. A new op is not authorised here.
   So the resolver is the one that IS built and measured 9/0 — identification **by effect**
   (`tools/recipes/probe_move_ctlterm_v0.py:327-351`, `tools/bench/probe_move_ctlterm_v0.log:134`, which named
   control uid 7 `stop (end)` as `ControlTerminal #642` in 14 s): move a candidate, read `panel_wiring`, and the
   label whose connected wire changed is that terminal's. Because a move CUTS the wire and moving back does not
   restore it, the search runs on a **separate throwaway copy** and only the resulting `label -> uid` map is
   carried into the build. The candidate set is not re-derived: `tools/bench/ctlterm_owners.json` (recorded at
   this same md5) already lists the **31** ControlTerminals owned by `Diagram #639` (`docs/d1-build-plan.md:220`).
2. **THE SINK RULE, applied mechanically, per row** (`docs/d1-route-b-plan.md` frontmatter `decided_2026_09_17`,
   judgement): a from-tunnel row's sink is ALWAYS a terminal with `Is Source?` FALSE. Every from-tunnel write is
   preceded by a read of that very terminal and REFUSED unless it reads `is_source == False` and `wire == 0`, and
   followed by the op's own ORDERED `Wire.Is Broken?` 6371004.
   ⚠️ **What that gate does and does not prove, MEASURED 2026-09-17** (`tools/bench/
   diag_moved_structure_terminals.log`, 39 pass / 0 fail): after a `GObject.Move` **every** terminal of a moved
   structure reads `is_source` FALSE, *including its OUTPUT tunnels*, because they are unwired. So
   `is_source == FALSE` is a necessary precondition, not a sufficient identification. What identifies the row is
   the INDEX measured on the pristine original in `d1_tunnel_sources.json`, and the same run measured that the
   index SURVIVES a move intact (five structures moved: `Wire 1902 -> 1902`, `LoopTunnel 132 -> 132`, terminal
   counts 7/7/10/7/7 unchanged, every name at its own index). STATUS OPEN 37 was never a tunnel-side problem:
   `#5540` t1 is an unnamed SINK on the pristine original, and the failing run's own `bare()` — a wire delete
   plus Remove Bad Wires — deleted the tunnel and dropped every higher index by one.
3. **The from-tunnel SOURCE is re-read at wiring time, INCLUDING ITS TERMINAL INDEX.** `d1_tunnel_sources.json`
   gives `(sink_uid, sink_term) -> tunnel_uid, outer_wire`. ⚠️ CORRECTED after the same review's A3-b: the first
   draft re-read the wire VALUE but kept a terminal index `ti` taken from a read of `#637` made BEFORE any move,
   while `#637`'s own tunnels can die with the wires the moves cut — a drifted `ti` would select a live but
   WRONG tunnel, and the SINK RULE, which checks only the sink, could not see it. Now nothing is cached: at
   wiring time `#637`'s outside terminals are re-read and matched **by wire uid** against `outer_wire`. A row
   whose `outer_wire` is no longer on any of `#637`'s terminals is reported NO-ROUTE with that measurement
   instead of being wired from whatever sits at the old index.
   (Measured for reassurance, not relied on: `tools/bench/diag_moved_structure_terminals.log` PB1 — five
   structures moved with no intervening Remove Bad Wires left `Wire 1902 -> 1902` and `LoopTunnel 132 -> 132`,
   so nothing died. The match-by-wire makes the build independent of that.)

PREDICTION CONTRACT — the S-gates of `docs/d1-route-b-plan.md` §7, with counts
------------------------------------------------------------------------------
 S0   md5 `2a78e17c449cacdaf5da389818526859` BEFORE; the eight op VIs present; `TRANSPORT = "queue"` has a
      creator in the fleet; handles recorded.
 S1   fresh copy: Diagram 170 · Node 626 · Wire 1902 · LoopTunnel 132 · ControlTerminal 114 · WhileLoop 3 ·
      Local 8 · SubVI 98 · Function 181.
 S1t  `#22700` `#23020` deleted -> SubVI 98->97, Function 181->180, Node 626->624, Wire 1902->1899; no STAYING
      node left with a bare named input.
 S1d  `#5058` `#48` `#376` deleted -> SubVI 97->94, all three uids gone; every wired terminal they carried is
      captured FIRST and enters the re-wire list (this is what replaces route A's "the move cut it").
 S2   3 fresh While loops on Diagram #686 -> WhileLoop 3->6, Diagram 170->173; `#637` still owns `#6810`,
      `#22082`, `#12589`, `#11639`, `ControlTerminal #642`.
      ⚠️ `docs/d1-route-b-plan.md` §7's S2/S6 rows say **174**/**174**, because §2b counts a FOURTH loop - the
      20-slot pool For loop. This recipe builds THREE (the session brief's list) and `s1q` is not executed, so
      173 is the right number for what is built and the plan's row is not what is asserted here. Stated rather
      than silently diverged (prior-art note, `archive/peer/2026-09-17-priorart-priorart-routeb-build.md`).
 S2d  3 fresh `drop_subvi` -> SubVI 94->97; each new subVI's owner chain reads uid -> body Diagram -> its loop.
 S3   21 nodes reparented (17 -> 1.2, 4 -> 1.5, 0 -> 1.7) + 8 ControlTerminals; `Diagram` unchanged BY the moves;
      `ControlTerminal` still 114; `Local` still 8.
 S3b  census over the movers + every node sharing a wire with one + diagram 19 + `#637`'s shift registers;
      no STAYING node bared; the cut set covers the 13 §8 crossings.
 S3c  8 shift registers created (4 / 2 / 2); `ControlTerminal` still 114; all 114 panel labels present.
 F0   the source map resolves every cut terminal (route A: 109/109).
 S3w  THE LEDGER. Every row reports WIRED / FAILED / NO-ROUTE with its mechanism. Gate: **0 FAILED and
      0 NO-ROUTE**. Each from-tunnel row additionally reports SINK-RULE OK/REFUSED and `Is Broken?`.
 S1q  8 queues (Q_free/Q_work 20 · Q_meta/Q_res/Q_good/Q_rmeta unbounded · Q_focus/Q_focusback 1). ARMED ONLY
      when S3w is clean — a queue endpoint cannot rescue a sink that has no route.

RUN 3, 2026-09-17 — the two judgement decisions, and what they can and cannot reach
-----------------------------------------------------------------------------------
Run 2 ended 63 WIRED / 0 FAILED / 3 NO-ROUTE (`tools/bench/build_d1_routeb_v0_run2.log:408`). The judgement
session decided both remaining shapes; this run implements them and NOTHING else:
 (1) `#1359` t1 and `#29874` t3 -> **`Q_sr1` / `Q_sr2`**, two lock-stepped queues: Obtain on Diagram #686,
     Enqueue inside 1.1's body with its `element` BRANCHED OFF THE LEFT REGISTER'S OWN WIRE (rule 1a: the left
     register's output is the PREVIOUS iteration's value, which is what the sink consumed - the right register's
     writer is used only as the queue's TYPE source), Dequeue inside 1.2's body -> the sink by index, Release
     outside. Facts from `tools/bench/diag_sr_transport.py` -> `tools/bench/sr_transport.json`, measured
     read-only on a pristine copy in the same runner. New gate: **S3w both SR queues built**.
 (2) `#2222` t0 <- control `Z/dZ` -> `from_ctl_unnamed`: use the control's OWN wire if it has one on this copy
     (measured, not assumed), else a temporary named sink, branch by index with `OpConnectFromWire_v0`, delete
     the temporary and RE-READ the sink.
🔴 **STOPPED BEFORE IT RAN, 2026-09-17 17:45 — `SR_QUEUE_AUTHORISED = False`, `TEMP_SINK_AUTHORISED = False`.**
The prior-art review this build required (`-Dual`: `archive/peer/2026-09-17-priorart-routeb-run3-codex.md` and
`…-opus.md`, 12 findings, 0 novel) refuted decision (1) with facts already on disk, and I CONFIRMED each one
without opening LabVIEW:
 * **the type source does not exist.** The queue's element type was to come from "the node that writes the
   partner RIGHT register" = `#1359` t2 / `#29874` t5, and BOTH ARE UNNAMED
   (`docs/frame-loop-wire-graph.md:417,:421`). `sr_queue` refuses a nameless type source, so both rows would
   have returned NO-ROUTE — the run could not pass its own new gate.
 * **the sink is an AUTO-INDEXING tunnel.** `tools/bench/d1_rewire_sources.json` gives both rows
   `{"kind": "tunnel", "index_mode": 1}`. `#1359` t1 auto-indexes an ARRAY and sets the For loop's N; a queue
   delivering one element per frame iteration is a different computation, and gate S3d (`IndexMode 0`) covers
   six OTHER tunnels, not these two.
 * **the write-back was dropped.** These are registers, read AND written by the moving node
   (`:417` writer `#1359` t2 -> register `#9018`; `:421` `#29874` t5 -> `#29505`). The queue carried only the
   read side, so the loop-carried state would have silently stopped updating.
 * **the mechanism was already decided, and the queue form already abandoned.**
   `docs/frame-loop-wire-graph.md:397` ("each must live in exactly one loop"), `docs/d1-build-plan.md:446`
   (`#376` moves WITH its two registers), and `archive/peer/2026-09-14-stage2-shiftreg-primitive.md:126-129`,
   where "queues standing in for shift registers" was attacked and replaced by `Loop.Add Shift Register`
   6361000 = `OpAddShiftReg_v0`. A NAMED source for each register exists: the initialisers
   `#8953` / `#28124` `Initialize Array`.`initialized array` (`:440,:444`).
That is a rule-1a call, which a material session does not make.
⚠️ **STATED IN ADVANCE, NOT DISCOVERED AFTERWARDS: THESE CANNOT PRODUCE `ExecState 1`.** `s1q` and `s4b` are
both still SKIPPED - the element types of the other six queues are an undesigned row (STATUS NEXT) and the three
sentinel `Equal?`s depend on them - so 1.2 / 1.5 / 1.7 keep UNWIRED CONDITIONAL TERMINALS, which is a broken VI
by construction (`s4` already prints `wire 0 = the loop never stops`). Run 3's honest target is **S3w 0 FAILED
and 0 NO-ROUTE**, i.e. the ledger gate, not the save.
 S4   each new loop's conditional terminal driven by its own sentinel `Equal?`; `#637` unchanged (terminal 648
      <- wire 3457 <- `#11639`).
 S5   junk `Invoke`s purged; `remove_bad_wires_scripted`; **ExecState 1 WARM**; saved; size recorded.
      On ExecState 0 the run MEASURES (bare-terminal census over all diagrams + the broken list) and fixes only
      what the measurement names, **budget 2** (CLAUDE.md §3).
 S6   cold re-open in a restarted LabVIEW: ExecState 1, Diagram 173, WhileLoop 6, ControlTerminal 114;
      original md5 unchanged AFTER.

Rig disassembled. No hardware, no GUI. The working copy is unique per run and is deleted unless it saves at
ExecState 1 as `Track_v6_D1_GPU.vi`; the ORIGINAL is only ever READ.

================================================================================================================
v1 — RUN 4, 2026-09-18 (cycle 36). EXACTLY FOUR CHANGES over v0; nothing else is touched.
================================================================================================================
PRIOR ART re-checked before a line was typed: `docs/toolkit-capabilities.md`, `grep "^def " tools/gscript.py`,
`ls tools/recipes tools/bench`. **NO NEW OP, NO NEW TOOL.** Everything below already exists and is reused:
`g.add_shift_reg` (:619) / `g.wire_sr` (:659) / `g.set_index_mode` (:1798) / `g.tunnels` (:887, returns
`index_mode` — so IndexMode IS readable and is read BEFORE and AFTER), `CONNECT_V1` = `OpConnectNested_v1`,
`tools/bench/p2_open_copy.py`'s preload pattern (pythoncom + `GetVIReference`, read-only, no save).

A. **BASELINE `ExecState` restored into `s1()`** — `tools/recipes/build_d1_v0.py:461` has this line and v0
   dropped it. Read on the UNTOUCHED copy, in THIS recipe's own instance and flow, before any construction, so
   "born 0" is separable from "the build made it 0". 🔴 NO PRELOAD is added to the build (cycle27 Pre-decided
   14(b): a preload can cross-link the copy to the in-memory original's subVIs and `g.save(TARGET)` would write
   that). The baseline is therefore a COLD read and is logged **UNREAD** per 14a — it is a CONTROL for the S5
   read taken the same way, not a verdict.
B. **The three NO-ROUTE rows of run 3** (`tools/bench/build_d1_routeb_v0_run3.log:385-387`), implemented as
   `docs/cycle27-plan.md` Pre-decided 13 / `docs/cycle15-plan.md` Pre-decided 2 and 3 decide them:
   B1 `#1359` t1 and `#29874` t3 — **the registers MOVE WITH THEIR NODES into 1.2**. `SR_MOVED` below adds two
      more `add_shift_reg` on 1.2 (after the four of `D1.SHIFT_REGS`, so they are reg[4] and reg[5]) and wires
      them with `wire_sr`: `RightIn` FIRST from the writer terminal (`#1359` t2 / `#29874` t5 — MEASURED,
      `docs/frame-loop-wire-graph.md:417,:421`, and both are `source-side` rows that v0 never re-connected at
      all), because an untyped register takes the type of its first wire (`gscript.py:668`); then `LeftIn` into
      the reader terminal (`#1359` t1 / `#29874` t3). `index_mode` of the reader tunnel is read with
      `g.tunnels`, written back to **1** with `g.set_index_mode` and re-read — "kept exactly as the original
      has it" (cycle15 item 2).
      `SR_QUEUE_AUTHORISED` stays **False permanently** and the `sr_queue` path is now unreachable.
   B2 `Z/dZ` → `#2222` t0 — **REORDERED**: the wire is made in `s3()` by index with `OpConnectNested_v1`
      (source = `ControlTerminal #403` still on the frame body, sink = `#2222` t0 on 1.2's body, checked
      `is_source` FALSE + `wire` 0) **BEFORE** the S3-ct reparent of `#403` (cycle15 item 3). The sink is
      re-read AFTER the reparent and the result is reported either way; if the reparent cuts it, `s3w` retries
      the SAME op with both ends on 1.2's body. No temporary sink, no renaming — `TEMP_SINK_AUTHORISED` stays
      **False permanently**.
C. **MEASURE BEFORE DELETING** (Pre-decided 14). When S5 reads `ExecState 0`, `preload_reread()` restarts
   LabVIEW, opens the **ORIGINAL read-only first** and re-reads the LIVE working copy's `ExecState` in that
   instance, printing BOTH readings, and only then is the copy deleted. Nothing is saved. Any reading that
   comes back beside an exception is printed **UNREAD**, never as a value.
D. Handle count is read at S0 (0 = LabVIEW not started yet), again once the panel is open in S1, and at the end.

RUN 5, 2026-09-18 — THIS FILE. It is a BYTE COPY of `build_d1_routeb_v1.py` at its prior-art-released hash
9ff90ded8f01 plus exactly four changes, all decided by the cycle-36 judgement session after the mandatory
failed-prediction review `archive/peer/2026-09-18-routeb-run4-error2-and-zdz.md` (claude/hypothesis opus-max,
ANSWERED). It carries a NEW FILE NAME because `tools/stop_record.py`'s launch gate keys its release to a
recipe's PATH + HASH and, by design (`docs/cycle18-plan.md` Pre-decided 2), a changed hash means UNREVIEWED —
editing v1 in place makes v1 permanently un-launchable, so v1 is left exactly as run 4 ran it and v2 is
prior-art reviewed on its own bytes before it launches. What already existed and was NOT rebuilt (checked in
`docs/toolkit-capabilities.md`, `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`): every op this
recipe calls, the temporary-sink `Z/dZ` path itself (already coded below), `bench_prep.labview_handles`,
`preload_reread`, and the whole S0–S6 skeleton. Nothing new was written; four lines were changed.

  1. `TEMP_SINK_AUTHORISED = True` — the `Z/dZ` ROW ONLY. `SR_QUEUE_AUTHORISED` stays False permanently.
  2. `fact(labview_handles())` immediately before the `g.count(TARGET, "LoopTunnel")` call that raised
     `error 2` in run 4 — the control reading that log lacked.
  3. the `done/failed/noroute` ledger prints BEFORE `settle_index_modes()` — run 4 lost 66 rows to the crash.
  4. `finally:` renames the working copy aside on the EXCEPTION path only; the normal path still deletes, and
     S0 removes any earlier `_crash_` copy.

RUN 5, SECOND PATCH — the prior-art review `archive/peer/2026-09-18-priorart-d1-routeb-run5.md` STOPPED the
launch with six slugs; judgement ACCEPTED it in full (cycle 37) and amended the binding plan, `docs/cycle27-
plan.md` **Pre-decided 13a**. Six further changes, all in THIS file (v1 stays byte-for-byte as run 4 ran it):

  5. A3/B4 — the v1/B2 RETRY is a LOGGED CONTROL ONLY: on `n_src is None or st is None` it emits its NO-ROUTE
     wording as a `fact` and FALLS THROUGH to the temporary sink, instead of `noroute.append` + `return False`,
     which made `TEMP_SINK_AUTHORISED` INERT (`node_index_on()` is None for every ControlTerminal).
  6. A2 — the flag comment and the runtime refusal no longer cite the 1055 modal of `docs/NAMES.md:473-480`
     (`docs/toolkit-capabilities.md:64` records that `OpCreateEqual_v0` fetches both operands INSIDE the op, so
     that text is the FIX for the defect, not evidence of it). They state the real, SILENT hazard instead:
     `src_names=()` → `Names=[]` (`tools/recipes/build_opsentinel_ops.py:397,:400`) → `Get Outputs` empty →
     `Index Array[0]` → a default refnum with NO error, whose PREDICTED SIGNATURE is that the sink stays BARE.
  7. A2 reader — a `fact` immediately after `create_equal` logs the `src_names` passed and the created node's
     terminal census, so an A2-class failure is READ, not inferred. No new op.
  8. A3b — `OUT` is `build_d1_routeb_v2.json` and the summary label is `build_d1_routeb_v2`, so run 4's JSON
     record survives untouched.
  9. A4 — this docstring now cites `archive/peer/2026-09-17-zdz-wirecut-opus.md` and `…-codex.md`, whose `:130`
     records the EXTERNAL-SOURCE finding that `Diagram.Nodes[]` cannot list a `ControlTerminal` (the fact the
     RETRY keeps re-measuring) and whose `:160-184` weighs the temporary-sink construction itself.
 10. The S3w authorisation gate is restated to 13a: it passes when `not _SR_MADE`, `SR_QUEUE_AUTHORISED is
     False`, and the temporary sink was used by the `Z/dZ` row ONLY. Its contribution to `ok`/`clean` is
     unchanged (it is not ANDed in).

RUN 7 — v4, CUT FROM v3'S BYTES (v3 stays as run 6's record; patching it in place would invalidate its released
stop record, `stop_record._check():318-331`). Four changes, ALL of them addressing or read-only instrumentation,
NONE of them a computation change (rule 1a). They are the cycle-39 judgement session's disposition of the run-6
failed-prediction review `archive/peer/2026-09-19-routeb-run6-regression.md`:

 J1. THE CACHED WIRE MAP IS INVALIDATED AROUND THE TEMP-SINK BRACKET, TARGETED TO ONE DIAGRAM.
     `#2222` sat at node index 19 on Diagram[24] in run 5 and 20 in run 6 because the `Z/dZ` temp-sink path
     CREATES and DELETES `Equal? #10105` on that same diagram in the same pass, while `build_d1_v0.wmap` caches
     per `(target, diagram)` and is invalidated only by an explicit `fresh=True` (`build_d1_v0.py:364-372`).
     `wmap_invalidate()` drops the ONE affected diagram's entry immediately after the create (inside
     `create_equal`, the common creation helper) and immediately after the delete. NOT a global `fresh=True` on
     every lookup: extra traverses are the wrong direction while `error 2` is open.
 J2. THE `Z/dZ` ROW'S VERIFICATION BECOMES A MEASUREMENT, taken AFTER the temporary sink is deleted, and any
     wrong reading FAILS the row: (a) the source identity — `wire_source_owner` on the wire the sink actually
     carries, the ControlTerminal's own self-echo, and the control's own panel wire, which must EQUAL the sink's;
     (b) the Wire-count delta across the WHOLE bracket, which must be 0; (c) `Is Broken?` False; (d) the sink
     terminal's wire id READ BACK FROM THE MACHINE. ⚠️ (b) is read VI-WIDE (`g.count(TARGET,'Wire')`): this fleet
     has NO per-diagram wire count, and building one is out of scope (Pre-decided 2) — the log says so in words.
 J3. THE PRE-REPARENT ORDERING GATE IS RETIRED. `S3-zdz 'Z/dZ' -> #2222 t0 is wired BEFORE the #403 reparent`
     FAILED in runs 4, 5 and 6, and in run 6 the row it guards SUCCEEDED: it encodes the REORDER route that
     `docs/cycle27-plan.md` Pre-decided 13a retired in favour of the temp-sink path, which wires `Z/dZ` AFTER the
     reparent BY DESIGN. The pre-reparent state is still RECORDED as a `fact`; the J2 gate is the replacement.
 J4. NO MESSAGE IS TRUNCATED. `str(e)[:70]` truncated the only NEW failure message of run 6 (`…run6.log:418`,
     `#2222 t5 'Correction Factor'`) at exactly the colon before LabVIEW's error code, discarding the full
     `error out` string that `gscript._err()` had just been fixed to keep. All nine `[:70]` sites in this file
     now log the FULL message. `tools/gscript.py` is NOT touched by v4.

PREDICTION for run 7: S0–S3 reproduce run 6 MINUS the retired gate, i.e. 80 PASS / 0 FAIL through S3 (run 6's
single FAIL was that gate); the S3w ledger prints before `settle_index_modes()`; the `Z/dZ` row reaches the
temporary sink and is then judged by the J2 gate, WIRED or FAILED being equally a measurement; `#2222` t3/t4/t5
are addressed against a map re-walked after the temp node's create and delete, so their run-5 outcomes
(t3/t4/t5 all WIRED) are the expectation and any other outcome is reported with its FULL message. Unchanged:
rule 1 (the original is only copied; md5 gated before and after), rule 1a (no computation change), no VI is run,
no motor, ASI or camera is touched.

RUN 8 — v5, CUT FROM v4'S BYTES (v2/v3/v4 are untouched; patching one in place would invalidate its released
stop record, `stop_record._check():318-331`). THREE changes, the cycle-39 judgement session's disposition of the
run-7 failed-prediction review `archive/peer/2026-09-19-routeb-run7-index-shift.md`, which REFUTED judgement's
own H4 (the +1 index shift) and whose alternative was ACCEPTED IN FULL. K1 removes a destructive call; K2 and K3
are read-only instrumentation. NONE is a computation change (rule 1a) — K1 moves the build TOWARD preservation,
because it stops deleting wires the original has.

PRIOR ART, checked before a line was written (CLAUDE.md §3 "before creating any new op, tool, or recipe"):
`grep "^def " tools/gscript.py` + `docs/toolkit-capabilities.md` + `ls tools/recipes tools/bench`. NO NEW OP AND
NO NEW HELPER VI. Everything K2/K3 need is already built: `build_d1_v0.wmap`/`build_track_v6_core.walk` (the
per-diagram node+terminal+wire walk this recipe already calls for every address), `gscript.report_all`
(the one-traverse object census), `gscript.node_terms`. Route A already owns the survival-check pattern
(`tools/recipes/build_d1_v0.py:1115-1128`, "F1v … {len(died)} deleted by it") — route B had dropped it.

 K1. THE MID-LOOP VI-WIDE REMOVE-BAD-WIRES IS DELETED, AND NOTHING REPLACES IT (`from_ctl_unnamed`, the line
     that stood at v4's `:1669`, directly after `delete_object(Comparison)`). `VI.Block Diagram:Remove Bad
     Wires` is whole-VI; this restructure deliberately leaves wires cut between S1d/S3 and this pass
     (`build_d1_routeb_v4_run7.log:274-280` lists `#2222`'s five cut input tunnels), so a reaper inside the row
     loop destroys the build's own scaffolding — run 7's VI-wide −96. NATURAL CONTROL, already run: run 5
     returned NO-ROUTE before the bracket and never reached the reaper, and in run 5 `#2222` t2/t3/t4/t5 ALL
     wired; runs 6 and 7 reached it and they failed. The temp node's only wire w29238 SURVIVED the delete
     (`Is Broken? False`, sink read back 29238), so no targeted cleanup is owed in its place.
 K2. THE J2(b) WIRE-COUNT GATE BECOMES PER-DIAGRAM. v4's comment claimed "this fleet has no per-diagram wire
     count at all"; that premise is REFUTED. `diagram_wire_count()` (this file) counts the distinct wires
     touching a node terminal on ONE diagram, out of the walk the recipe already takes. ⚠️ The review's own
     suggestion, `len(gscript.net_map(target, diagram_index))`, is NOT used and the reason is measured, not
     preferred: `net_map` drops an untyped `Invoke` per op run on the TARGET and then purges them and calls
     `remove_bad_wires_scripted(target)` ITSELF (`tools/gscript.py:2507-2516`, `:2568-2588`) — the very VI-wide
     reaper K1 removes, fired twice mid-loop. The GATE is now the per-diagram delta-0; the VI-wide pair is read
     and logged BESIDE it so the two instruments can be compared once.
 K3. THE LEDGER REPORTS SURVIVING WIRES, NOT ATTEMPTS. (a) the `next(…, 0)` sentinel in the `from-ctl`
     `wire_control` path becomes `None`, so "no such terminal" stops colliding with "present and unwired" —
     run 7's `#2222 t5` `sink wire 0 -> 0` was NOT evidence that terminal 5 exists — and the `wire_sr` and
     plain `wire` rows, which recorded no uid and no readback at all, now take the same one-call readback every
     other path pays. (b) immediately after the S3w PRE-SETTLE ledger line (NOT after S5: the run has never yet
     reached S5) a SURVIVAL CENSUS reads `set(o["uid"] for o in g.report_all(TARGET,"Wire"))` and reports how
     many of the ledger's claimed wire uids still exist, which ones do not, and which WIRED rows registered no
     uid at all and are therefore outside the census.

PREDICTION for run 8: S0–S3 reproduce run 7, i.e. 80 PASS / 0 FAIL through S3. K1's discriminator: if the
mid-loop VI-wide reaper was the cause, `#2222` t3/t4 leave NO-ROUTE and t5 leaves FAILED — the ledger returns
toward run 5's 66/57/6/3 or better and the `Z/dZ` row's (b) reading comes back delta 0 on BOTH instruments; if
they still fail, the cause is upstream of the bracket and the census plus the per-diagram pair say which.
`Z/dZ` itself is WIRED or FAILED, either being a measurement. The `error 2` inside `settle_index_modes` is NOT
addressed by this run and is expected to recur; the ledger and the census both print BEFORE it. Unchanged:
rule 1 (the original is only copied; md5 gated before and after), rule 1a (no computation change), no VI is
run, no motor, ASI or camera is touched.

PREDICTION for run 5: S0–S3 reproduce run 4 (80 PASS / 1 FAIL); the S3w ledger PRINTS before
`settle_index_modes()` whatever happens after it; the `Z/dZ` row now REACHES `:1296`/`:1302` — the RETRY logs
its NO-ROUTE reason as a fact and falls through, the temporary `Equal?` is created, and the row ends WIRED or
BARE, either being a measurement; the restated authorisation gate PASSES. Unchanged: rule 1 (the original is
only copied; md5 gated before and after), rule 1a (no computation change), no VI is run, no motor, ASI or
camera is touched.
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, HERE)
import gscript as g                                                              # noqa: E402
from bench_prep import labview_handles                                           # noqa: E402
import build_d1_v0 as D1                                                         # noqa: E402
from build_d1_v0 import (move_in, owner_of, diag_index, wmap, terms_of,          # noqa: E402
                         sr_census, bare_named_sinks, loop_end_ref, class_index)
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1             # noqa: E402
from build_opcreateconstonterm_v0 import create_const_on_term as CONST_ON_TERM   # noqa: E402
from build_opconnectfromwire_v0 import connect_from_wire as CONNECT_FROM_WIRE    # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner                         # noqa: E402
import d1_rewire_map as MAP                                                      # noqa: E402
import build_opsentinel_ops as SENT                                              # noqa: E402

# ---------------------------------------------------------------------------- constants, all measured
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
CLAUDEDEV = g.CLAUDEDEV
BENCH = os.path.join(ROOT, "tools", "bench")
RUN_STAMP = time.strftime("%H%M%S")
# unique per run (build_d1_v0.py:183-188: LabVIEW served an edited VI from MEMORY when the name was reused);
# renamed to the deliverable only if it saves at ExecState 1.
TARGET = os.path.join(CLAUDEDEV, f"SCRATCH_routeb_{RUN_STAMP}.vi")
DELIVERABLE = os.path.join(CLAUDEDEV, "Track_v6_D1_GPU.vi")
# EVIDENCE, NOT LITTER (cycle-38 judgement on prior-art F1 `contradicted`): run 5's working copy was renamed
# aside at the crash instead of being deleted, and it is the fixture for the unrun discriminator of BOTH of run
# 5's failures (`…run5.log:396-401` error 2, `:402` error 5001). Named outright rather than globbed, and
# deleted by nothing in this recipe.
CRASH_COPY = os.path.join(CLAUDEDEV, "SCRATCH_routeb_235020_crash_001808.vi")
# A3b (prior-art, run 5): run 4's record is `build_d1_routeb_v1.json` and must survive untouched.
OUT = os.path.join(BENCH, "build_d1_routeb_v5.json")

GPU_KERNEL = os.path.join(CLAUDEDEV, "GPU_kernel_v1.vi")
# located by search, not assumed: the two are NOT in the same folder (`save trace.vi` is under `background VIs`,
# `ASI_adjust focus-subvi.vi` under `Madcity`). Both are ORIGINALS - rule 1 - and are only ever READ by
# `drop_subvi`, which places a CALL to them and does not open them for editing.
VILIB = os.path.dirname(os.path.dirname(os.path.dirname(ROOT)))     # ...\zz_LabView VI
ASI_VI = os.path.join(VILIB, "Madcity", "ASI_adjust focus-subvi.vi")
SAVE_VI = os.path.join(VILIB, "background VIs", "save trace.vi")

V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))
CONST_LABELS = json.load(open(os.path.join(BENCH, "opcreateconstonterm_labels.json"), encoding="utf-8"))
CFW_LABELS = json.load(open(os.path.join(BENCH, "opconnectfromwire_v0_labels.json"), encoding="utf-8"))
EQUAL_LABELS = json.load(open(os.path.join(BENCH, "opcreate_equal_labels.json"), encoding="utf-8"))
TUNNEL_SOURCES = {}
for _r in json.load(open(os.path.join(BENCH, "d1_tunnel_sources.json"), encoding="utf-8"))["rows"]:
    TUNNEL_SOURCES[(_r["sink_uid"], _r["sink_term"])] = _r

SIBLING_DIAG_UID = 686        # the FlatSequenceFrame diagram that HOLDS WhileLoop #637 ("diagram 19")
FRAME_LOOP_UID = 637
FRAME_BODY_UID = 639          # "diagram 43"
CTLTERM_STOP_UID = 642
COND_TERM_UID, COND_WIRE_UID, COND_SRC_UID = 648, 3457, 11639
STAY_ON_11 = [6810, 22082, 12589, 11639]

BEFORE = dict(Diagram=170, Node=626, Wire=1902, LoopTunnel=132, ControlTerminal=114, WhileLoop=3, Local=8,
              SubVI=98, Function=181)
EXPECT = dict(BEFORE)

# route B §2a — DELETED, not moved. The three subVIs are re-dropped FRESH; the two TIFF nodes are fixture
# insertions that §11h removed from D1 entirely.
FRESH = {"1.2": (5058, GPU_KERNEL, "GPU_kernel_v1.vi"),
         "1.5": (48, ASI_VI, "ASI_adjust focus-subvi.vi"),
         "1.7": (376, SAVE_VI, "save trace.vi")}
# route B §2c — 21 nodes. 1.7 receives NO moved node at all: `#376` is dropped fresh.
MOVE_TABLE = {
    "1.2": [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 1359, 2222, 2626, 6104, 8885, 9833,
            11261, 29874, 10686],
    "1.5": [10407, 3529, 3560, 3447],
    "1.7": [],
}
# THE REPARENT SET IS SIX CONTROLS over SEVEN `from-ctl` rows - not eight.
# ⚠️ CORRECTED 2026-09-17 by `archive/peer/2026-09-17-priorart-priorart-routeb-build.md` A3(ii). Route B §2c
# says "8, not 6" and adds `min value` #17257 and `Force (pN) vs Extension (nm) ` #8038 - but both are
# INDICATORS (`tools/recipes/probe_move_ctlterm_v0.py:7-8`: `min value` is driven by #10969, `Force (pN) vs
# Extension (nm) ` by #11261), so they are SINKS of a node, not sources of a `from-ctl` row. `d1_rewire_sources
# .json` has exactly 7 `from-ctl` rows and every one is `"indicator": false` over these six labels - neither
# indicator appears. The two extra rows §2c found (`Force\nsmoothing\nhalf-width` #28148 -> #1359 t7 and
# `Extension\nmedian filter\nhalf-width` #28996 -> #1359 t8 / #29874 t6) ARE real and ARE here; what §2c got
# wrong is adding the indicators on top of them.
CTLTERM_LABELS_12 = ["Auto-Reset", "Reset Tracking", "Z/dZ", "Correction Factor",
                     "Force\nsmoothing\nhalf-width", "Extension\nmedian filter\nhalf-width"]
CTLTERM_OWNERS = os.path.join(BENCH, "ctlterm_owners.json")
NON_INDEXED = ["cross size", "# of bead 4 packs", "4 pack remainder", "Array of cal clusters",
               "Real-space cosine window", "Cosine bandpass\nfor Hilbert "]
EXPECTED_CROSSINGS = [5637, 3040, 373, 5859, 505, 5975, 121, 42, 3512, 3646, 7429, 3912, 4027]

# 🔴 OFF, and only the judgement session may turn it on. See the RUN 3 block of this file's docstring: the
# Q_sr1/Q_sr2 mechanism is refuted by measurements already on disk, and turning this True would spend ~550 s and
# the LabVIEW lock to fail the run's own gate. The code is left in place so the decision is about the design,
# not about re-writing it.
SR_QUEUE_AUTHORISED = False
# Likewise: decision (2)'s TEMPORARY-SINK branch. Reading the control's OWN wire is safe and stays on; creating a
# bare `Equal?` with `src_names=()` is UNMEASURED.
# ⚠️ THE OLD GROUNDS WERE MIS-CITED and are withdrawn (prior-art A2, cycle27 Pre-decided 13a): this comment used
# to cite a 1055 MODAL DIALOG from an invalid terminal refnum (`docs/NAMES.md:473-480`), but
# `docs/toolkit-capabilities.md:64` (cycle27 Pre-decided 13a says `:52`; the row has MOVED - MEASURED here,
# reported under OPEN, not silently corrected in the plan) records that `OpCreateEqual_v0` fetches BOTH
# OPERANDS INSIDE THE OP, so no
# terminal refnum ever crosses COM - that text is the FIX for that defect, not evidence of it.
# THE REAL HAZARD IS SILENT, not modal: `src_names=()` -> `Names=[]`
# (`tools/recipes/build_opsentinel_ops.py:397,:400`) -> `Get Outputs` returns an empty array -> `Index Array[0]`
# yields a DEFAULT refnum WITH NO ERROR. PREDICTED SIGNATURE: the write silently does nothing and THE SINK STAYS
# BARE - which this row's own discriminator already reads (the `wire {after}` / `Is Broken?` fact below and the
# `retry`/`ledger row present` fact after the ledger). A measurable outcome, not a dialog that hangs the run.
# 🟢 RUN 5 (this file = v2, byte-copy of v1 + the four changes below). Cycle-36 judgement decision (b):
# TURNED ON for the `Z/dZ` ROW ONLY, as the discriminating test. Grounds, measured and not asserted: the
# REORDER that was to make this branch unnecessary has NO by-index route (`build_d1_routeb_v1_run4.log:163`)
# and the S3 node moves cut w730, not the `#403` reparent (`archive/peer/2026-09-18-routeb-run4-error2-and-
# zdz.md`). The branch uses ONLY already-built ops (`OpCreateEqual_v0` -> `wire_control` ->
# `OpConnectFromWire_v0` -> delete + `remove_bad_wires_scripted`): no new op, no new device.
# `SR_QUEUE_AUTHORISED` stays False PERMANENTLY.
TEMP_SINK_AUTHORISED = True

# ---- v1 / B1: the TWO registers that MOVE WITH THEIR NODES into 1.2 (cycle15 Pre-decided 2, cycle27 13).
# Every uid below is MEASURED, not inferred: `docs/frame-loop-wire-graph.md` right-register table row 8/12
# (`:417`,`:421` = writer `#1359` t2 -> right #9018, `#29874` t5 -> right #29505) and left-register table row
# 8/12 (reader `#1359` t1 <- left #9025 w9097, `#29874` t3 <- left #29512 w28039). `initial` is the original's
# initialiser and is RECORDED ONLY — v0 wires no initial value for ANY of its 8 registers either, so wiring it
# for 2 of 10 would be an inconsistency this session is not authorised to introduce (reported under OPEN).
# (right_uid, left_uid, name, reader=(node_uid, term), writer=(node_uid, term), reader_index_mode, initial)
SR_MOVED = {
    "1.2": [(9018, 9025, "#1359 For Loop register (unnamed)", (1359, 1), (1359, 2), 1,
             "#8953 Initialize Array t1 'initialized array' w9051"),
            (29505, 29512, "#29874 For Loop register (unnamed)", (29874, 3), (29874, 5), 1,
             "#28124 Initialize Array t1 'initialized array' w29122")],
}
SR_MOVED_ROWS = {(rec[3][0], rec[3][1]): (row, rec) for row, recs in SR_MOVED.items() for rec in recs}
# ---- v1 / B2: the REORDERED Z/dZ wire. `#2222` t0 is UNNAMED, so it is reached by INDEX with
# OpConnectNested_v1; the source is the ControlTerminal the by-effect resolver returns for 'Z/dZ' (run 3
# measured #403, `build_d1_routeb_v0_run3.log:15`, but the uid is taken from THIS run's resolver, never pinned).
ZDZ_LABEL = "Z/dZ"
ZDZ_SINK = (2222, 0)
PREWIRED = {}
# (tag, label) per row that actually CREATED a temporary named sink. Read by the S3w authorisation gate, which
# cycle27 Pre-decided 13a scopes to the `Z/dZ` row ONLY.
_TEMP_SINK_USED = []

g._run.__defaults__ = (6.0, 180.0)
passes, fails, facts = [], [], []


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def node_index_on(diagram_index, uid, fresh=False):
    w = wmap(TARGET, diagram_index, fresh)
    return w[uid][0] if uid in w else None


def wmap_invalidate(diagram_index):
    """J1 (cycle-39 judgement, disposing `archive/peer/2026-09-19-routeb-run6-regression.md` Q-B1): drop the
    CACHED walk of ONE diagram, so the NEXT reader re-walks it.

    `build_d1_v0.wmap` caches per `(target, diagram_index)` and is invalidated only by an explicit `fresh=True`
    (`tools/recipes/build_d1_v0.py:364-372`). The temporary-sink path CREATES and DELETES an `Equal?` on the
    destination body diagram inside one pass, which shifts that diagram's whole `Nodes[]` index space - run 5
    addressed `#2222` at N[19] on Diagram[24], run 6 at N[20]. Every row addressed against a map taken on the
    other side of that bracket is addressing by a stale index.

    TARGETED ON PURPOSE. The alternative - `fresh=True` on every lookup - buys the same correctness with a full
    `B.walk` per lookup, and extra traverses are exactly the wrong direction while the `error 2`
    (`Traverse for GObjects`) crash is open and unexplained. Nothing is read or written on the machine here: it
    is a dict `pop` on this process's own cache.

    Returns (key, hit) so the caller can log whether anything was actually dropped."""
    key = (TARGET, int(diagram_index))
    hit = key in D1._WALKS
    D1._WALKS.pop(key, None)
    return key, hit


def diagram_wire_count(diagram_index, fresh=False):
    """K2 (cycle-39 judgement, disposing `archive/peer/2026-09-19-routeb-run7-index-shift.md` Q2): the number of
    DISTINCT wires touching a node terminal on ONE diagram - the per-diagram wire count v4's J2(b) said this
    fleet did not have.

    ⚠️ THE REVIEW'S OWN SUGGESTION, `len(gscript.net_map(target, diagram_index))`, IS NOT USED, AND THE REASON IS
    MEASURED, NOT PREFERRED: `net_map` is DESTRUCTIVE ON THE TARGET. Every per-node/per-terminal run of
    `OpNetInfo_v1` drops an untyped `Invoke` on the VI (75 of them from one walk of an 8-node diagram,
    `tools/gscript.py:2507-2516`), and `net_map` then purges them and calls
    **`remove_bad_wires_scripted(target)`** itself (`tools/gscript.py:2568-2588`) - i.e. exactly the VI-wide
    reaper K1 removes from this bracket, fired TWICE (once per reading) in the middle of the row loop. Using it
    here would destroy the discriminator it was asked to instrument.

    So the count is taken from the fleet's OWN non-destructive walker, which this recipe already calls for every
    address: `build_d1_v0.wmap` -> `build_track_v6_core.walk` = `node_labels` + `node_terms_uid` per node
    (`tools/recipes/build_track_v6_core.py:84-92`). It carries the SAME caveat the review stated for `net_map`:
    it sees only wires that touch a node terminal on this diagram, so a fully orphaned wire is invisible - which
    for the J2(b) question is a feature, because it counts exactly the wires still attached to something.
    Read-only; no op writes anything."""
    w = wmap(TARGET, diagram_index, fresh)
    return len({r["wire"] for rec in w.values() for r in rec[2] if r.get("wire")})


def crash_copy_measure():
    """MEASURE run 5's renamed-aside crash copy; delete nothing (cycle-38 judgement on prior-art F1).

    Four readings, in this order: md5, size, `ExecState` read COLD, and `ExecState` read again with the ORIGINAL
    PRELOADED READ-ONLY (`docs/cycle27-plan.md` Pre-decided 14a - a cold 0 measures subVI linkage, so only the
    preloaded read is a verdict on the copy itself). The preloaded read runs in a RESTARTED instance and this
    function restarts LabVIEW AGAIN before returning, so the build below still runs in an instance with nothing
    preloaded - Pre-decided 14(b) forbids a preload inside the build, because a cross-linked copy would be
    written by `g.save(TARGET)`. NOTHING IS SAVED and NOTHING IS RUN here; a value that comes back beside an
    exception is reported UNREAD, never as a value (Pre-decided 14).
    Prior art checked before writing this: `preload_reread()` below already implements the preload pattern for
    the LIVE copy at the END of a run; it restarts LabVIEW and takes the ORIGINAL's own reading too, so the two
    share that shape deliberately. Nothing else in the fleet reads a stray copy's ExecState."""
    print("\n  --- S0 crash-copy MEASUREMENT (evidence; nothing here deletes it)", flush=True)
    if not os.path.exists(CRASH_COPY):
        fact(f"S0 crash copy {os.path.basename(CRASH_COPY)} is NOT on disk - every reading below is UNREAD")
        return
    fact(f"S0 crash copy {os.path.basename(CRASH_COPY)}: md5 {md5(CRASH_COPY)}, "
         f"size {os.path.getsize(CRASH_COPY)} bytes")
    try:
        es_cold = g.exec_state(CRASH_COPY)
        fact(f"S0 crash copy ExecState COLD (no preload) = {es_cold} - by Pre-decided 14a a cold 0 is UNREAD as "
             f"a verdict on the copy; it measures subVI linkage")
    except Exception as e:
        fact(f"S0 crash copy COLD ExecState UNREAD - {type(e).__name__}: {str(e)[:100]}")
    # ---- preloaded re-read, in its own restarted instance
    try:
        g.close_panel(CRASH_COPY)
    except Exception:
        pass
    g._lv = None
    import subprocess

    def _restart(tag):
        try:
            rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                                capture_output=True, text=True, timeout=600)
            fact(f"S0 crash copy: lv_restart {tag} rc={rc.returncode}; handles now {labview_handles()}")
        except Exception as e:
            fact(f"S0 crash copy: lv_restart {tag} FAILED ({type(e).__name__}: {str(e)[:80]})")
        g._lv = None

    m_before = md5(ORIGINAL)
    _restart("BEFORE the preloaded read (nothing the cold read left resident can confound it)")
    app = vo = vc = None
    try:
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        app = dynamic.Dispatch("LabVIEW.Application")
        try:
            vo = app.GetVIReference(ORIGINAL, "", False, 0)
            fact(f"S0 crash copy: the ORIGINAL is resident READ-ONLY, its own ExecState {int(vo.ExecState)}")
        except Exception as e:
            fact(f"S0 crash copy: the ORIGINAL could NOT be preloaded - UNREAD ({type(e).__name__}: "
                 f"{str(e)[:90]}); the reading below is therefore still COLD and stays UNREAD")
        try:
            vc = app.GetVIReference(CRASH_COPY, "", False, 0)
            fact(f"S0 **crash copy PRELOADED ExecState = {int(vc.ExecState)}** (1 = idle/runnable, 0 = broken)")
        except Exception as e:
            fact(f"S0 crash copy PRELOADED ExecState UNREAD - {type(e).__name__}: {str(e)[:90]}")
    except Exception as e:
        fact(f"S0 crash copy preloaded re-read could not run at all - UNREAD ({type(e).__name__}: {str(e)[:110]})")
    finally:
        vo = None                                      # reference hygiene (CLAUDE.md §3): every ref opened here
        vc = None                                      # is released before the instance is restarted
        app = None
    # Pre-decided 14(b): the BUILD must not run with the original preloaded, so the instance is replaced again.
    _restart("AFTER the preloaded read (so the build itself starts in a clean instance)")
    m_after = md5(ORIGINAL)
    fact(f"S0 crash copy: original md5 across the preloaded read {m_before} -> {m_after} "
         f"({'UNCHANGED' if m_before == m_after else '**CHANGED**'}); nothing saved, nothing run; the crash copy "
         f"is STILL ON DISK = {os.path.exists(CRASH_COPY)}")


# ============================================================================== S0
def s0():
    print("\n=== S0: preconditions", flush=True)
    # P4 IS REVERSED (cycle-38 judgement, dispatch 3, on prior-art finding F1 `contradicted`,
    # `archive/peer/2026-09-19-priorart-d1-routeb-run6.md`): the renamed-aside crash copy is EVIDENCE, not litter.
    # It is the named fixture for the still-unrun discriminator of BOTH of run 5's failures, so S0 MEASURES it and
    # DELETES NOTHING. There is deliberately no `SCRATCH_routeb_*_crash_*` glob anywhere in this file - a glob is
    # how the previous version would have swept the fixture away; the one file is named outright.
    crash_copy_measure()
    m0 = md5(ORIGINAL)
    gate("S0a original md5 BEFORE", m0 == ORIG_MD5, m0, fatal=True)
    need = [("OpMoveIn_v0.vi", None), ("OpConnectNested_v1.vi", None), ("OpCreateConstOnTerm_v0.vi", None),
            ("OpConnectFromWire_v0.vi", None), ("OpStopFromNode_v0.vi", None), ("OpCreateEqual_v0.vi", None),
            ("OpLoopEndRef_v0.vi", None), ("OpWireSource_v5.vi", None)]
    miss = [n for n, _ in need if not os.path.exists(os.path.join(CLAUDEDEV, n))]
    gate("S0b the eight writer/reader ops are on disk", not miss, f"missing {miss}", fatal=True)
    miss2 = [p for p in (GPU_KERNEL, ASI_VI, SAVE_VI) if not os.path.exists(p)]
    gate("S0c the three subVIs to drop fresh are on disk", not miss2, f"missing {miss2}", fatal=True)
    gate("S0d TRANSPORT 'queue' has a creator in the fleet today", hasattr(g, "queue_node"),
         "gscript.queue_node -> OpQueueObtain/Enqueue/Dequeue/Release_v0, core 162/162")
    h0 = labview_handles()
    fact(f"LabVIEW handles before: {h0} (fresh-instance baseline ~31,500)")
    # RUN 5 (cycle-36 judgement (d)): a crash RENAMES the working copy aside instead of deleting it, so the
    # state can be measured afterwards. Cycle 38 kept that evidence: the measurement ran at the TOP of S0 and
    # nothing in this run deletes it.
    fact(f"S0 crash-copy MEASUREMENT already ran at the top of S0; the file is untouched and stays on disk: "
         f"{os.path.exists(CRASH_COPY)}")
    fact(f"S0 refnum counters at entry: {g.ref_counts()} (in-process VI Server refs opened by gscript - NOT "
         f"the kernel handle count, which cannot see them)")
    return h0


# ============================================================================== S1 / S1t / S1d
def s1():
    print("\n=== S1: the D1 working copy", flush=True)
    if os.path.exists(TARGET):
        os.remove(TARGET)
    shutil.copy2(ORIGINAL, TARGET)
    mt = md5(TARGET)
    gate("S1z the working copy on DISK is byte-identical to the original before LabVIEW sees it", mt == ORIG_MD5,
         f"{mt} at {TARGET}", fatal=True)
    g.open_panel(TARGET)
    time.sleep(1.0)
    # ---- v1 / A: THE BASELINE EXECSTATE, restored from `build_d1_v0.py:461`. Read on the UNTOUCHED copy, in
    # this recipe's OWN instance and flow, BEFORE a single construction call. No preload is added (Pre-decided
    # 14(b): a preload can cross-link the copy to the in-memory original's subVIs and `g.save(TARGET)` at S5
    # would then write that). It is therefore the SAME KIND of read as S5's, which is exactly what makes it a
    # control: whatever it says, S5's number is only meaningful as a DIFFERENCE from it.
    try:
        es0 = g.exec_state(TARGET)
        fact(f"S1 BASELINE ExecState of the untouched working copy = {es0} — read COLD (no preload), so by "
             f"cycle27 Pre-decided 14a this value is UNREAD as a verdict on legality; it measures subVI "
             f"LINKAGE in this instance. Its job is to be compared with S5's read, taken the same way.")
    except Exception as e:
        es0 = None
        fact(f"S1 BASELINE ExecState UNREAD — the read itself raised {type(e).__name__}: {str(e)[:100]}")
    fact(f"S1 LabVIEW handles with the copy open: {labview_handles()}")
    got = {c: g.count(TARGET, c) for c in BEFORE}
    fact(f"S1 BEFORE census: {got}")
    gate("S1 the copy matches the BEFORE census", all(got[c] == BEFORE[c] for c in BEFORE),
         f"{ {c: (BEFORE[c], got[c]) for c in BEFORE if got[c] != BEFORE[c]} } (empty = all match)", fatal=True)
    return got


def s1t():
    print("\n=== S1t: delete the FIXTURE TIFF writer before any other edit (§11h)", flush=True)
    d43 = diag_index(TARGET, FRAME_BODY_UID)
    gate("S1t Diagram #639 is Traverse index 43", d43 == 43, f"index {d43}")
    bare0 = bare_named_sinks(TARGET, d43)
    c0 = {c: g.count(TARGET, c) for c in ("SubVI", "Function", "Node", "Wire")}
    for uid, cls, label in D1.TIFF_DELETE:
        order = [o["uid"] for o in g.report_all(TARGET, cls)]
        gate(f"S1t #{uid} ({label}) present before deletion", uid in order, f"not among {cls}", fatal=True)
        g.delete_object(TARGET, cls, order.index(uid), verify=False)
        if cls in EXPECT:
            EXPECT[cls] -= 1
    g.remove_bad_wires_scripted(TARGET)
    node_uids = {o["uid"] for o in g.report_all(TARGET, "Node")}
    for uid, _cls, label in D1.TIFF_DELETE:
        gate(f"S1t #{uid} ({label}) is GONE", uid not in node_uids)
    c1 = {c: g.count(TARGET, c) for c in c0}
    gate("S1t counts moved exactly as §11h predicts (SubVI -1, Function -1, Node -2, Wire -3)",
         c1 == dict(SubVI=97, Function=180, Node=624, Wire=1899), f"{c0} -> {c1}")
    bare1 = bare_named_sinks(TARGET, d43, fresh=True)
    new_bare = {k: v for k, v in bare1.items() if k not in bare0}
    gate("S1t no STAYING node was left with a bare named input", not new_bare,
         f"newly bare {sorted((u, i, n) for (u, i), n in new_bare.items())[:8]}")
    return d43


def s1d(d43):
    """ROUTE B's own step. The three subVIs are DELETED, and their wired terminals are captured FIRST so the
    re-wire list carries them exactly as route A's move-diff did (`d1_rewire_map` classifies the same rows)."""
    print("\n=== S1d: delete #5058 / #48 / #376 — they are re-DROPPED fresh, not moved (route B §2a)", flush=True)
    cut = []
    for row, (uid, _path, label) in FRESH.items():
        t = terms_of(TARGET, d43, uid)
        if not gate(f"S1d #{uid} ({label}) is a node on diagram 43 and its terminals read", bool(t),
                    f"{len(t)} terminals"):
            continue
        wired = [(uid, i, nm, src, w) for i, (nm, src, w) in t.items() if w]
        cut.extend(wired)
        fact(f"S1d #{uid} {label} -> {row}: {len(t)} terminals, {len(wired)} wired (all enter the re-wire list)")
    before_sub = g.count(TARGET, "SubVI")
    for _row, (uid, _p, label) in FRESH.items():
        ids = [o["uid"] for o in g.report_all(TARGET, "SubVI")]
        gate(f"S1d #{uid} ({label}) found for deletion", uid in ids, "not in report_all('SubVI')", fatal=True)
        g.delete_object(TARGET, "SubVI", ids.index(uid), verify=False)
        EXPECT["SubVI"] -= 1
    after_sub = g.count(TARGET, "SubVI")
    gone = {o["uid"] for o in g.report_all(TARGET, "Node")}
    gate("S1d all three uids are gone and SubVI 97 -> 94",
         after_sub == 94 and not any(u in gone for u, _p, _l in FRESH.values()),
         f"SubVI {before_sub} -> {after_sub}; still present "
         f"{[u for u, _p, _l in FRESH.values() if u in gone]}")
    # the sinks their outputs used to feed are now bare - route B §2a's warning, made machine-visible
    bare = bare_named_sinks(TARGET, d43, fresh=True)
    fact(f"S1d {len(bare)} bare named sinks on diagram 43 after the three deletes "
         f"(§2a: #6384's error chain via w541 and #12589 t1 via w9113 are among them)")
    fact(f"S1d re-wire rows captured from the deleted nodes: {len(cut)}")
    return cut


# ============================================================================== S2 / S2d
def s2():
    print("\n=== S2: three fresh While loops on Diagram #686", flush=True)
    sib_i = diag_index(TARGET, SIBLING_DIAG_UID)
    fact(f"Diagram#{SIBLING_DIAG_UID} (holder of WhileLoop#{FRAME_LOOP_UID}) is Traverse index {sib_i}")
    loops = {}
    for row, loc in (("1.2", (2600, 2600)), ("1.5", (2600, 3400)), ("1.7", (2600, 4200))):
        dg0, wl0 = g.uids(TARGET, "Diagram"), g.uids(TARGET, "WhileLoop")
        g.loop_in("while", TARGET, sib_i, loc)
        nd, nw = g.new_since(TARGET, "Diagram", dg0), g.new_since(TARGET, "WhileLoop", wl0)
        gate(f"S2 loop {row} created", len(nd) == 1 and len(nw) == 1,
             f"+{len(nd)} diagrams, +{len(nw)} while loops", fatal=True)
        loops[row] = dict(loop=nw[0]["uid"], body=nd[0]["uid"])
        fact(f"{row}: WhileLoop #{nw[0]['uid']}, body Diagram #{nd[0]['uid']}")
    gate("S2 WhileLoop 3 -> 6 and Diagram 170 -> 173",
         g.count(TARGET, "WhileLoop") == BEFORE["WhileLoop"] + 3
         and g.count(TARGET, "Diagram") == BEFORE["Diagram"] + 3,
         f"WhileLoop {g.count(TARGET, 'WhileLoop')}, Diagram {g.count(TARGET, 'Diagram')}")
    gate("S2b #637 still exists", FRAME_LOOP_UID in [o["uid"] for o in g.report_all(TARGET, "WhileLoop")])
    for uid in STAY_ON_11 + [CTLTERM_STOP_UID]:
        try:
            _c, ou = owner_of(TARGET, uid)
            gate(f"S2c #{uid} still owned by the frame loop body", ou == FRAME_BODY_UID, f"owner {ou}")
        except Exception as e:
            gate(f"S2c #{uid} still owned by the frame loop body", False, f"UNRESOLVED READ: {str(e)[:120]}")
    return loops


def s2d(loops):
    print("\n=== S2d: drop the three subVIs FRESH, each inside its own loop body", flush=True)
    fresh_uid = {}
    for row, (old, path, label) in FRESH.items():
        sv0 = g.uids(TARGET, "SubVI")
        g.drop_subvi(TARGET, path, diag_index(TARGET, loops[row]["body"]), (900, 400))
        new = g.new_since(TARGET, "SubVI", sv0)
        if not gate(f"S2d {label} dropped into {row}", len(new) == 1, f"new subVIs {new}"):
            continue
        u = new[0]["uid"]
        fresh_uid[old] = u
        try:
            _c, ou = owner_of(TARGET, u)
            _c2, ou2 = owner_of(TARGET, ou) if ou else (None, None)
            gate(f"S2d {label} owner chain: uid -> body Diagram -> WhileLoop",
                 ou == loops[row]["body"] and ou2 == loops[row]["loop"],
                 f"#{u} -> Diagram#{ou} (want {loops[row]['body']}) -> WhileLoop#{ou2} (want {loops[row]['loop']})")
        except Exception as e:
            gate(f"S2d {label} owner chain: uid -> body Diagram -> WhileLoop", False, f"{str(e)[:120]}")
        fact(f"S2d {label}: old #{old} -> fresh #{u} on {row}")
    gate("S2d SubVI 94 -> 97", g.count(TARGET, "SubVI") == EXPECT["SubVI"] + 3,
         f"SubVI {g.count(TARGET, 'SubVI')} (want {EXPECT['SubVI'] + 3})")
    EXPECT["SubVI"] += 3
    # ⚠️ UID REUSE, MEASURED in route A (`build_d1_v0.py:719-726`): after the delete, `drop_subvi` came back with
    # the deleted node's uid **5058 again**. The ordering here is safe by construction - every delete in S1d
    # precedes every drop in S2d, with S1d's "all three uids are gone" gate in between - but the fact is recorded
    # rather than left implicit (prior-art B4), because `RETARGET` and `S3b-collateral`'s filter both key on
    # exactly these uids.
    reused = [f"#{old} -> #{new}" for old, new in fresh_uid.items() if old == new]
    fact(f"S2d uid REUSE check: {len(reused)} of {len(fresh_uid)} fresh drops came back with the deleted uid "
         f"{reused} (harmless - RETARGET is then the identity for that row; the hazard is only if a drop had "
         f"preceded a delete, which S1d/S2d's ordering forbids)")
    return fresh_uid


# ============================================================================== S3 / S3b
PROBE = os.path.join(CLAUDEDEV, f"SCRATCH_ctprobe_{RUN_STAMP}.vi")


def resolve_ctlterms():
    """THE CONTROL-TERMINAL UID RESOLVER — `probe_move_ctlterm_v0`'s BY-EFFECT route (header point 1), run on a
    THROWAWAY copy because a move CUTS the terminal's wire and moving back does not restore it. There is no
    lookup: `Generic.Owner` of a ControlTerminal is its DIAGRAM (measured, `probe_move_ctlterm_v0.log:47`) and
    `ControlTerminal.Control` 6353000 is UNVERIFIED and unbuilt (`docs/vi-server-ids.json:145`). Candidates come
    from `tools/bench/ctlterm_owners.json`, recorded at this same md5, not re-derived."""
    print("\n=== S3-ct: resolve the 6 ControlTerminal uids BY EFFECT, on a throwaway copy", flush=True)
    with open(CTLTERM_OWNERS, encoding="utf-8") as f:
        owners = json.load(f)
    gate("S3-ct ctlterm_owners.json was recorded at THIS original's md5", owners.get("md5") == ORIG_MD5,
         f"{owners.get('md5')}")
    cands = [int(u) for u, v in owners["owners"].items() if v.get("owner_uid") == FRAME_BODY_UID]
    fact(f"S3-ct {len(cands)} ControlTerminals are owned by Diagram #{FRAME_BODY_UID} "
         f"(docs/d1-build-plan.md:220 says 31)")
    out = {}
    if os.path.exists(PROBE):
        os.remove(PROBE)
    shutil.copy2(ORIGINAL, PROBE)
    try:
        g.open_panel(PROBE)
        time.sleep(1.0)
        sib_i = diag_index(PROBE, SIBLING_DIAG_UID)
        dg0 = g.uids(PROBE, "Diagram")
        g.loop_in("while", PROBE, sib_i, (4200, 2600))
        nd = g.new_since(PROBE, "Diagram", dg0)
        if not gate("S3-ct the probe copy got a destination loop", len(nd) == 1, f"{nd}"):
            return out
        body_uid = nd[0]["uid"]
        prev = {r["uid"]: r["wire"] for r in g.panel_wiring(PROBE)}
        lbl_of = {r["uid"]: r["label"] for r in g.panel_wiring(PROBE)}
        wanted = set(CTLTERM_LABELS_12)
        y = 60
        for u in cands:
            if not wanted:
                break
            try:
                move_in(PROBE, u, diag_index(PROBE, body_uid), (60, y))
            except Exception as e:
                fact(f"S3-ct candidate #{u}: move raised {e} - skipped")          # J4: full message
                continue
            y += 90
            now = {r["uid"]: r["wire"] for r in g.panel_wiring(PROBE)}
            changed = [cu for cu in prev if now.get(cu) != prev[cu]]
            prev = now
            for cu in changed:
                lb = lbl_of.get(cu)
                if lb in wanted:
                    out[lb] = u
                    wanted.discard(lb)
                    fact(f"S3-ct {lb!r}: control #{cu} <- ControlTerminal #{u} (its panel row's wire changed "
                         f"when #{u} moved - probe_move_ctlterm_v0.py:327-351's route)")
            if len(changed) > 1:
                fact(f"S3-ct candidate #{u} changed {len(changed)} panel rows "
                     f"{[lbl_of.get(c) for c in changed]} - REPORTED; a move that changes more than one row is "
                     f"ambiguous and its mapping is not trustworthy")
        gate(f"S3-ct all {len(CTLTERM_LABELS_12)} labels resolved to a ControlTerminal uid", not wanted,
             f"unresolved {sorted(wanted)} after {len(cands)} candidates")
    finally:
        try:
            g.close_panel(PROBE)
        except Exception:
            pass
        try:
            if os.path.exists(PROBE):
                os.remove(PROBE)
            fact(f"S3-ct probe copy deleted in the same run: {os.path.basename(PROBE)}")
        except Exception as e:
            fact(f"S3-ct probe copy NOT deleted ({str(e)[:60]})")
    return out


def s3(loops, deleted_cut, ct_uids):
    print("\n=== S3: move 21 nodes + 8 ControlTerminals (route B §2c)", flush=True)
    frame_i = diag_index(TARGET, FRAME_BODY_UID)
    outer_i = diag_index(TARGET, SIBLING_DIAG_UID)
    frame_by = wmap(TARGET, frame_i, fresh=True)
    outer_by = wmap(TARGET, outer_i, fresh=True)
    moving = [u for us in MOVE_TABLE.values() for u in us]
    moving_wires = {r["wire"] for u in moving if u in frame_by for r in frame_by[u][2] if r["wire"]}
    neighbours = sorted({u for u, (_n, _l, rows) in frame_by.items()
                         if u not in moving and any(r["wire"] in moving_wires for r in rows)})
    fact(f"S3b net neighbours on diagram 43 (stay put, share a net with a mover): {neighbours}")
    before_terms = {uid: terms_of(TARGET, frame_i, uid) for uid in list(moving) + neighbours}
    before_outer = {uid: terms_of(TARGET, outer_i, uid) for uid in sorted(outer_by)}
    loop_i_637 = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(FRAME_LOOP_UID)
    before_sr = sr_census(TARGET, loop_i_637)
    fact(f"S3b BEFORE: {len(before_terms)} nodes on d43 ({len(moving)} moving + {len(neighbours)} neighbours), "
         f"{len(before_outer)} on d19, {len(before_sr)} shift registers of #637")

    # --- #637's own outside terminals: the FROM-TUNNEL SOURCES, read on Diagram #686 BEFORE any move.
    n637 = node_index_on(outer_i, FRAME_LOOP_UID)
    t637 = {r["i"]: (r["name"], r["is_source"], r["wire"])
            for r in (g.node_terms(TARGET, outer_i, n637) if n637 is not None else [])}
    by_wire637 = {w: i for i, (_n, _s, w) in t637.items() if w}
    fact(f"S3b #637 is Diagram[{outer_i}].Nodes[{n637}] with {len(t637)} outside terminals; "
         f"{sum(1 for _n, s, w in t637.values() if not s and w)} of them are INPUT tunnels carrying a wire")

    y = 60
    for row, uids in MOVE_TABLE.items():
        for uid in uids:
            body_uid, loop_uid = loops[row]["body"], loops[row]["loop"]
            move_in(TARGET, uid, diag_index(TARGET, body_uid), (60, y))
            y += 130
            try:
                oc, ou = owner_of(TARGET, uid)
                oc2, ou2 = owner_of(TARGET, ou) if ou else (None, None)
                ok = (ou == body_uid and ou2 == loop_uid)
            except Exception as e:
                oc = ou = oc2 = ou2 = f"<{str(e)[:50]}>"
                ok = False
            gate(f"S3 #{uid} -> {row}", ok,
                 f"owner {oc}#{ou} (want Diagram#{body_uid}); owner(owner) {oc2}#{ou2} "
                 f"(want WhileLoop#{loop_uid})", fatal=True)

    # ==================== v1 / B2: THE REORDER — 'Z/dZ' -> #2222 t0 BEFORE the S3-ct reparent of #403 =========
    # cycle15 Pre-decided 3 / cycle27 Pre-decided 13, verbatim: "wire `Z/dZ` to `#2222` t0 (by index,
    # `OpConnectNested_v1`, sink is `is_source` FALSE) BEFORE the S3-ct reparent of `ControlTerminal #403`; no
    # temporary sink, no renaming." The node moves above have already put `#2222` inside 1.2's body while the
    # ControlTerminal is still on the frame body, so this is a CROSS-DIAGRAM write, which is what v1 of the op
    # exists for. NOTHING here is assumed: the source node index, its terminal, and the sink's `is_source`/`wire`
    # are all read live, and a missing address is reported as a MEASUREMENT rather than worked around.
    print("\n=== S3-zdz: the REORDERED 'Z/dZ' -> #2222 t0 wire (cycle15 Pre-decided 3)", flush=True)
    zdz_ct = ct_uids.get(ZDZ_LABEL)
    zs_uid, zs_t = ZDZ_SINK
    b12 = diag_index(TARGET, loops["1.2"]["body"])
    frame_now = diag_index(TARGET, FRAME_BODY_UID)
    wmap(TARGET, b12, fresh=True)
    wmap(TARGET, frame_now, fresh=True)
    n_sink = node_index_on(b12, zs_uid)
    n_src = node_index_on(frame_now, zdz_ct) if zdz_ct else None
    sink_live = terms_of(TARGET, b12, zs_uid) if n_sink is not None else {}
    src_live = terms_of(TARGET, frame_now, zdz_ct) if n_src is not None else {}
    fact(f"S3-zdz ControlTerminal for {ZDZ_LABEL!r} = #{zdz_ct}; on Diagram[{frame_now}] it is Nodes[{n_src}] "
         f"with terminals {sorted(src_live.items())}; sink #{zs_uid} is Diagram[{b12}].Nodes[{n_sink}] "
         f"t{zs_t} = {sink_live.get(zs_t)}")
    zdz_wire = 0
    if zdz_ct is None or n_src is None:
        fact(f"S3-zdz NOT ATTEMPTED — the ControlTerminal is {'unresolved' if zdz_ct is None else f'#{zdz_ct}'} "
             f"and its node index on Diagram[{frame_now}] is {n_src}. `OpConnectNested_v1` addresses "
             f"Diagram[].Nodes[].Terminals[] (build_opconnectnested_v1.py:418-420), so a ControlTerminal that "
             f"does not appear in that diagram's Nodes[] has no by-index route. MEASURED, not inferred.")
    elif n_sink is None:
        fact(f"S3-zdz NOT ATTEMPTED — #{zs_uid} is not on Diagram[{b12}] (1.2's body) after the moves")
    else:
        s_nm, s_is_src, s_w = sink_live.get(zs_t, ("<no such terminal>", None, None))
        src_t = next((i for i, (_n, isrc, _w) in src_live.items() if isrc), 0 if src_live else None)
        if s_is_src is not False or s_w != 0:
            fact(f"S3-zdz SINK RULE REFUSES the write: t{zs_t} {s_nm!r} is_source={s_is_src} wire={s_w} — a "
                 f"source or an occupied terminal is never a sink (route-B frontmatter)")
        elif src_t is None:
            fact(f"S3-zdz the ControlTerminal #{zdz_ct} reports NO terminals at all on Diagram[{frame_now}] — "
                 f"nothing to take as the wire source")
        else:
            dwz, esz, errz = CONNECT_V1(TARGET, b12, n_sink, zs_t, frame_now, n_src, src_t, V1_LABELS)
            wmap(TARGET, b12, fresh=True)
            zdz_wire = terms_of(TARGET, b12, zs_uid).get(zs_t, (None, None, 0))[2]
            fact(f"S3-zdz OpConnectNested_v1 D[{frame_now}].N[{n_src}].T[{src_t}] -> D[{b12}].N[{n_sink}]."
                 f"T[{zs_t}]: wire 0 -> {zdz_wire}, delta {dwz}, ExecState {esz} (COLD, so UNREAD as a "
                 f"verdict), err {str(errz)[:80]!r}")
    # ---- J3 (cycle-39 judgement, disposing `archive/peer/2026-09-19-routeb-run6-regression.md`). THE GATE THAT
    # STOOD HERE IS RETIRED. Its exact text was:
    #     gate("S3-zdz 'Z/dZ' -> #2222 t0 is wired BEFORE the #403 reparent (cycle15 Pre-decided 3)",
    #          bool(zdz_wire), f"sink wire {zdz_wire}")
    # It FAILED in runs 4, 5 and 6, and in run 6 the row it guards SUCCEEDED (`build_d1_routeb_v3_run6.log:408`).
    # It asserts the ORDERING of the REORDER route - wire `Z/dZ` BEFORE the `#403` reparent - which
    # `docs/cycle27-plan.md` Pre-decided 13a RETIRED in favour of the temporary-sink path, and that path wires
    # `Z/dZ` AFTER the reparent by design. A gate that must fail whenever the chosen route is taken measures the
    # route, not the build. The reading itself is still taken and RECORDED; what replaces the assertion is the
    # J2 gate, evaluated on the machine AFTER the temp-sink bracket.
    fact(f"S3-zdz PRE-REPARENT state RECORDED, NOT GATED (J3): #{ZDZ_SINK[0]} t{ZDZ_SINK[1]} carries wire "
         f"{zdz_wire} before the #{zdz_ct} reparent. Under Pre-decided 13a this row runs through the TEMPORARY "
         f"SINK, which wires it AFTER the reparent, so a non-zero reading here is not required and a zero one is "
         f"not a failure. The verification of this row is the J2 gate after the temp-sink bracket.")
    PREWIRED[ZDZ_SINK] = dict(before_reparent=zdz_wire, ct=zdz_ct)

    ct_before = g.count(TARGET, "ControlTerminal")
    ct_moved = set()
    for lbl, u in ct_uids.items():
        body_uid, loop_uid = loops["1.2"]["body"], loops["1.2"]["loop"]
        try:
            move_in(TARGET, u, diag_index(TARGET, body_uid), (60, y))
            y += 130
            _oc, ou = owner_of(TARGET, u)
            _oc2, ou2 = owner_of(TARGET, ou) if ou else (None, None)
            ok = ou == body_uid and ou2 == loop_uid
            if ok:
                ct_moved.add(lbl)
            gate(f"S3-ct ControlTerminal #{u} ({lbl!r}) -> 1.2", ok,
                 f"owner Diagram#{ou} (want {body_uid}), owner(owner) #{ou2} (want {loop_uid})")
        except Exception as e:
            gate(f"S3-ct ControlTerminal #{u} ({lbl!r}) -> 1.2", False, f"{str(e)[:140]}")
    gate("S3-ct ControlTerminal count unchanged by the reparent (moved, not destroyed)",
         g.count(TARGET, "ControlTerminal") == ct_before, f"{ct_before} -> {g.count(TARGET, 'ControlTerminal')}")
    # v1 / B2: DID THE REPARENT SURVIVE? A `GObject.Move` CUTS the moved object's wires (measured,
    # probe_move_ctlterm_v0), so this is the one thing the reorder cannot be assumed to have bought. Measured,
    # never assumed; if it is 0 the row falls back into S3w's ledger and is retried there with the SAME op.
    b12_after = diag_index(TARGET, loops["1.2"]["body"])
    wmap(TARGET, b12_after, fresh=True)
    zdz_after = terms_of(TARGET, b12_after, ZDZ_SINK[0]).get(ZDZ_SINK[1], (None, None, 0))[2]
    PREWIRED[ZDZ_SINK]["after_reparent"] = zdz_after
    fact(f"S3-zdz AFTER the #{PREWIRED[ZDZ_SINK]['ct']} reparent, #{ZDZ_SINK[0]} t{ZDZ_SINK[1]} carries wire "
         f"{zdz_after} (was {PREWIRED[ZDZ_SINK]['before_reparent']} before it). Non-zero = the reorder held and "
         f"this terminal never enters the S3w ledger; 0 = the move cut it and S3w retries.")
    gate("S3a the moves destroyed no frame diagram",
         g.count(TARGET, "Diagram") == BEFORE["Diagram"] + 3, f"Diagram {g.count(TARGET, 'Diagram')}")
    gate("S3 Local still 8 (route B §6 R7)", g.count(TARGET, "Local") == BEFORE["Local"],
         f"Local {g.count(TARGET, 'Local')}")

    # --- the AFTER census and the diff
    after_terms = {}
    for row, uids in MOVE_TABLE.items():
        if not uids:
            continue
        bi = diag_index(TARGET, loops[row]["body"])
        wmap(TARGET, bi, fresh=True)
        for uid in uids:
            after_terms[uid] = terms_of(TARGET, bi, uid)
    frame_i = diag_index(TARGET, FRAME_BODY_UID)
    wmap(TARGET, frame_i, fresh=True)
    for uid in neighbours:
        after_terms[uid] = terms_of(TARGET, frame_i, uid)
    outer_i = diag_index(TARGET, SIBLING_DIAG_UID)
    wmap(TARGET, outer_i, fresh=True)
    outer_cut = []
    for uid, before in before_outer.items():
        after = terms_of(TARGET, outer_i, uid)
        for i, (nm, src, w) in before.items():
            if w and (i not in after or not after[i][2]):
                outer_cut.append((uid, i, nm, src, w))
    # #637 itself legitimately loses outside terminals: its tunnels die with the wires the moves cut.
    d19_other = [r for r in outer_cut if r[0] != FRAME_LOOP_UID]
    gate("S3b-d19 no node on diagram 19 OTHER THAN #637 lost a wire (A1: #7202 Global motor pos.vi lives here)",
         not d19_other, f"{d19_other}")
    fact(f"S3b-d19 #637's own outside terminals that lost their wire: "
         f"{len([r for r in outer_cut if r[0] == FRAME_LOOP_UID])} (EXPECTED - a tunnel dies with its inner wire)")
    after_sr = sr_census(TARGET, [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(FRAME_LOOP_UID))
    sr_changed = [k for k in before_sr if after_sr.get(k) != before_sr[k]]
    fact(f"S3b-sr shift registers of #637 whose wiring changed: {sr_changed}")

    cut = list(deleted_cut)
    for uid, before in before_terms.items():
        after = after_terms.get(uid, {})
        for i, (nm, src, w) in before.items():
            if w and (i not in after or not after[i][2]):
                cut.append((uid, i, nm, src, w))
    for r in cut:
        tag = ("deleted" if r[0] in {u for u, _p, _l in FRESH.values()}
               else "STAYED-BUT-BARED" if r[0] in neighbours else "moved")
        print(f"      cut  #{r[0]} t{r[1]} {r[2]!r} {'OUT' if r[3] else 'IN'} was w{r[4]}  [{tag}]", flush=True)
    fact(f"S3b census diff: {len(cut)} terminals to re-connect "
         f"({len(deleted_cut)} from the three deleted subVIs + {len(cut) - len(deleted_cut)} from the moves)")
    cut_wires = {r[4] for r in cut}
    missing = [w for w in EXPECTED_CROSSINGS if w not in cut_wires]
    gate("S3b the cut set covers plan §8's 13 wired crossings", not missing, f"not cut: {missing}")
    staying = [u for u in neighbours if u not in {u2 for u2, _p, _l in FRESH.values()}]
    collateral = [r for r in cut if r[0] in staying]
    gate("S3b-collateral no STAYING node was bared by a move", not collateral, f"{collateral}")
    return dict(cut=cut, neighbours=neighbours, t637=t637, by_wire637=by_wire637, n637=n637,
                outer_cut=outer_cut, sr_changed=sr_changed, ct_moved=ct_moved)


# ============================================================================== S3c
def s3c(loops):
    print("\n=== S3c: 8 shift registers (4 on 1.2, 2 on 1.5, 2 on 1.7)", flush=True)
    panel_before = g.panel_wiring(TARGET)
    made = []
    for row, regs in D1.SHIFT_REGS.items():
        loop_uids = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")]
        li = loop_uids.index(loops[row]["loop"])
        seen = g.loop_cast(TARGET, li, class_name="WhileLoop")
        gate(f"S3c index {li} really is {row}'s WhileLoop #{loops[row]['loop']}",
             seen["loop_uid"] == loops[row]["loop"] and not seen["errors"],
             f"loop_cast({li}) -> {seen['loop_uid']}, errors {seen['errors']}", fatal=True)
        for (right, left, name) in regs:
            uid = g.add_shift_reg(TARGET, li, y_position=120 + 60 * len(made), class_name="WhileLoop")
            made.append((row, uid, name, right, left))
            fact(f"{row}: shift register #{uid} for {name!r} (was #{right}/#{left})")
    # ---- v1 / B1: the TWO registers that MOVE WITH THEIR NODES (cycle15 Pre-decided 2). Created AFTER the four
    # of D1.SHIFT_REGS on the same loop, so on 1.2 they are reg[4] and reg[5]; `sr_moved()` verifies that by uid
    # with `shift_reg_left` before it writes anything.
    for row, recs in SR_MOVED.items():
        loop_uids = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")]
        li = loop_uids.index(loops[row]["loop"])
        for (right, left, name, reader, writer, _imode, initial) in recs:
            uid = g.add_shift_reg(TARGET, li, y_position=120 + 60 * len(made), class_name="WhileLoop")
            made.append((row, uid, name, right, left))
            fact(f"{row}: shift register #{uid} MOVED WITH ITS NODES for {name} (was right #{right} / left "
                 f"#{left} on #{FRAME_LOOP_UID}); reader #{reader[0]} t{reader[1]}, writer #{writer[0]} "
                 f"t{writer[1]}; the original's initial value {initial} is NOT wired here — v0 wires no initial "
                 f"value for any of its 8 registers either (reported, not silently changed)")
    gate("S3c 10 shift registers created (8 of D1.SHIFT_REGS + 2 MOVED, v1/B1)", len(made) == 10, f"{len(made)}")
    gate("S3c ControlTerminal still 114", g.count(TARGET, "ControlTerminal") == BEFORE["ControlTerminal"],
         f"{g.count(TARGET, 'ControlTerminal')}")
    return panel_before, made


# ============================================================================== F0 / S3w — THE LEDGER
def s3w(loops, regs, r3, fresh_uid):
    print("\n=== F0: the re-wire source map, completed inside the build (§11j.2)", flush=True)
    payload = MAP.build_map(r3["cut"])
    with open(os.path.join(BENCH, "d1_routeb_rewire_sources.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
    fact(f"F0 source map: {payload['resolved']}/{payload['cut_terminals']} resolved, "
         f"by action {payload['by_action']}")
    gate("F0 every cut terminal has a resolved source", payload["unresolved"] == 0,
         f"unresolved {payload['unresolved']}")

    ACTIONS = ("same-loop", "from-kernel", "from-const", "from-sr", "to-sr", "from-ctl", "from-tunnel")
    rows = [r for r in payload["rows"] if r["action"].split(":")[0] in ACTIONS]
    fact(f"S3w rows to connect: {len(rows)} (the other {payload['cut_terminals'] - len(rows)} are source-side, "
         f"from-stay or cross-loop = queue endpoints)")

    ci = class_index(TARGET)
    done, failed, noroute, sinkrule, retarget_ok = [], [], [], [], []
    # ---- K3(b) (cycle-39 judgement, disposing `archive/peer/2026-09-19-routeb-run7-index-shift.md` Q4).
    # THE LEDGER'S `WIRED` COUNT IS A MIXTURE, and its weakest members meant only "the call returned without
    # raising": `wire_sr` and plain `wire` rows recorded NO uid and NO readback at all. Every WIRED row now
    # registers the wire uid it claims, and the SURVIVAL CENSUS printed right after the PRE-SETTLE ledger line
    # tests those uids against the machine's own `report_all(TARGET,'Wire')`. One traverse, no new op; the
    # pattern is route A's (`tools/recipes/build_d1_v0.py:1115-1128`), which route B had dropped.
    ledger_wires = []                                    # [(tag, kind, wire_uid)] - only non-zero, machine-read

    def claim_wire(tag, kind, uid):
        """Register a wire uid this row CLAIMS to have made/kept. Never raises: a census is instrumentation."""
        try:
            u = int(uid)
        except (TypeError, ValueError):
            return
        if u:
            ledger_wires.append((tag, kind, u))
    reg_by_row = {}
    for row, uid, name, right, left in regs:
        reg_by_row.setdefault(row, []).append((uid, name, right, left))
    # route B: the three deleted subVIs are re-dropped, so every row naming one is re-targeted to the fresh uid.
    RETARGET = dict(fresh_uid)
    # ⚠️ RUN 1 MEASURED (`tools/bench/build_d1_routeb_v0.log:373-382`): TEN of the fifteen NO-ROUTE rows were this
    # one caller bug. `tools/bench/d1_rewire_map.py:41-45` gives a row a destination loop only when its uid is in
    # that file's own MOVE table; `#5058` is NOT (it is the `KERNEL` constant at `:46`, classified only as a
    # SOURCE, action `from-kernel`, `:184-185`). So every row where `#5058` is the SINK came back `dest=None`,
    # `sink_addr` searched only the frame body and diagram 19, and the fresh kernel is on neither - it is inside
    # 1.2. `#48` and `#376` ARE in that table and every one of their rows wired. The destination of a deleted-and-
    # re-dropped subVI is not a guess: it is where S2d put it, which is `FRESH`'s own key.
    DEST_FALLBACK = {old: row for row, (old, _p, _l) in FRESH.items()}

    _TUNNEL_OUT = {}

    def tunnel_out_wire(tuid):
        """{LoopTunnel uid -> its OUTER wire}, built once by walking `gscript.tunnels()` (`gscript.py:887`).
        ADDED after `archive/peer/2026-09-17-routeb-run1-noroute-codex.md` point 2: matching #637's outside
        terminals BY WIRE UID is ambiguous when a net fans out to two tunnels, and `Is Source? FALSE` only says
        "a sink", not "the intended tunnel". `d1_tunnel_sources.json` carries the TUNNEL's own uid, so the source
        is resolved by IDENTITY instead of by value. One pass over the VI's LoopTunnels, cached."""
        if not _TUNNEL_OUT:
            n = g.count(TARGET, "LoopTunnel")
            for i in range(n):
                try:
                    t = g.tunnels(TARGET, i)
                except Exception:
                    continue
                if t.get("uid"):
                    _TUNNEL_OUT[t["uid"]] = t.get("out_wire") or 0
            fact(f"S3w LoopTunnel identity map built: {len(_TUNNEL_OUT)} of {n} tunnels read "
                 f"(uid -> outer wire; used instead of matching #637's terminals by wire value)")
        return _TUNNEL_OUT.get(int(tuid))

    def sink_addr(dest, sink_uid, sink_t, sink_name):
        """(body diagram index, node index, terminal index) for a sink, re-resolved NOW. Where the sink carries
        a NAME the terminal index is taken from the live census by name, because an index cached from the
        original is exactly the drift `archive/peer/2026-09-17-rbw-deleted-wires-run9.md` point 3 names."""
        u = RETARGET.get(sink_uid, sink_uid)
        # `dest` is None for a sink that STAYS where it is - a node bared by S1d's deletes (#6384's error chain,
        # #12589 t1) rather than by a move. `d1_rewire_map` only assigns a destination to the MOVERS, so the
        # diagram is searched instead of assumed: the frame body first, then the diagram that holds the loops.
        cands = ([diag_index(TARGET, loops[dest]["body"])] if dest else
                 [diag_index(TARGET, FRAME_BODY_UID), diag_index(TARGET, SIBLING_DIAG_UID)])
        d = n = None
        for cand in cands:
            n = node_index_on(cand, u, fresh=True)
            if n is not None:
                d = cand
                break
        if n is None:
            return None, None, None, None
        live = g.node_terms(TARGET, d, n)
        # PREFER THE MEASURED INDEX. `tools/bench/diag_moved_structure_terminals.log` (39/0, 2026-09-17) measured
        # that a `GObject.Move` of all five structures left `Wire 1902 -> 1902`, `LoopTunnel 132 -> 132` and every
        # terminal name at its own index - the index SURVIVES a move. What does NOT survive is a wire DELETE plus
        # Remove Bad Wires, which removes the tunnel and drops every higher index by one (`[5979, 5637, 0]`).
        # The name is therefore only a FALLBACK, and only when it is UNIQUE: the same log shows `#5540` carrying
        # `'Bead is good? array out'` on BOTH t2 and t3, and after a move every terminal of a moved structure
        # reads `is_source` FALSE - including its OUTPUT tunnels - so a name+is_source lookup can land on either.
        t = sink_t
        if sink_name and not any(r["i"] == sink_t for r in live):
            m = [r["i"] for r in live if r["name"] == sink_name and not r["is_source"]]
            if len(m) == 1:
                t = m[0]
        return d, n, t, {r["i"]: (r["name"], r["is_source"], r["wire"]) for r in live}

    def v1_connect(tag, dest, sink_uid, sink_t, sink_name, src_uid, src_t, src_where, why):
        d, n, t, _live = sink_addr(dest, sink_uid, sink_t, sink_name)
        su = RETARGET.get(src_uid, src_uid)
        if src_where == "outer":
            src_cands = [diag_index(TARGET, SIBLING_DIAG_UID)]
        elif src_where in loops:
            src_cands = [diag_index(TARGET, loops[src_where]["body"])]
        else:
            src_cands = [diag_index(TARGET, FRAME_BODY_UID), diag_index(TARGET, SIBLING_DIAG_UID)]
        src_d = src_n = None
        for cand in src_cands:
            src_n = node_index_on(cand, su, fresh=True)
            if src_n is not None:
                src_d = cand
                break
        if n is None or src_n is None:
            noroute.append((tag, f"{why}: sink node index {n} / source node index {src_n}"))
            return False
        dw, es, err = CONNECT_V1(TARGET, d, n, t, src_d, src_n, src_t, V1_LABELS)
        wire = next((r["wire"] for r in g.node_terms(TARGET, d, n) if r["i"] == t), 0)
        if wire:
            claim_wire(tag, "v1_connect", wire)                    # K3(b)
            done.append((tag, f"OpConnectNested_v1 D[{src_d}].N[{src_n}].T[{src_t}] -> D[{d}].N[{n}].T[{t}] "
                              f"wire {wire} (delta {dw}, ExecState {es}) [{why}]"))
            return True
        failed.append((tag, f"OpConnectNested_v1 left the sink BARE (delta {dw}, ExecState {es}, "
                            f"err {str(err)!r}) [{why}]"))                        # J4: full message
        return False

    def create_equal(diagram_index, location):
        """One bare `Equal?` on a nested diagram, via the op the freeze lift already closed at (`OpCreateEqual_v0`,
        23/0, `tools/recipes/build_opsentinel_ops.py:133`). NO NEW OP. Returns the new Comparison uid.
        ⚠️ The op's documented use wires x and y from a source node's named outputs (`:96`); calling it with an
        EMPTY name list is unmeasured, which is why the caller reports the exception verbatim instead of
        retrying."""
        before = set(g.uids(TARGET, "Comparison"))
        err = SENT.create_node("equal", EQUAL_LABELS, TARGET, diagram_index, location,
                               src_cls="Comparison", src_index=0, src_names=())
        new = [u for u in g.uids(TARGET, "Comparison") if u not in before]
        # J1: this is the COMMON creation helper, so the cached walk of the diagram just mutated is dropped HERE,
        # on every path - including the failure path, where the op may still have placed a node before erroring.
        _k, _hit = wmap_invalidate(diagram_index)
        fact(f"J1 create_equal: cached wire map for Diagram[{diagram_index}] INVALIDATED after the create "
             f"(cache hit dropped: {_hit}); new Comparison uids {new}, err {str(err)[:120]!r}")
        if err or len(new) != 1:
            raise RuntimeError(f"create_equal: err {err!r}, new {new}")
        return new[0]

    # ============================ THE TWO JUDGEMENT DECISIONS OF 2026-09-17 (session brief, route B (3)) =====
    # (1) `#1359` t1 and `#29874` t3: TWO LOCK-STEPPED QUEUES. Their source is a `LeftShiftRegister` of `#637`
    #     that STAYS on 1.1 (MEASURED, `tools/bench/d1_tunnel_sources.json`: the source terminal of w9097 /
    #     w28039 is owned by LeftShiftRegister #9025 / #29512), while both sinks move into 1.2. Two sibling loops
    #     cannot be wired directly, so the value crosses through a queue enqueued in 1.1 each iteration with the
    #     frame and dequeued in 1.2 in the same iteration as Q_work - `docs/stage2-assembly-step-c.md`'s paired
    #     producer/consumer shape, which step C measured at 162/162 in replay.
    # RULE 1a, THE PART THAT IS EASY TO GET WRONG: what `#1359` t1 consumed is the LEFT register's OUTPUT - the
    # PREVIOUS iteration's value. Enqueueing from the node that WRITES the right register would advance it by one
    # iteration and change the computation while every structural gate stayed green. So the enqueue's `element`
    # is branched off the LEFT register's own inside wire with `OpConnectFromWire_v0`, and the node that writes
    # the right register is used ONLY as the queue's TYPE source (a type carries no value).
    SR_FACTS_PATH = os.path.join(BENCH, "sr_transport.json")
    SR_ROWS = {(1359, 1): "Q_sr1", (29874, 3): "Q_sr2"}
    _SR_FACTS = {}
    _SR_MADE = {}

    def sr_facts():
        if not _SR_FACTS:
            try:
                with open(SR_FACTS_PATH, encoding="utf-8") as f:
                    _SR_FACTS.update(json.load(f))
            except Exception as e:
                _SR_FACTS["error"] = str(e)[:120]
        return _SR_FACTS

    def sr_queue(tag, dest, sink_uid, sink_t, sink_name, qname):
        """One lock-stepped queue for one LeftShiftRegister row. Returns True only if the sink ends up WIRED.

        Every address is re-read live; the only thing taken from `sr_transport.json` is (a) which LEFT register
        feeds this sink and (b) which NAMED node output carries its TYPE. Both were measured read-only on a
        pristine copy by `tools/bench/diag_sr_transport.py` in the same runner.
        """
        f = sr_facts()
        if f.get("error"):
            noroute.append((tag, f"sr_transport.json unreadable ({f['error']}) - run "
                                 f"tools/bench/diag_sr_transport.py first"))
            return False
        rec = next((v for v in (f.get("regs") or {}).values()
                    if tuple(v.get("sink") or ()) == (sink_uid, sink_t)), None)
        ts = (rec or {}).get("type_source")
        if not rec or not ts or not ts.get("traverse") or not ts.get("term_name"):
            noroute.append((tag, f"no measured TYPE SOURCE for {qname}: sr_transport.json rec="
                                 f"{json.dumps(rec)[:200] if rec else None}. `queue_node('obtain', …)` types the "
                                 f"queue from a NAMED node output (gscript.py:1068-1074) and this build refuses "
                                 f"to guess one"))
            return False
        d686 = diag_index(TARGET, SIBLING_DIAG_UID)
        d43 = diag_index(TARGET, FRAME_BODY_UID)
        d12 = diag_index(TARGET, loops["1.2"]["body"])
        tcls, tidx = ts["traverse"]
        try:
            # --- the LEFT register's inside wire, RE-READ NOW (never the value cached in the json) -------------
            loop_i = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(FRAME_LOOP_UID)
            live = g.shift_reg_left(TARGET, loop_i, rec["reg_index"], 0, "WhileLoop")
            lt = live.get("left") or {}
            if (lt.get("uid")) != rec["left_uid"]:
                noroute.append((tag, f"{qname}: reg[{rec['reg_index']}]'s LEFT register is now "
                                     f"#{lt.get('uid')}, was #{rec['left_uid']} - the register index drifted, "
                                     f"so the branch would be taken from the wrong net"))
                return False
            w_sr = next((t.get("wire") for t in (lt.get("inside") or []) if t.get("wire")), 0)
            if not w_sr:
                noroute.append((tag, f"{qname}: LEFT #{lt.get('uid')} has no inside wire now "
                                     f"(was w{rec['left_inside']}) - nothing to branch from"))
                return False
            srcs = [x for x in wire_source_owner(TARGET, w_sr)
                    if x.get("is_source") and x.get("recip") == w_sr]
            if len(srcs) != 1:
                noroute.append((tag, f"{qname}: w{w_sr} has {len(srcs)} source terminals, not 1"))
                return False
            # --- Obtain on Diagram #686, OUTSIDE both loops ---------------------------------------------------
            ob = g.queue_node("obtain", TARGET, tcls, tidx, ts["term_name"], d686,
                              (2400, 120 + 90 * len(_SR_MADE)))
            fns = [o["uid"] for o in g.report_all(TARGET, "Function")]
            ob_i = fns.index(ob[0])
            fact(f"S3w {qname}: Obtain placed on Diagram[{d686}] uid {ob[0]}, element type from "
                 f"{tcls}[{tidx}].{ts['term_name']!r} (the node that writes the PARTNER RIGHT register - a TYPE "
                 f"source only, no value is taken from it)")
            # --- Enqueue inside 1.1's body; the tunnel is auto-created (NAMES.md:762) -------------------------
            enq = g.queue_node("enqueue", TARGET, "Function", ob_i, "queue out", d43,
                               (2200, 160 + 90 * len(_SR_MADE)))
            # `queue_node` returns EVERY new Function uid, and placing a node inside a loop can create more than
            # the primitive itself (NAMES.md:762 - the refnum tunnel is auto-created). So the Enqueue is
            # identified by the terminal it must have, not by position in that list.
            en_i = el = enq_uid = None
            for u in enq:
                i = node_index_on(d43, u, fresh=True)
                if i is None:
                    continue
                t_el = next((x["i"] for x in g.node_terms(TARGET, d43, i)
                             if x["name"] == "element" and not x["is_source"]), None)
                if t_el is not None:
                    en_i, el, enq_uid = i, t_el, u
                    break
            if el is None:
                noroute.append((tag, f"{qname}: none of the new nodes {enq} on Diagram[{d43}] has a bare "
                                     f"'element' input - the Enqueue was not identified"))
                return False
            dw, es, err, sub = CONNECT_FROM_WIRE(TARGET, w_sr, srcs[0]["i"], d43, en_i, el, CFW_LABELS)
            got = next((x["wire"] for x in g.node_terms(TARGET, d43, en_i) if x["i"] == el), 0)
            if not got or sub.get("Is Broken?") is not False:
                failed.append((tag, f"{qname}: enqueue element branch from w{w_sr} -> wire {got}, "
                                    f"Is Broken? {sub.get('Is Broken?')!r}, delta {dw}, ExecState {es}, "
                                    f"err {str(err)[:60]!r}"))
                return False
            fact(f"S3w {qname}: Enqueue.element <- branch of the LEFT register's own wire w{w_sr} "
                 f"(source terminal {srcs[0]['i']}, owner {srcs[0].get('owner_class')}#"
                 f"{srcs[0].get('owner_uid')}) -> wire {got}, Is Broken? False")
            # --- Dequeue inside 1.2's body, then element -> the sink by INDEX --------------------------------
            deq = g.queue_node("dequeue", TARGET, "Function", ob_i, "queue out", d12,
                               (200, 160 + 90 * len(_SR_MADE)))
            dq_i = de = deq_uid = None
            for u in deq:
                i = node_index_on(d12, u, fresh=True)
                if i is None:
                    continue
                t_el = next((x["i"] for x in g.node_terms(TARGET, d12, i)
                             if x["name"] == "element" and x["is_source"]), None)
                if t_el is not None:
                    dq_i, de, deq_uid = i, t_el, u
                    break
            d, n, t, liveT = sink_addr(dest, sink_uid, sink_t, sink_name)
            if de is None or n is None:
                noroute.append((tag, f"{qname}: no new node in {deq} on Diagram[{d12}] has an 'element' OUTPUT "
                                     f"(Dequeue not identified), or the sink node index is {n}"))
                return False
            nm, is_src, w0 = liveT.get(t, ("<no such terminal>", None, None))
            if is_src is not False or w0 != 0:
                noroute.append((tag, f"{qname}: SINK RULE REFUSES t{t} {nm!r} is_source={is_src} wire={w0}"))
                return False
            dw2, es2, err2 = CONNECT_V1(TARGET, d, n, t, d12, dq_i, de, V1_LABELS)
            after = next((x["wire"] for x in g.node_terms(TARGET, d, n) if x["i"] == t), 0)
            # --- Release, outside both loops ------------------------------------------------------------------
            rel = g.queue_node("release", TARGET, "Function", ob_i, "queue out", d686,
                               (2600, 120 + 90 * len(_SR_MADE)))
            _SR_MADE[qname] = dict(obtain=ob[0], enqueue=enq_uid, dequeue=deq_uid, release=rel[0],
                                   type_source=f"{tcls}[{tidx}].{ts['term_name']}", left_wire=w_sr,
                                   sink_wire=after)
            if after:
                done.append((tag, f"{qname}: Obtain#{ob[0]} D[{d686}] | Enqueue#{enq_uid} D[{d43}] element<-w{w_sr}"
                                  f" | Dequeue#{deq_uid} D[{d12}].element -> D[{d}].N[{n}].T[{t}] wire {after} "
                                  f"(delta {dw2}, ExecState {es2}) | Release#{rel[0]}"))
                return True
            failed.append((tag, f"{qname}: Dequeue.element left the sink BARE (delta {dw2}, ExecState {es2}, "
                                f"err {str(err2)!r})"))                            # J4: full message
            return False
        except Exception as e:
            failed.append((tag, f"{qname}: {type(e).__name__}: {str(e)[:150]}"))
            return False

    # ======================== v1 / B1: THE REGISTERS MOVE WITH THEIR NODES (cycle15 Pre-decided 2) ============
    # The queue mechanism above is DEAD CODE from here on (`SR_QUEUE_AUTHORISED` is False permanently, cycle27
    # Pre-decided 13). What replaces it is the mechanism `docs/frame-loop-wire-graph.md:397` and
    # `archive/peer/2026-09-14-stage2-shiftreg-primitive.md:126-129` already decided: the loop-carried state
    # lives in exactly ONE loop, so the register itself is re-created on 1.2 and BOTH of its sides are wired -
    # the READ (left inside -> the sink) and the WRITE-BACK (the writer terminal -> right inside). The
    # write-back is the half v0 never re-connected at all: `#1359` t2 and `#29874` t5 are `source-side` rows,
    # which `d1_rewire_map` excludes from the ledger, so no row ever named them.
    _IMODE_PENDING = {}

    def sr_moved(tag, sink_uid, sink_t, sink_name):
        row, rec = SR_MOVED_ROWS[(sink_uid, sink_t)]
        right, left, name, reader, writer, imode, _initial = rec
        regs_here = reg_by_row.get(row, [])
        ridx = next((i for i, (_u, _nm, rr, _ll) in enumerate(regs_here) if rr == right), None)
        if ridx is None:
            noroute.append((tag, f"{name}: no shift register was created on {row} for right #{right}"))
            return False
        new_uid = regs_here[ridx][0]
        loop_i = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(loops[row]["loop"])
        # THE REGISTER INDEX IS VERIFIED BY UID, never trusted from creation order.
        try:
            liveR = g.shift_reg_left(TARGET, loop_i, ridx, 0, "WhileLoop")
        except Exception as e:
            noroute.append((tag, f"{name}: shift_reg_left(loop {loop_i}, reg {ridx}) raised "
                                 f"{type(e).__name__}: {str(e)[:100]} - the register is UNREAD, not absent"))
            return False
        if liveR.get("uid") != new_uid:
            noroute.append((tag, f"{name}: reg[{ridx}] of {row}'s loop is #{liveR.get('uid')}, not the "
                                 f"#{new_uid} add_shift_reg returned - the register index drifted"))
            return False
        bi = diag_index(TARGET, loops[row]["body"])
        wmap(TARGET, bi, fresh=True)
        t_live = terms_of(TARGET, bi, sink_uid)
        fact(f"S3w {name}: #{sink_uid} on Diagram[{bi}].Nodes[{node_index_on(bi, sink_uid)}], terminals "
             f"{sorted(t_live.items())}")
        # --- the WRITE-BACK first: an untyped register takes the type of its FIRST wire (gscript.py:668) ------
        w_uid, w_t = writer
        wn = node_index_on(bi, w_uid)
        wr_nm, wr_src, wr_w = terms_of(TARGET, bi, w_uid).get(w_t, ("<no such terminal>", None, None))
        if wn is None or wr_src is not True or wr_w:
            noroute.append((tag, f"{name}: the WRITE-BACK terminal #{w_uid} t{w_t} reads name {wr_nm!r} "
                                 f"is_source={wr_src} wire={wr_w} on Nodes[{wn}] - it must be a bare SOURCE "
                                 f"(docs/frame-loop-wire-graph.md:417/:421 measured it as the register's writer)"))
            return False
        try:
            g.wire_sr("RightIn", TARGET, loop_i, ridx, node_index=wn, term_index=w_t)
        except Exception as e:
            failed.append((tag, f"{name}: wire_sr RightIn reg[{ridx}] <- D[{bi}].N[{wn}].T[{w_t}] raised "
                                f"{type(e).__name__}: {str(e)[:120]}"))
            return False
        wmap(TARGET, bi, fresh=True)
        after_w = terms_of(TARGET, bi, w_uid).get(w_t, (None, None, 0))[2]
        # --- then the READ side, under the SINK RULE ----------------------------------------------------------
        nm2, is_src2, w0 = terms_of(TARGET, bi, sink_uid).get(sink_t, ("<no such terminal>", None, None))
        if is_src2 is not False or w0 != 0:
            noroute.append((tag, f"{name}: SINK RULE REFUSES t{sink_t} {nm2!r} is_source={is_src2} wire={w0} "
                                 f"(write-back already made: wire {after_w})"))
            return False
        n = node_index_on(bi, sink_uid)
        try:
            g.wire_sr("LeftIn", TARGET, loop_i, ridx, node_index=n, term_index=sink_t)
        except Exception as e:
            failed.append((tag, f"{name}: wire_sr LeftIn reg[{ridx}] -> D[{bi}].N[{n}].T[{sink_t}] raised "
                                f"{type(e).__name__}: {str(e)[:120]} (write-back wire {after_w})"))
            return False
        wmap(TARGET, bi, fresh=True)
        after_r = terms_of(TARGET, bi, sink_uid).get(sink_t, (None, None, 0))[2]
        if after_r:
            # IndexMode is settled in ONE LoopTunnel pass after the row loop - a per-row pass over ~132 tunnels
            # would cost more than the rest of the step. The tunnel is identified by the wire just created.
            _IMODE_PENDING[(sink_uid, sink_t)] = dict(wire=after_r, want=imode, name=name)
        if after_r and after_w:
            claim_wire(tag, "sr_moved.RightIn", after_w)           # K3(b)
            claim_wire(tag, "sr_moved.LeftIn", after_r)            # K3(b)
            done.append((tag, f"MOVED REGISTER reg[{ridx}] #{new_uid} on {row} ({name}): RightIn <- "
                              f"D[{bi}].N[{wn}].T[{w_t}] wire {after_w} | LeftIn -> D[{bi}].N[{n}].T[{sink_t}] "
                              f"wire {after_r}; initial value NOT wired (same as the other 8 registers)"))
            return True
        failed.append((tag, f"{name}: read wire {after_r}, write-back wire {after_w} - both must be non-zero"))
        return False

    def settle_index_modes():
        """cycle15 Pre-decided 2's "keep `index_mode 1` exactly as the original has it", in ONE pass over the
        VI's LoopTunnels. The tunnel is found by the wire `wire_sr` just put on the reader terminal; every
        reading that comes back beside an exception is printed UNREAD, never as a value."""
        if not _IMODE_PENDING:
            return
        want_wires = {v["wire"]: k for k, v in _IMODE_PENDING.items()}
        found = {}
        # RUN 5 instrumentation (cycle-36 judgement (c)): run 4 raised `error 2` (memory full) on the very next
        # line and NO handle reading bracketed it, while the SAME call succeeded at 51,284 handles at S1
        # (`build_d1_routeb_v1_run4.log:26-27`). This is the control that log did not have.
        fact(f"S3w handles IMMEDIATELY BEFORE g.count(TARGET, 'LoopTunnel') in settle_index_modes: "
             f"{labview_handles()} ({len(_IMODE_PENDING)} pending IndexMode rows)")
        n_tun = g.count(TARGET, "LoopTunnel")
        for i in range(n_tun):
            try:
                trec = g.tunnels(TARGET, i)
            except Exception:
                continue
            if not trec.get("uid"):
                continue
            ow = trec.get("out_wire") or 0
            if ow in want_wires:
                found.setdefault(want_wires[ow], []).append((i, trec.get("index_mode"), trec.get("uid")))
        for key, rec in _IMODE_PENDING.items():
            hits = found.get(key, [])
            if len(hits) != 1:
                fact(f"S3w IndexMode UNREAD for {rec['name']}: w{rec['wire']} matches {len(hits)} LoopTunnels "
                     f"{hits} out of {n_tun} - not a unique identification, so nothing was written")
                continue
            ti, im_before, tuid = hits[0]
            im_after = "UNREAD"
            try:
                if im_before != rec["want"]:
                    g.set_index_mode(TARGET, ti, rec["want"])
                im_after = g.tunnels(TARGET, ti).get("index_mode")
            except Exception as e:
                im_after = f"UNREAD ({type(e).__name__}: {e})"                     # J4: full message
            fact(f"S3w IndexMode {rec['name']}: LoopTunnel[{ti}] #{tuid} on w{rec['wire']} read {im_before}, "
                 f"want {rec['want']}, now {im_after} (cycle15 Pre-decided 2 - kept exactly as the original)")

    # (2) `#2222` t0 <- control `Z/dZ` (uid 47), UNNAMED sink. `wire_control` is name-addressed on BOTH ends, so
    #     it cannot reach an unnamed sink, and `OpConnectFromWire_v0` needs a WIRE to branch from. Decision: give
    #     the control a wire by wiring it to a TEMPORARY NAMED SINK, branch off that wire by index, then delete
    #     the temporary. If the control ALREADY drives a wire on this copy the temporary is skipped entirely -
    #     measured per run, never assumed (`tools/bench/diag_sr_transport.py` P4/P5 measured it on the pristine
    #     original; the copy is re-read here because the moves may have cut it).
    def from_ctl_unnamed(tag, dest, sink_uid, sink_t, sink_name, label):
        d, n, t, liveT = sink_addr(dest, sink_uid, sink_t, sink_name)
        if n is None:
            noroute.append((tag, f"{label!r}: sink #{sink_uid} is not on {dest}'s body diagram"))
            return False
        nm, is_src, w0 = liveT.get(t, ("<no such terminal>", None, None))
        if is_src is not False or w0 != 0:
            noroute.append((tag, f"{label!r}: SINK RULE REFUSES t{t} {nm!r} is_source={is_src} wire={w0}"))
            return False
        row = next((x for x in g.panel_wiring(TARGET) if x.get("label") == label), None)
        if not row:
            noroute.append((tag, f"{label!r} is not on the panel of this copy"))
            return False
        zw, temp, tmp_note = int(row.get("wire") or 0), None, "control already drives a wire"
        _wct_before = None                      # J2(b); set when the temp-sink bracket is actually opened
        # ---- v1 / B2 RETRY, same op, same decision (cycle15 Pre-decided 3). The reorder in S3 wired this
        # terminal BEFORE the reparent; a `GObject.Move` cuts wires, so if the sink is bare again BOTH ends are
        # now on 1.2's body and the identical by-index write is simply repeated there. No temporary sink, no
        # renaming, no new mechanism - which is the whole content of the decision.
        if not zw and (sink_uid, sink_t) == ZDZ_SINK and PREWIRED.get(ZDZ_SINK, {}).get("ct"):
            ct_uid = PREWIRED[ZDZ_SINK]["ct"]
            bi = diag_index(TARGET, loops["1.2"]["body"])
            wmap(TARGET, bi, fresh=True)
            n_src = node_index_on(bi, ct_uid)
            src_terms = terms_of(TARGET, bi, ct_uid)
            st = next((i for i, (_n, isrc, _w) in src_terms.items() if isrc), 0 if src_terms else None)
            if n_src is None or st is None:
                # LOGGED CONTROL ONLY (prior-art B4, cycle27 Pre-decided 13a). The RETRY no longer decides this
                # row: it records its NO-ROUTE reason as a MEASUREMENT (the same wording run 4 printed) and FALLS
                # THROUGH to the temporary-sink branch below. `noroute.append(...)` and `return False` are gone -
                # they made `TEMP_SINK_AUTHORISED` inert, because `node_index_on()` is None for every
                # ControlTerminal, so execution never reached the branch the flag controls.
                fact(f"S3w {label!r}: RETRY not possible - ControlTerminal #{ct_uid} is not in "
                     f"Diagram[{bi}].Nodes[] (index {n_src}, terminals {sorted(src_terms)}), "
                     f"and OpConnectNested_v1 addresses Diagram[].Nodes[].Terminals[] only "
                     f"[logged control only - falling through to the temporary sink]")
            else:
                n2 = node_index_on(bi, sink_uid)
                dwz, esz, errz = CONNECT_V1(TARGET, bi, n2, sink_t, bi, n_src, st, V1_LABELS)
                wmap(TARGET, bi, fresh=True)
                got = terms_of(TARGET, bi, sink_uid).get(sink_t, (None, None, 0))[2]
                fact(f"S3w {label!r} RETRY (v1/B2): OpConnectNested_v1 D[{bi}].N[{n_src}].T[{st}] -> "
                     f"D[{bi}].N[{n2}].T[{sink_t}] wire 0 -> {got}, delta {dwz}, ExecState {esz} (COLD, UNREAD), "
                     f"err {str(errz)!r}; S3 pre-wire was {PREWIRED[ZDZ_SINK].get('before_reparent')} and the "
                     f"reparent left {PREWIRED[ZDZ_SINK].get('after_reparent')}")
                PREWIRED[ZDZ_SINK]["retry"] = got
                if got:
                    claim_wire(tag, "from_ctl_unnamed.v1_retry", got)       # K3(b)
                    done.append((tag, f"OpConnectNested_v1 (v1/B2 retry after the #{ct_uid} reparent cut the S3 "
                                      f"pre-wire) D[{bi}].N[{n_src}].T[{st}] -> D[{bi}].N[{n2}].T[{sink_t}] "
                                      f"wire {got}"))
                    return True
                failed.append((tag, f"{label!r}: the by-index retry left the sink BARE (delta {dwz}, "
                                    f"ExecState {esz}, err {str(errz)!r})"))       # J4: full message
                return False
        if not zw and not TEMP_SINK_AUTHORISED:
            noroute.append((tag, f"{label!r} carries NO wire on this copy and the TEMPORARY-SINK branch is not "
                                 f"authorised (bare `Equal?` with src_names=() is UNMEASURED; the hazard is "
                                 f"SILENT, not the withdrawn 1055 modal - src_names=() -> Names=[] "
                                 f"(build_opsentinel_ops.py:397,:400) -> Get Outputs empty -> Index Array[0] "
                                 f"returns a default refnum with NO error, whose predicted signature is that "
                                 f"THE SINK STAYS BARE). MEASURED, reported, not guessed."))
            return False
        if not zw:
            # the temporary named sink: an `Equal?` primitive, whose inputs are named `x` / `y`. Built with the
            # op the freeze lift already closed at (`OpCreateEqual_v0`, 23/0) - no new op is introduced here.
            tdi = diag_index(TARGET, loops[dest]["body"])
            # ---- J2(b), OPENED HERE: the Wire count across the WHOLE temp-sink bracket (create -> wire_control
            # -> OpConnectFromWire_v0 -> delete + Remove Bad Wires) must come back UNCHANGED. Every write in the
            # bracket is a BRANCH off an existing net or the removal of the node that carried it, so the expected
            # delta is 0; a non-zero delta says a net was created or destroyed, which is what "the deletion
            # silently re-formed the net" would look like.
            # ⚠️ K2 (cycle-39 judgement, disposing the run-7 review): THE GATING READING IS NOW PER DIAGRAM.
            # v4's comment here claimed "this fleet has no per-diagram wire count at all"; the review REFUTED
            # that premise, and `diagram_wire_count()` above is the count, taken from the walker this recipe
            # already uses (NOT from `net_map`, which fires a VI-wide Remove Bad Wires of its own - see that
            # function's docstring). BOTH instruments are read and logged side by side so the two can be
            # compared once: `_wct_*` is the whole VI (`g.count`, a whole-VI Traverse, `tools/gscript.py:1005`),
            # `_wcd_*` is Diagram[tdi] alone. The GATE is the per-diagram delta; the VI-wide pair is reported.
            _wcd_before = diagram_wire_count(tdi, fresh=True)
            _wct_before = g.count(TARGET, "Wire")
            try:
                temp = create_equal(tdi, (400, 900))
            except Exception as e:
                noroute.append((tag, f"{label!r}: temporary named sink could not be created: {str(e)[:140]}. "
                                     f"`OpCreateEqual_v0` is documented to place an `Equal?` WIRED from a source "
                                     f"node's named outputs (build_opsentinel_ops.py:96); creating one with no "
                                     f"source is UNMEASURED and this is the measurement"))
                return False
            tmp_note = f"temporary Equal? #{temp} created as a named sink"
            _TEMP_SINK_USED.append((tag, label))
            # A2 READER (prior-art A2, cycle27 Pre-decided 13a): the hazard of `src_names=()` is SILENT, so it is
            # READ here rather than inferred - (i) the src_names actually passed, (ii) the created node's own
            # terminal census. No new op: `terms_of` is build_d1_v0's cached walk, re-taken fresh because the
            # node was just created.
            try:
                _tcen = terms_of(TARGET, tdi, temp, fresh=True)
            except Exception as e:
                _tcen = f"UNREAD ({type(e).__name__}: {e})"                        # J4: full message
            fact(f"S3w {label!r} A2 READER: create_equal called with src_names=() (SENT.create_node "
                 f"src_cls='Comparison', src_index=0, src_names=(), Diagram[{tdi}]); created Equal? #{temp} "
                 f"terminal census = {_tcen}. PREDICTED signature of the silent-default-refnum failure is a BARE "
                 f"sink, read by this row's own discriminator below.")
            # ---- P1 (cycle-38 judgement): THE TWO-INDEX RETRY, the SAME one the five sibling `from-ctl` rows
            # use at :1736-1753 of this file (citation corrected 2026-09-19 - prior-art F3 found `:1600-1617`
            # wrong, that range is the `from-const`/`from-sr` dispatch; `docs/d1-route-b-plan.md:599` cited
            # `:1567-1584`, also stale). Run 5 passed ONE fixed `src_diagram_index` - `diag_index(TARGET,
            # FRAME_BODY_UID)`, the STAY diagram - while S3-ct had ALREADY reparented this row's ControlTerminal
            # #403 onto 1.2's body (`build_d1_routeb_v2_run5.log:171`), and the temp sink itself is created on
            # 1.2's body (`:332`). `Get Controls.vi` was therefore asked for a control on a diagram the terminal
            # no longer lives on: error 5001 (`:402`). The order follows what S3-ct MEASURED (`r3['ct_moved']`),
            # and the other index is tried if the sink stays bare - VERIFIED BY EFFECT on the temp sink's OWN
            # `x` terminal wire, never on the call's return.
            ci.update(class_index(TARGET))
            tcls, tix = ci.get(temp, (None, None))

            def _x_term(cen):
                if not isinstance(cen, dict):
                    return None
                return next((i for i, (nm, isrc, _w) in cen.items() if nm == "x" and isrc is False), None)

            _tx = _x_term(_tcen)
            if _tx is None:
                try:
                    _tx = _x_term(terms_of(TARGET, tdi, temp, fresh=True))
                except Exception:
                    _tx = None
            sd_moved = diag_index(TARGET, loops["1.2"]["body"])
            sd_stay = diag_index(TARGET, FRAME_BODY_UID)
            reparented = label in (r3.get("ct_moved") or set())
            order = [sd_moved, sd_stay] if reparented else [sd_stay, sd_moved]
            tw, ttried = 0, []
            for sd in order:
                try:
                    g.wire_control(TARGET, [label], tcls, tix, ["x"], branch=True, src_diagram_index=sd)
                    try:
                        tw = (terms_of(TARGET, tdi, temp, fresh=True).get(_tx, (None, None, 0))[2]
                              if _tx is not None else 0)
                    except Exception as e2:
                        tw = 0
                        ttried.append((sd, f"sink re-read raised {type(e2).__name__}: {str(e2)[:50]}", 0))
                        continue
                    ttried.append((sd, "no error", tw))
                except Exception as e:
                    # J2(d) + J4: a raise is NOT a reading of the sink. The old line recorded the INITIALISER 0
                    # and truncated the message at 70 chars, so `sink wire 0 -> 0` claimed a measurement that was
                    # never taken. The sink is re-read FROM THE MACHINE here, and the full message is kept.
                    try:
                        tw = (terms_of(TARGET, tdi, temp, fresh=True).get(_tx, (None, None, 0))[2]
                              if _tx is not None else 0)
                        _rb = f"machine read after the raise: temp `x` wire {tw}"
                    except Exception as e3:
                        tw = 0
                        _rb = f"sink UNREAD after the raise ({type(e3).__name__}: {e3})"
                    ttried.append((sd, f"{e} || {_rb}", tw))
                if tw:
                    break
            try:
                row = next((x for x in g.panel_wiring(TARGET) if x.get("label") == label), None)
                zw = int((row or {}).get("wire") or 0)
            except Exception as e:
                row, zw = None, 0
                ttried.append(("panel_wiring", f"{type(e).__name__}: {str(e)[:60]}", 0))
            fact(f"S3w {label!r} P1 TWO-INDEX RETRY into the temporary sink: reparented={reparented}, "
                 f"1.2-body Diagram index {sd_moved}, frame-body Diagram index {sd_stay}, order {order}, "
                 f"temp `x` terminal index {_tx}; attempts (index, outcome, sink wire) = {ttried}; "
                 f"temp `x` wire {tw}; control panel wire {zw}; refs {g.ref_counts()}")
            if not tw and not zw:
                noroute.append((tag, f"{label!r}: wire_control left the temporary sink's `x` BARE on BOTH "
                                     f"diagram indices; attempts {ttried}"))
                return False
        if not zw:
            noroute.append((tag, f"{label!r}: still carries no wire after {tmp_note}"))
            return False
        # ---- P2, CORRECTED 2026-09-19 (cycle-38 judgement on prior-art F3 `already-measured`,
        # `archive/peer/2026-09-19-priorart-d1-routeb-run6.md`). P2 used to assert that `wire_source_owner` had
        # NEVER been measured with a ControlTerminal as the wire's source. THAT WAS FALSE, and the measurement is
        # this build's own: `tools/bench/diag_hierarchy_a3.log:106` and `:110` (2026-09-16) run `OpWireSource_v5`
        # on the wires of two of these six labels - 'Force\nsmoothing\nhalf-width' (w31059) and
        # 'Extension\nmedian filter\nhalf-width' (w31166) - and each returns EXACTLY ONE reciprocal source
        # terminal, `source=True owner 'Diagram' uid 639`. So a ControlTerminal source resolves as its OWNING
        # DIAGRAM (uid 639 is the frame body's diagram; `tools/bench/probe_move_ctlterm_v0.log:53`
        # `OBSERVED uid 403 -> owner 'Diagram' uid 639`, the Z/dZ terminal itself - NOT `:47`, which is uid 642,
        # a different control), and `len(srcs) == 1` below is the EXPECTED reading, not an unknown.
        # The census and the fall-through are KEPT anyway: the two measured wires were read on the UNTOUCHED
        # original, whereas here `#403` has been reparented and the sink lives on a temporary node, so the census
        # records the state the reading was taken in and a raise still becomes a RECORDED ledger row rather than
        # an exception that ends the run.
        _ct = (PREWIRED.get((sink_uid, sink_t)) or {}).get("ct")
        _cen = {"ct_uid": _ct, "owner_class": None, "owner_uid": None, "owner_diagram_index": None,
                "wire_on_control": zw}
        try:
            if _ct:
                _cen["owner_class"], _cen["owner_uid"] = owner_of(TARGET, _ct)
                try:
                    _cen["owner_diagram_index"] = diag_index(TARGET, _cen["owner_uid"])
                except Exception as e:
                    _cen["owner_diagram_index"] = f"<not a Diagram: {type(e).__name__}>"
        except Exception as e:
            _cen["owner_class"] = f"<owner_of raised {type(e).__name__}: {str(e)[:50]}>"
        fact(f"S3w {label!r} P2 ControlTerminal CENSUS before wire_source_owner(w{zw}): {_cen}; "
             f"1.2-body Diagram index {diag_index(TARGET, loops['1.2']['body'])}, frame-body Diagram index "
             f"{diag_index(TARGET, FRAME_BODY_UID)}; refs {g.ref_counts()}")
        try:
            _terms = wire_source_owner(TARGET, zw)
        except Exception as e:
            failed.append((tag, f"{label!r}: wire_source_owner(w{zw}) RAISED {type(e).__name__}: {str(e)[:110]} "
                                f"- a ControlTerminal source is ALREADY measured to return one source terminal "
                                f"owned by its Diagram (diag_hierarchy_a3.log:106,:110), so this raise is the "
                                f"reparent/temp-sink state, not the op; census {_cen}"))
            return False
        srcs = [x for x in _terms if x.get("is_source") and x.get("recip") == zw]
        fact(f"S3w {label!r} P2 wire_source_owner(w{zw}) returned {len(_terms)} terminal(s), "
             f"{len(srcs)} of them sources: {[{k: x.get(k) for k in ('i', 'is_source', 'owner_class', 'owner_uid')} for x in _terms][:6]}")
        if len(srcs) != 1:
            noroute.append((tag, f"{label!r}: w{zw} has {len(srcs)} source terminals, not 1"))
            return False
        dw, es, err, sub = CONNECT_FROM_WIRE(TARGET, zw, srcs[0]["i"], d, n, t, CFW_LABELS)
        after = next((x["wire"] for x in g.node_terms(TARGET, d, n) if x["i"] == t), 0)
        fact(f"S3w {label!r} -> #{sink_uid} t{t}: {tmp_note}; branched off w{zw} terminal {srcs[0]['i']} "
             f"(owner {srcs[0].get('owner_class')}#{srcs[0].get('owner_uid')}) -> wire {after}, "
             f"Is Broken? {sub.get('Is Broken?')!r}, delta {dw}, ExecState {es}, err {str(err)[:60]!r}")
        if temp is not None:
            # DELETE THE TEMPORARY, then RE-READ THE SINK. The branch and the temporary's own segment belong to
            # ONE net, so deleting the sink node can take the branch with it; that is exactly why the sink is
            # re-read AFTER the delete and the row is only counted WIRED if it still carries a wire.
            # ---- K1 (cycle-39 judgement, disposing `archive/peer/2026-09-19-routeb-run7-index-shift.md`):
            # THE MID-LOOP VI-WIDE `remove_bad_wires_scripted(TARGET)` THAT STOOD HERE IS DELETED, AND NOTHING
            # REPLACES IT. `VI.Block Diagram:Remove Bad Wires` is whole-VI by definition, and this restructure
            # deliberately leaves wires cut between S1d/S3 and this rewiring pass (`build_d1_routeb_v4_run7.log`
            # `:274-280` lists `#2222`'s own five cut input tunnels), so a VI-wide reaper INSIDE the row loop
            # destroys the build's own scaffolding - that is run 7's -96. Measured grounds: run 5 returned
            # NO-ROUTE at this function's `:1606-1609` and therefore NEVER REACHED this bracket, and in run 5
            # `#2222` t2/t3/t4/t5 ALL wired; runs 6 and 7 reached it and they failed. The temp node's only wire,
            # w29238, demonstrably SURVIVED the delete (`Is Broken? False`, sink read back 29238), so no targeted
            # cleanup is needed in its place. This moves the build TOWARD rule-1a preservation: it stops deleting
            # wires the ORIGINAL has. ONE LINE, and the discriminator's value depends on it staying one line.
            try:
                ids = [o["uid"] for o in g.report(TARGET, "Comparison")]
                if temp in ids:
                    g.delete_object(TARGET, "Comparison", ids.index(temp))
            except Exception as e:
                fact(f"S3w {label!r}: temporary Equal? #{temp} could not be deleted: {e} "
                     f"- it is a dead-but-legal node and is REPORTED, not hidden")
            # J1: the delete (and `Remove Bad Wires` behind it) mutates this diagram's `Nodes[]` index space, so
            # the cached walk is dropped HERE too - the second half of the bracket the run-6 review measured.
            _k2, _hit2 = wmap_invalidate(tdi)
            fact(f"J1 temp-sink delete: cached wire map for Diagram[{tdi}] INVALIDATED after the delete "
                 f"(cache hit dropped: {_hit2}). Every row addressed after this point re-walks the diagram.")
            d, n, t, liveT = sink_addr(dest, sink_uid, sink_t, sink_name)
            after = (next((x["wire"] for x in g.node_terms(TARGET, d, n) if x["i"] == t), 0)
                     if n is not None else 0)
            fact(f"S3w {label!r}: after deleting the temporary sink, #{sink_uid} t{t} carries wire {after}")
            # ================= J2: THE ROW'S VERIFICATION, AS A MEASUREMENT ==================================
            # (cycle-39 judgement, disposing `archive/peer/2026-09-19-routeb-run6-regression.md` Q-A.) Run 6's
            # whole verification of this row was: the temp node's `x` carried w29238, ONE source terminal on that
            # wire was owned by `Diagram#567`, `Is Broken? False`, and the id was still there after the delete.
            # The review's refutation stands: an owner of `Diagram#567` is a predicate ~30 objects on that
            # diagram satisfy, everything probative was read BEFORE the delete, and a wire uid is an allocation
            # slot, not an identity. So four readings are taken HERE, after the delete, and ANY wrong one FAILS
            # the row rather than letting it be counted WIRED.
            _j2 = {"d_sink_wire": after, "b_wire_count_vi_wide": (_wct_before, None, None),
                   "b_wire_count_diagram": (_wcd_before, None, None),
                   "c_is_broken": sub.get("Is Broken?"), "a_ct_uid_expected": _ct}
            try:
                _wct_after = g.count(TARGET, "Wire")
            except Exception as e:
                _wct_after = None
                _j2["b_err"] = f"{type(e).__name__}: {e}"
            _wdelta = ((_wct_after - _wct_before) if (_wct_after is not None and _wct_before is not None)
                       else None)
            _j2["b_wire_count_vi_wide"] = (_wct_before, _wct_after, _wdelta)
            # K2: the AFTER reading of Diagram[tdi]. No `fresh=True` is needed and none is paid: J1 dropped this
            # diagram's cached walk immediately after the delete (`wmap_invalidate(tdi)` above), so whatever map
            # is in the cache now was taken AFTER the delete by `sink_addr`; if none is, this walks once.
            try:
                _wcd_after = diagram_wire_count(tdi)
            except Exception as e:
                _wcd_after = None
                _j2["b_diag_err"] = f"{type(e).__name__}: {e}"
            _wddelta = ((_wcd_after - _wcd_before) if (_wcd_after is not None and _wcd_before is not None)
                        else None)
            _j2["b_wire_count_diagram"] = (_wcd_before, _wcd_after, _wddelta)
            try:
                _j2["a_src_terms_after"] = wire_source_owner(TARGET, after) if after else []
            except Exception as e:
                _j2["a_src_terms_after"] = f"UNREAD ({type(e).__name__}: {e})"
            try:
                _j2["a_ct_self_echo"] = owner_of(TARGET, _ct) if _ct else None
            except Exception as e:
                _j2["a_ct_self_echo"] = f"UNREAD ({type(e).__name__}: {e})"
            try:
                _prow = next((x for x in g.panel_wiring(TARGET) if x.get("label") == label), None)
                _j2["a_control_own_wire"] = int((_prow or {}).get("wire") or 0)
            except Exception as e:
                _j2["a_control_own_wire"] = f"UNREAD ({type(e).__name__}: {e})"
            _srcs_after = ([x for x in _j2["a_src_terms_after"]
                            if isinstance(x, dict) and x.get("is_source") and x.get("recip") == after]
                           if isinstance(_j2["a_src_terms_after"], list) else [])
            # (a) THE SOURCE IDENTITY. `OpWireSource_v5` reports a terminal's OWNER, never the terminal's own
            # uid (`tools/bench/opwiresource_v5_labels.json`: `uid_back`/`cls_back` echo the INPUT object), and a
            # ControlTerminal's terminal is measured to report its owning DIAGRAM (`diag_hierarchy_a3.log:106`,
            # `:110`). So the identity is closed from the OTHER end instead, which this fleet CAN read: the
            # control's OWN wire must equal the wire the sink now carries. That is the reciprocal the review
            # asked for ("`ControlTerminal#403`'s own wire equal to W"), and the self-echo below prints the
            # object's own class and uid so `#403` is named rather than assumed.
            _a_ok = (bool(after) and isinstance(_j2["a_control_own_wire"], int)
                     and _j2["a_control_own_wire"] == after and len(_srcs_after) == 1)
            _b_ok = (_wddelta == 0)                  # K2: the GATE is the PER-DIAGRAM delta
            _c_ok = (sub.get("Is Broken?") is False)
            _d_ok = bool(after)
            fact(f"S3w {label!r} J2 GATE READINGS (all taken AFTER the temporary sink was deleted): "
                 f"(a) source identity ok={_a_ok} - control's own wire {_j2['a_control_own_wire']} vs sink wire "
                 f"{after}, {len(_srcs_after)} reciprocal source terminal(s) on w{after}, ControlTerminal "
                 f"self-echo {_j2['a_ct_self_echo']}, terms {_j2['a_src_terms_after']}; "
                 f"(b) Wire count ok={_b_ok} - K2 PER-DIAGRAM Diagram[{tdi}] "
                 f"{_j2['b_wire_count_diagram']} (before, after, delta) IS THE GATE; VI-WIDE "
                 f"{_j2['b_wire_count_vi_wide']} (before, after, delta) is reported BESIDE it so the two "
                 f"instruments can be compared once; "
                 f"(c) Is Broken? ok={_c_ok} - {sub.get('Is Broken?')!r}; "
                 f"(d) sink wire read back from the machine ok={_d_ok} - {after}")
            if not (_a_ok and _b_ok and _c_ok and _d_ok):
                failed.append((tag, f"{label!r}: J2 GATE FAILED - a(source identity)={_a_ok}, "
                                    f"b(PER-DIAGRAM Wire delta 0)={_b_ok}, c(Is Broken? False)={_c_ok}, "
                                    f"d(sink wire read back)={_d_ok}; readings {_j2}"))
                return False
        if after and sub.get("Is Broken?") is not True:
            claim_wire(tag, "from_ctl_unnamed", after)              # K3(b)
            done.append((tag, f"OpConnectFromWire_v0 w{zw} -> D[{d}].N[{n}].T[{t}] wire {after} "
                              f"({tmp_note}, temporary deleted={temp is not None})"))
            return True
        failed.append((tag, f"{label!r}: sink wire {after}, Is Broken? {sub.get('Is Broken?')!r}"))
        return False

    def from_tunnel(tag, r, dest, sink_uid, sink_t, sink_name):
        """THE SINK RULE, mechanically. Source = the wire currently on `#637`'s outside terminal for this
        tunnel; sink = a terminal that must read `Is Source? FALSE` AND `wire 0` before anything is written."""
        ts = TUNNEL_SOURCES.get((sink_uid, sink_t))
        if not ts:
            noroute.append((tag, "not in d1_tunnel_sources.json - re-run diag_tunnelsource_onehop.py"))
            return False
        # NOTHING CACHED, AND ADDRESSED BY TUNNEL IDENTITY. Run 1 matched #637's outside terminals by WIRE UID
        # and refused on 2 hits for `w5812` / `w2731` (`build_d1_routeb_v0.log:383-384`). codex
        # (`archive/peer/2026-09-17-routeb-run1-noroute-codex.md` point 2) refuted the obvious repair: a net
        # legally fans out to two tunnels, and `Is Source? FALSE` says "a sink", not "THE intended tunnel" - an
        # arbitrary pick would be a type-correct, executable, WRONG wire that no gate here could see. So the
        # source comes from the TUNNEL's own uid, which `d1_tunnel_sources.json` already carries.
        # DECISION (1), 2026-09-17: the two LeftShiftRegister-fed rows are not a wire at all - they are a
        # cross-loop TRANSPORT, and they get their own lock-stepped queue. Taken BEFORE the tunnel lookup,
        # because `tunnel_out_wire` correctly finds nothing for them (a LeftShiftRegister is not a LoopTunnel)
        # and run 2 spent both of its NO-ROUTE rows saying so.
        if (sink_uid, sink_t) in SR_MOVED_ROWS:
            # v1 / B1: the decided mechanism. The queue branch below is unreachable and stays only so the
            # refusal remains readable next to what replaced it.
            return sr_moved(tag, sink_uid, sink_t, sink_name)
        if (sink_uid, sink_t) in SR_ROWS:
            if not SR_QUEUE_AUTHORISED:
                noroute.append((tag, "Q_sr1/Q_sr2 NOT AUTHORISED - see the RUN 3 block in this file's docstring; "
                                     "the mechanism is refuted by our own measurements and the decision is the "
                                     "judgement session's"))
                return False
            return sr_queue(tag, dest, sink_uid, sink_t, sink_name, SR_ROWS[(sink_uid, sink_t)])
        w_now = tunnel_out_wire(ts["tunnel_uid"])
        if not w_now:
            noroute.append((tag, f"LoopTunnel #{ts['tunnel_uid']} has no outer wire now "
                                 f"(present in the tunnel map: {int(ts['tunnel_uid']) in _TUNNEL_OUT}; "
                                 f"pristine outer was w{ts['outer_wire']}). Absent = the tunnel is not a "
                                 f"LoopTunnel at all - `d1_tunnel_sources.json` measured a LeftShiftRegister "
                                 f"source for #1359 t1 and #29874 t3, and route B §6 R1 keeps that register on "
                                 f"loop 1.1, which makes those rows a cross-loop TRANSPORT question, not a wire"))
            return False
        if w_now != ts["outer_wire"]:
            fact(f"S3w tunnel #{ts['tunnel_uid']}'s outer wire is w{w_now} now, was w{ts['outer_wire']} when "
                 f"d1_tunnel_sources.json was recorded - identity, not the value, decided this row")
        terms = wire_source_owner(TARGET, w_now)
        srcs = [x for x in terms if x.get("is_source") and x.get("recip") == w_now]
        if len(srcs) != 1:
            noroute.append((tag, f"w{w_now} has {len(srcs)} source terminals, not 1: "
                                 f"{[(x.get('owner_class'), x.get('owner_uid')) for x in srcs]}"))
            return False
        d, n, t, live = sink_addr(dest, sink_uid, sink_t, sink_name)
        if n is None:
            noroute.append((tag, f"sink #{RETARGET.get(sink_uid, sink_uid)} is not on {dest}'s body diagram"))
            return False
        nm, is_src, w0 = live.get(t, ("<no such terminal>", None, None))
        if is_src is not False or w0 != 0:
            sinkrule.append((tag, "REFUSED", f"t{t} {nm!r} is_source={is_src} wire={w0}"))
            noroute.append((tag, f"SINK RULE REFUSES the write: t{t} {nm!r} reads is_source={is_src}, "
                                 f"wire={w0} - a source or an occupied terminal is never a sink "
                                 f"(d1-route-b-plan.md frontmatter; STATUS OPEN 37)"))
            return False
        dw, es, err, sub = CONNECT_FROM_WIRE(TARGET, w_now, srcs[0]["i"], d, n, t, CFW_LABELS)
        after = next((x["wire"] for x in g.node_terms(TARGET, d, n) if x["i"] == t), 0)
        broken = sub.get("Is Broken?")
        sinkrule.append((tag, "OK" if (after and broken is False) else "BAD",
                         f"src w{w_now}.Terms[{srcs[0]['i']}] owner {srcs[0].get('owner_class')}"
                         f"#{srcs[0].get('owner_uid')} -> D[{d}].N[{n}].T[{t}] {nm!r}; wire 0 -> {after}; "
                         f"Is Broken? {broken!r}; delta {dw}; ExecState {es}; err {str(err)[:60]!r}"))
        if after and broken is False:
            claim_wire(tag, "from_tunnel", after)                  # K3(b)
            done.append((tag, f"OpConnectFromWire_v0 w{w_now} -> D[{d}].N[{n}].T[{t}] wire {after}, "
                              f"Is Broken? FALSE"))
            return True
        failed.append((tag, f"OpConnectFromWire_v0: wire 0 -> {after}, Is Broken? {broken!r}, "
                            f"err {str(err)[:80]!r}"))
        return False

    for r in rows:
        act = r["action"].split(":")[0]
        src = r.get("source") or {}
        sink_uid, sink_t, sink_name = r["uid"], r["i"], r["name"]
        dest = r.get("dest") or DEST_FALLBACK.get(sink_uid)
        # `tag` was assigned AFTER the RETARGET block below while that block already appended `(tag, ...)` on a
        # name mismatch - a latent NameError that run 2 never reached because no row mismatched. Moved up.
        tag = f"#{sink_uid} t{sink_t} {sink_name!r} <- {act} {src.get('uid')}"
        # CODEX'S FALSIFICATION TEST, RUN AS A GATE (`archive/peer/2026-09-17-routeb-run1-noroute-codex.md`
        # point 1). Giving `#5058`'s rows `dest = "1.2"` proves only WHERE the fresh kernel is; it does not prove
        # that `sink_term` still names the same connector. The fresh `GPU_kernel_v1.vi` has a different pane
        # population (13 shared + 6 extra) from the deleted `Track N beads four-fold over-kernel-v3.vi`'s 16
        # terminals, and a compatible data type would make a wrong wire NON-broken - "wrong-but-valid, and no
        # gate here would catch it". So for every RE-TARGETED sink the live terminal at that index must carry the
        # SAME NAME the pristine census recorded, or the row is refused rather than wired.
        if sink_uid in RETARGET and sink_name:
            _d, _n, _t, _live = sink_addr(dest, sink_uid, sink_t, sink_name)
            got = (_live or {}).get(_t, ("<no such terminal>", None, None))[0] if _n is not None else None
            if got != sink_name:
                noroute.append((tag, f"RE-TARGET REFUSED: the deleted #{sink_uid} carried {sink_name!r} at t{sink_t}, "
                                     f"but the fresh #{RETARGET[sink_uid]} carries {got!r} at t{_t}. The index "
                                     f"does not name the same connector, so wiring it would be a wrong-but-valid "
                                     f"connection (codex, routeb-run1-noroute, point 1)"))
                continue
            retarget_ok.append((sink_uid, sink_t, sink_name))
        try:
            if dest is None and act in ("from-const", "from-sr", "to-sr"):
                noroute.append((tag, f"{act} needs a destination LOOP and this sink stays where it is "
                                     f"(d1_rewire_map assigns `dest` only to the movers)"))
                continue
            if act == "from-const":
                d, n, t, _live = sink_addr(dest, sink_uid, sink_t, sink_name)
                loop_i = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(loops[dest]["loop"])
                if n is None:
                    raise RuntimeError("the sink node is not on its destination diagram")
                res = CONST_ON_TERM(TARGET, loop_i, n, t, CONST_LABELS, value=src.get("val"))
                ok = bool(res.get("created_uid")) and not res.get("inv_err")
                (done if ok else failed).append(
                    (tag, f"OpCreateConstOnTerm_v0 value {src.get('val')!r} -> uid {res.get('created_uid')} "
                          f"{str(res.get('inv_err', ''))[:60]}"))
                continue
            if act in ("from-sr", "to-sr"):
                row_of = src.get("row") or dest
                regs_here = reg_by_row.get(row_of, [])
                ridx = next((i for i, (u, nm, rr, ll) in enumerate(regs_here) if rr == src.get("right")), None)
                d, n, t, _live = sink_addr(row_of, sink_uid, sink_t, sink_name)
                loop_i = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(loops[row_of]["loop"])
                if ridx is None or n is None:
                    raise RuntimeError(f"register {src.get('right')} or node {sink_uid} not found on {row_of}")
                g.wire_sr("LeftIn" if act == "from-sr" else "RightIn", TARGET, loop_i, ridx,
                          node_index=n, term_index=t)
                # K3(a): this row used to record NO uid and NO readback - "WIRED" meant only that the call
                # returned. ONE `node_terms` read, the same one every other path already pays, with the `None`
                # sentinel so ABSENT is distinguishable from bare.
                _wsr = (next((x["wire"] for x in g.node_terms(TARGET, d, n) if x["i"] == t), None)
                        if n is not None else None)
                claim_wire(tag, "wire_sr", _wsr)                   # K3(b)
                done.append((tag, f"wire_sr {'LeftIn' if act == 'from-sr' else 'RightIn'} reg[{ridx}] "
                                  f"-> D[{d}].N[{n}].T[{t}] wire {_wsr} "
                                  f"({'NO SUCH TERMINAL' if _wsr is None else ('BARE' if _wsr == 0 else 'ok')})"))
                continue
            if act == "from-ctl":
                lbl = src.get("label")
                if lbl and not sink_name:
                    # DECISION (2), 2026-09-17: R3's unnamed sink. `wire_control` is name-addressed on BOTH ends,
                    # so the control is given a WIRE (its own, or a temporary named sink) and the sink is reached
                    # by INDEX with `OpConnectFromWire_v0`.
                    from_ctl_unnamed(tag, dest, sink_uid, sink_t, sink_name, lbl)
                    continue
                if not lbl:
                    # §11u.2 fault 2: a ForLoop tunnel whose name `Wire Inputs.vi` will not match.
                    noroute.append((tag, f"control {lbl!r} / sink name {sink_name!r}: wire_control is "
                                         f"name-addressed on BOTH ends and the CONTROL end has no label"))
                    continue
                # §11u.2 fault 1, CLOSED by measurement: the caller MUST pass src_diagram_index = the Traverse
                # index of the diagram the ControlTerminal now lives on. After S3-ct that is 1.2's body.
                ci.update(class_index(TARGET))
                s_cls, s_i = ci.get(RETARGET.get(sink_uid, sink_uid), (None, None))
                d, n, t, _live = sink_addr(dest, sink_uid, sink_t, sink_name)
                # WHICH DIAGRAM THE CONTROL TERMINAL IS ON IS NOT ASSUMED (prior-art B2). The first draft passed
                # 1.2's body unconditionally with the comment "after S3-ct that is 1.2's body" - which is true
                # only if S3-ct actually reparented it, and run 9 failed with six 5001s from `Get Controls.vi`
                # for exactly that reason (`build_d1_v0_run9.log:315-316`, cause at `d1-build-plan.md:1169`).
                # So the index follows what S3-ct MEASURED, and the other one is tried if the sink stays bare.
                sd_moved = diag_index(TARGET, loops["1.2"]["body"])
                sd_stay = diag_index(TARGET, FRAME_BODY_UID)
                order = ([sd_moved, sd_stay] if lbl in (r3.get("ct_moved") or set()) else [sd_stay, sd_moved])
                after, tried = 0, []
                for sd in order:
                    try:
                        # branch=True, then VERIFY BY EFFECT: a control that already drives another sink gains
                        # NO Wire object on a branch (gscript.py:1906-1910, twice misread as a silent decline
                        # on 2026-08-31), while a crossing into a structure adds two - so the delta check
                        # cannot discriminate and the sink terminal's own wire is the only sound gate.
                        g.wire_control(TARGET, [lbl], s_cls, s_i, [sink_name], branch=True, src_diagram_index=sd)
                        # ---- K3(a) (cycle-39 judgement, disposing `2026-09-19-routeb-run7-index-shift.md` Q4):
                        # THE SENTINEL IS `None`, NOT `0`. `next(..., 0)` returned the SAME value for "the
                        # terminal exists and is unwired" and for "there is no such terminal", so run 7's
                        # `#2222 t5 'Correction Factor'` ledger row read `sink wire 0 -> 0` and that was taken
                        # as evidence the terminal existed. It is not. `None` = ABSENT, `0` = present and bare.
                        # The `from-tunnel` path already distinguishes them (`.get(t, ("<no such terminal>",
                        # None, None))` in this file's `from_tunnel`); this path now does too.
                        after = (next((x["wire"] for x in g.node_terms(TARGET, d, n) if x["i"] == t), None)
                                 if n is not None else None)
                        tried.append((sd, "no error", after))
                    except Exception as e:
                        # J2(d) + J4 (cycle-39 judgement, disposing the run-6 regression review). THIS is the
                        # line the review named: `tried.append((sd, str(e)[:70], 0))` recorded the INITIALISER
                        # `0`, so run 6's `#2222 t5 'Correction Factor'` ledger row read `sink wire 0 -> 0` on
                        # both indices while the sink was NEVER READ after the attempts - the wire may have been
                        # made. It is read from the machine now, and the message is no longer truncated at the
                        # colon before LabVIEW's error code.
                        try:
                            # K3(a), same sentinel change as above: None = ABSENT, 0 = present and bare.
                            after = (next((x["wire"] for x in g.node_terms(TARGET, d, n) if x["i"] == t), None)
                                     if n is not None else None)
                            _rb = (f"machine read after the raise: sink D[{d}].N[{n}].T[{t}] wire {after} "
                                   f"({'NO SUCH TERMINAL' if after is None else 'present'})")
                        except Exception as e3:
                            after = None
                            _rb = f"sink UNREAD after the raise ({type(e3).__name__}: {e3})"
                        tried.append((sd, f"{e} || {_rb}", after))
                    if after:
                        break
                claim_wire(tag, "wire_control", after)              # K3(b)
                (done if after else failed).append(
                    (tag, f"wire_control {lbl!r} -> {sink_name!r}; sink D[{d}].N[{n}].T[{t}] wire {after} "
                          f"({'NO SUCH TERMINAL' if after is None else ('BARE' if after == 0 else 'ok')}); "
                          f"reparented={lbl in (r3.get('ct_moved') or set())}; attempts {tried}"))
                continue
            if act == "from-tunnel":
                from_tunnel(tag, r, dest, sink_uid, sink_t, sink_name)
                continue
            # same-loop / from-kernel: a NODE source. By NAME where both ends have one, by INDEX otherwise.
            if not sink_name or not src.get("name"):
                if src.get("kind") == "node" and src.get("i") is not None:
                    v1_connect(tag, dest, sink_uid, sink_t, sink_name, src["uid"], src["i"], dest,
                               f"unnamed end (sink {sink_name!r}, source {src.get('name')!r})")
                else:
                    noroute.append((tag, f"unnamed end and the source is not a node ({src.get('kind')})"))
                continue
            s_uid = RETARGET.get(src["uid"], src["uid"])
            s_cls, s_i = ci.get(s_uid, (None, None))
            d_cls, d_i = ci.get(RETARGET.get(sink_uid, sink_uid), (None, None))
            if s_cls is None or d_cls is None:
                ci.update(class_index(TARGET))
                s_cls, s_i = ci.get(s_uid, (None, None))
                d_cls, d_i = ci.get(RETARGET.get(sink_uid, sink_uid), (None, None))
            if s_cls is None or d_cls is None:
                raise RuntimeError(f"no Traverse class/index for source {s_uid} or sink {sink_uid}")
            try:
                g.wire(TARGET, s_cls, s_i, src["name"], d_cls, d_i, sink_name, branch=True)
                # K3(a): same repair as the `wire_sr` row above - a plain `wire` row recorded no uid at all.
                try:
                    _d2, _n2, _t2, _l2 = sink_addr(dest, sink_uid, sink_t, sink_name)
                    _ww = (next((x["wire"] for x in g.node_terms(TARGET, _d2, _n2) if x["i"] == _t2), None)
                           if _n2 is not None else None)
                except Exception as _e2:
                    _ww = None
                    _l2 = f"<readback raised {type(_e2).__name__}: {str(_e2)[:60]}>"
                claim_wire(tag, "wire", _ww)                       # K3(b)
                done.append((tag, f"wire {s_cls}[{s_i}].{src['name']!r} -> {d_cls}[{d_i}].{sink_name!r} "
                                  f"wire {_ww} "
                                  f"({'NO SUCH TERMINAL' if _ww is None else ('BARE' if _ww == 0 else 'ok')})"))
            except Exception as e:
                if src.get("kind") == "node" and src.get("i") is not None:
                    v1_connect(tag, dest, sink_uid, sink_t, sink_name, src["uid"], src["i"], dest,
                               f"retry by index after {str(e)[:60]}")
                else:
                    failed.append((tag, str(e)[:160]))
        except Exception as e:
            failed.append((tag, str(e)[:160]))

    # ---- RUN 5 (cycle-36 judgement (c)): THE LEDGER PRINTS FIRST. In run 4 this block sat AFTER
    # `settle_index_modes()`, which raised `error 2`, and all 66 `s3w` rows were lost with it. A ledger that
    # does not survive an exception in a later step is not a ledger.
    print("\n  --- S3w LEDGER (printed BEFORE settle_index_modes, run 5) ---", flush=True)
    fact(f"S3w ledger PRE-SETTLE: attempted {len(rows)}, WIRED {len(done)}, FAILED {len(failed)}, "
         f"NO-ROUTE {len(noroute)}")
    # ---- K3(b) THE SURVIVAL CENSUS. Placed HERE, immediately after the ledger line and BEFORE
    # `settle_index_modes()`, on the cycle-39 judgement's instruction: the run has NEVER YET REACHED S5, so a
    # census placed there would never have been read. ONE `report_all(TARGET,'Wire')` traverse, no new op. It
    # answers the question the WIRED count does not: do the wires the ledger CLAIMS still exist on the machine?
    try:
        _live_w = set(int(o["uid"]) for o in g.report_all(TARGET, "Wire"))
        _claimed = [(t, k, u) for t, k, u in ledger_wires]
        _gone = [(t, k, u) for t, k, u in _claimed if u not in _live_w]
        _by_kind = {}
        for t, k, u in _claimed:
            _by_kind.setdefault(k, [0, 0])
            _by_kind[k][0] += 1
            if u in _live_w:
                _by_kind[k][1] += 1
        fact(f"S3w K3 SURVIVAL CENSUS: {len(_claimed)} wire uid(s) claimed by the WIRED rows, "
             f"{len(_claimed) - len(_gone)} still exist, {len(_gone)} GONE; live Wire objects on the VI "
             f"{len(_live_w)}; per row-kind (claimed, surviving) "
             f"{ {k: tuple(v) for k, v in sorted(_by_kind.items())} }")
        for _t, _k, _u in _gone:
            print(f"      GONE     w{_u}  [{_k}]  {_t}", flush=True)
        if not _gone:
            print("      (no claimed wire has disappeared)", flush=True)
        _unrecorded = [t for t, _d in done if not any(t == tt for tt, _kk, _uu in _claimed)]
        fact(f"S3w K3 CENSUS COVERAGE: {len(done)} WIRED rows, {len(set(t for t, _k, _u in _claimed))} of them "
             f"registered a wire uid; rows with NO uid recorded (so NOT covered by the census): {_unrecorded}")
    except Exception as e:
        fact(f"S3w K3 SURVIVAL CENSUS UNREAD ({type(e).__name__}: {e}) - reported, not hidden; "
             f"{len(ledger_wires)} uid(s) had been claimed")
    for t, d in done:
        print(f"      WIRED    {t}  {d}", flush=True)
    for t, d in failed:
        print(f"      FAILED   {t}  {d}", flush=True)
    for t, d in noroute:
        print(f"      NO-ROUTE {t}  {d}", flush=True)
    settle_index_modes()
    # v1 / B2: the Z/dZ row may never REACH the ledger - if the S3 pre-wire survived the reparent the terminal
    # is not bare, so `d1_rewire_map` has no cut row for it. Report its live state either way.
    try:
        _bz = diag_index(TARGET, loops["1.2"]["body"])
        wmap(TARGET, _bz, fresh=True)
        _wz = terms_of(TARGET, _bz, ZDZ_SINK[0]).get(ZDZ_SINK[1], (None, None, 0))[2]
    except Exception as e:
        _wz = f"UNREAD ({type(e).__name__}: {str(e)[:60]})"
    fact(f"S3w {ZDZ_LABEL!r} -> #{ZDZ_SINK[0]} t{ZDZ_SINK[1]} FINAL: wire {_wz}; "
         f"ledger row present = {any(f'#{ZDZ_SINK[0]} t{ZDZ_SINK[1]} ' in t for t, _ in done + failed + noroute)}; "
         f"PREWIRED {json.dumps(PREWIRED.get(ZDZ_SINK, {}), default=str)}")
    # (the WIRED/FAILED/NO-ROUTE loops that used to stand here now run BEFORE settle_index_modes, above.)
    print("\n  --- the SINK RULE, row by row (route B frontmatter) ---", flush=True)
    for t, v, d in sinkrule:
        print(f"      SINK-{v:<8} {t}  {d}", flush=True)
    fact(f"S3w RE-TARGET name check (codex point 1): {len(retarget_ok)} rows where the fresh subVI's "
         f"terminal at the pristine index carries the SAME name - verified, not assumed")
    fact(f"S3w ledger: attempted {len(rows)}, WIRED {len(done)}, FAILED {len(failed)}, NO-ROUTE {len(noroute)}; "
         f"SINK RULE {sum(1 for _t, v, _d in sinkrule if v == 'OK')} OK / "
         f"{sum(1 for _t, v, _d in sinkrule if v == 'REFUSED')} REFUSED / "
         f"{sum(1 for _t, v, _d in sinkrule if v == 'BAD')} BAD")
    ok = gate("S3w 0 rows FAILED", not failed, f"{len(failed)} failed: {[t for t, _ in failed][:6]}")
    ok &= gate("S3w 0 rows NO-ROUTE (route B §7's own gate)", not noroute,
               f"{len(noroute)} have none: {[t for t, _ in noroute][:8]}")
    # v1 / B1 replaces v0's "both lock-stepped SR queues built" gate: the mechanism is now a MOVED REGISTER.
    sr_rows_done = [t for t, _d in done if "MOVED REGISTER" in _d]
    gate("S3w both MOVED registers wired on BOTH sides (v1/B1, cycle15 Pre-decided 2)", len(sr_rows_done) == 2,
         f"{len(sr_rows_done)} of 2: {sr_rows_done}")
    # RESTATED for cycle27 Pre-decided 13a (run 5): `SR_QUEUE_AUTHORISED` stays False PERMANENTLY, and the
    # temporary sink is authorised for the `Z/dZ` row ONLY. The old form asserted `TEMP_SINK_AUTHORISED is
    # False`, which 13a has revised, so it would log a spurious FAIL. Its contribution to `ok`/`clean` is
    # unchanged: it is a bare `gate(...)` call and is NOT ANDed in.
    gate("S3w authorisation flags at cycle27 Pre-decided 13a (SR_QUEUE False permanently; the temporary sink "
         "used by the Z/dZ row ONLY, no other row)",
         (not _SR_MADE and SR_QUEUE_AUTHORISED is False
          and all(lbl == "Z/dZ" for _t, lbl in _TEMP_SINK_USED)),
         f"queues made {sorted(_SR_MADE)}, SR_QUEUE={SR_QUEUE_AUTHORISED}, TEMP_SINK={TEMP_SINK_AUTHORISED}, "
         f"temp-sink rows {_TEMP_SINK_USED}")
    return dict(wired=done, failed=failed, noroute=noroute, sinkrule=sinkrule, clean=bool(ok), sr=dict(_SR_MADE),
                index_modes={str(k): v for k, v in _IMODE_PENDING.items()})


# ============================================================================== S1q / S4 / S5 / S6
def s1q(loops, clean):
    print("\n=== S1q: the 8 queues", flush=True)
    if not clean:
        print("  SKIPPED-GATE  S1q: the S3w ledger is not clean. A queue endpoint cannot give a route to a sink "
              "that has none, and an unsound base makes every count below meaningless (route B §7 S3w).",
              flush=True)
        return None
    outer_i = diag_index(TARGET, SIBLING_DIAG_UID)
    made = {}
    for name, bound in D1.QUEUES.items():
        fact(f"S1q {name} (bound {bound}) - obtain placed on Diagram[{outer_i}]")
    fact("S1q NOT EXECUTED in this run: `queue_node('obtain', …)` takes the ELEMENT TYPE from a named OUTPUT "
         "terminal of an existing node, and route B's plan (§2b) does not name which terminal types the eight "
         "queues take. That is a design row, not a mechanical one - reported, never guessed.")
    return made


def s4(loops):
    print("\n=== S4: conditional terminals", flush=True)
    loop_uids = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")]
    r = loop_end_ref(TARGET, loop_uids.index(FRAME_LOOP_UID))
    gate("S4a #637's conditional terminal is untouched",
         r["loop_uid"] == FRAME_LOOP_UID and r["cond_term_uid"] == COND_TERM_UID
         and r["cond_wire_uid"] == COND_WIRE_UID and not r["errs"],
         f"loop {r['loop_uid']}, term {r['cond_term_uid']} (want {COND_TERM_UID}), "
         f"wire {r['cond_wire_uid']} (want {COND_WIRE_UID}); errs {r['errs'][:80]!r}")
    for row in ("1.2", "1.5", "1.7"):
        rr = loop_end_ref(TARGET, loop_uids.index(loops[row]["loop"]))
        fact(f"S4 {row}: conditional terminal {rr['cond_term_uid']}, wire {rr['cond_wire_uid']} "
             f"(0 = the loop never stops); errs {rr['errs'][:60]!r}")
    print("  SKIPPED-GATE  S4b/S4s: the three sentinel Equal?s and their -1 literals need the queues of S1q; "
          "with S1q unexecuted there is no `Dequeue.element` to compare against.", flush=True)


def s5(inv0, loops):
    print("\n=== S5: purge, remove bad wires, ExecState", flush=True)
    junk = g.new_since(TARGET, "Invoke", inv0)
    for o in junk:
        ids = [x["uid"] for x in g.report(TARGET, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(TARGET, "Invoke", ids.index(o["uid"]), verify=False)
    left = g.new_since(TARGET, "Invoke", inv0)
    gate("S5a every junk Invoke left by the mutating ops is gone", not left, f"still present {left}")
    fact(f"S5 purged {len(junk)} junk Invoke(s): {[o['uid'] for o in junk]}")
    g.remove_bad_wires_scripted(TARGET)
    es = g.exec_state(TARGET)
    # v1 / A + Pre-decided 14a: this read is taken WITHOUT the original preloaded, exactly like S1's baseline.
    # It is reported as a PAIR with that baseline - the difference is the only part that is about this build.
    fact(f"S5 ExecState {es} read COLD (no preload) - by Pre-decided 14a a cold 0 is UNREAD as a verdict; the "
         f"reading that counts is the preloaded re-read C does before the copy is deleted")
    if gate("S5 ExecState 1 WARM", es == 1, f"ExecState {es}"):
        g.save(TARGET)
        fact(f"saved {TARGET}; size {os.path.getsize(TARGET)} bytes")
        return True
    # ---- ExecState 0: MEASURE, do not infer (CLAUDE.md "when a diagnosis is GUESSED twice, build the reader")
    # ⚠️ INSTRUMENT FIXED after run 1. The first version walked ALL 173 diagrams and reported **420** bare named
    # inputs (`build_d1_routeb_v0.log:419-436`) - and most of them are ORIGINAL: an unwired `error in (no error)`
    # or `type of dialog (OK msg:1)` is legal LabVIEW, so "bare named input" does NOT discriminate and the number
    # said nothing. It is now restricted to the diagrams THIS BUILD touched - the frame body, the diagram that
    # holds the loops, and the three new bodies - which is the set where a bare sink can only have been made here.
    # The sound general instrument is still `VI.Get Errors` (method 452), which CLAUDE.md lists as MISSING; this
    # run does not build it (a new op is judgement, not material).
    print("\n  --- ExecState 0: the MEASUREMENT, on the diagrams this build touched (not an explanation)",
          flush=True)
    touched = [("frame body #639", diag_index(TARGET, FRAME_BODY_UID)),
               ("diagram 19 #686", diag_index(TARGET, SIBLING_DIAG_UID))]
    for row in ("1.2", "1.5", "1.7"):
        if row in (loops or {}):
            touched.append((f"{row} body #{loops[row]['body']}", diag_index(TARGET, loops[row]["body"])))
    bad = []
    for label, i in touched:
        try:
            rows = g.node_labels(TARGET, i)
        except Exception as e:
            fact(f"S5m {label}: node_labels raised {str(e)[:60]}")
            continue
        for n in range(len(rows)):
            try:
                for r in g.node_terms(TARGET, i, n):
                    if not r["is_source"] and r["wire"] == 0 and r["name"]:
                        bad.append((label, i, n, r["i"], r["name"]))
            except Exception:
                break
    fact(f"S5m {len(bad)} bare NAMED input terminals on the {len(touched)} diagrams this build touched "
         f"({[l for l, _i in touched]}) - NOT a verdict on its own: an unwired `error in (no error)` is legal, "
         f"which is why run 1's whole-VI count of 420 discriminated nothing")
    for row in bad[:80]:
        print(f"      BARE  {row[0]} Diagram[{row[1]}] Nodes[{row[2]}].T[{row[3]}] {row[4]!r}", flush=True)
    return False


def s6():
    print("\n=== S6: cold re-open in a restarted LabVIEW", flush=True)
    g._lv = None
    import subprocess
    try:
        rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                            capture_output=True, text=True, timeout=600)
        fact(f"lv_restart rc={rc.returncode}: {(rc.stdout or '').strip().splitlines()[-1:]}")
    except Exception as e:
        fact(f"lv_restart failed ({str(e)[:80]})")
    g._lv = None
    es = g.exec_state(TARGET)
    got = {c: g.count(TARGET, c) for c in ("Diagram", "WhileLoop", "ControlTerminal")}
    fact(f"cold: ExecState {es}, {got}, size {os.path.getsize(TARGET)} bytes")
    return gate("S6 cold re-open is runnable and the census holds",
                es == 1 and got["Diagram"] == BEFORE["Diagram"] + 3
                and got["WhileLoop"] == BEFORE["WhileLoop"] + 3
                and got["ControlTerminal"] == BEFORE["ControlTerminal"], f"ExecState {es}, {got}")


# ============================================================================== v1 / C: MEASURE BEFORE DELETING
def preload_reread(path):
    """cycle27 Pre-decided 14 + 14a. Run 3 deleted its broken working copy and destroyed the evidence, so the
    ExecState-0 cause on record is an advance INFERENCE. This re-reads `ExecState` on the LIVE copy with the
    ORIGINAL preloaded READ-ONLY - the `tools/bench/p2_open_copy.py` pattern verbatim - in a RESTARTED instance,
    so nothing the build left resident can confound it. NOTHING IS SAVED and nothing is run. Every reading that
    comes back beside an exception is reported UNREAD, never as a value (14: "a value returned beside an error
    has measured nothing"). This is a read-only step and is deliberately NOT part of the build: adding a preload
    to the build itself can cross-link the copy to the in-memory original's subVIs and `g.save(TARGET)` would
    write that (Pre-decided 14(b))."""
    print("\n=== C: preloaded re-read of the LIVE broken copy, BEFORE it is deleted (Pre-decided 14)", flush=True)
    if not os.path.exists(path):
        fact(f"C: the working copy {os.path.basename(path)} is already gone - nothing to re-read")
        return
    try:
        g.close_panel(path)
    except Exception:
        pass
    g._lv = None
    import subprocess
    try:
        rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                            capture_output=True, text=True, timeout=600)
        fact(f"C: lv_restart rc={rc.returncode} (a fresh instance, so the build's residents cannot confound "
             f"the reading); handles now {labview_handles()}")
    except Exception as e:
        fact(f"C: lv_restart FAILED ({type(e).__name__}: {str(e)[:80]}) - the reading below is taken in "
             f"whatever instance exists and is weaker for it")
    m_before = md5(ORIGINAL)
    app = vo = vc = None
    try:
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        app = dynamic.Dispatch("LabVIEW.Application")
        try:
            vo = app.GetVIReference(ORIGINAL, "", False, 0)
            es_o = int(vo.ExecState)
            fact(f"C: the ORIGINAL is resident READ-ONLY, its own ExecState {es_o}")
        except Exception as e:
            fact(f"C: the ORIGINAL could NOT be preloaded - UNREAD ({type(e).__name__}: {str(e)[:90]}). Every "
                 f"reading below is therefore still a COLD read and stays UNREAD.")
        try:
            vc = app.GetVIReference(path, "", False, 0)
            es_c = int(vc.ExecState)
            fact(f"C: **PRELOADED ExecState of the LIVE working copy {os.path.basename(path)} = {es_c}** "
                 f"(1 = idle/runnable, 0 = broken). Compare with S1's baseline and S5's cold read.")
        except Exception as e:
            fact(f"C: the working copy's preloaded ExecState is UNREAD ({type(e).__name__}: {str(e)[:90]})")
    except Exception as e:
        fact(f"C: the preloaded re-read could not run at all - UNREAD ({type(e).__name__}: {str(e)[:110]})")
    finally:
        # reference hygiene (CLAUDE.md): every reference this step opened is released here
        vo = None
        vc = None
        app = None
        m_after = md5(ORIGINAL)
        fact(f"C: original md5 across the preloaded read: {m_before} -> {m_after} "
             f"({'UNCHANGED' if m_before == m_after else '**CHANGED**'}); nothing was saved, nothing was run")


# ============================================================================== main
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    if "--restart" in sys.argv:
        import subprocess
        try:
            rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                                capture_output=True, text=True, timeout=600)
            print(f"  FACT  lv_restart rc={rc.returncode}", flush=True)
        except Exception as e:
            print(f"  FACT  lv_restart FAILED {str(e)[:100]}", flush=True)
    t0 = time.time()
    g._lv = None
    result, saved, crashed = {}, False, False
    h0 = s0()
    # P3 (cycle-38 judgement): an IN-PROCESS refnum ledger at every phase boundary. It counts the VI Server
    # references THIS recipe's own calls open and release through gscript (`gscript.vi_ref`, :226-255). It is
    # NOT `labview_handles()`: the kernel handle count cannot see VI Server refnums, which is exactly why the
    # run4-vs-run5 handle comparison was withdrawn (STATUS lock block, 2026-09-19).
    # ⚠️ AND NOT EVIDENCE ABOUT `error 2` EITHER (cycle-38 dispatch 1, measured; prior-art F4 `helper-exists`,
    # ACCEPTED IN PART): no `Traverse for GObjects` refnum array ever crosses COM - `report_all` reads only
    # scalar columns (`tools/gscript.py:451-463`) - so these counters cannot see the suspected refnum-class
    # exhaustion inside an op VI, and a flat reading here must NOT be cited as excluding it. They are kept
    # because CLAUDE.md §3's reference-hygiene rule mandates them whatever explains `error 2`.
    def refs(phase):
        fact(f"REFS after {phase}: {g.ref_counts()}")
    try:
        # the ControlTerminal search runs FIRST, on its own throwaway copy, so the build target is never open
        # at the same time and the destructive probe can never touch it.
        ct_uids = resolve_ctlterms()
        refs("resolve_ctlterms")
        s1()
        refs("S1")
        inv0 = g.uids(TARGET, "Invoke")
        d43 = s1t()
        refs("S1t")
        deleted_cut = s1d(d43)
        refs("S1d")
        loops = s2()
        refs("S2")
        fresh_uid = s2d(loops)
        refs("S2d")
        r3 = s3(loops, deleted_cut, ct_uids)
        refs("S3")
        _panel_before, regs = s3c(loops)
        refs("S3c")
        led = s3w(loops, regs, r3, fresh_uid)
        refs("S3w")
        s1q(loops, led["clean"])
        s4(loops)
        refs("S4")
        panel_after = g.panel_wiring(TARGET)
        gate("S3c panel survived: 114 rows", len(panel_after) == BEFORE["ControlTerminal"],
             f"{len(panel_after)} rows")
        saved = s5(inv0, loops)
        if saved:
            if os.path.exists(DELIVERABLE):
                os.remove(DELIVERABLE)
            g.close_panel(TARGET)
            os.rename(TARGET, DELIVERABLE)
            fact(f"renamed to the deliverable {DELIVERABLE} ({os.path.getsize(DELIVERABLE)} bytes)")
            globals()["TARGET"] = DELIVERABLE
            s6()
        result = dict(loops=loops, fresh=fresh_uid, cut=r3["cut"], ledger=led,
                      sr_changed=r3["sr_changed"], saved=saved)
    except Stop as e:
        fact(f"STOP at a fatal gate: {e}")
    except BaseException as e:                       # RUN 5 (d): the EXCEPTION path, re-raised unchanged
        crashed = True
        fact(f"CRASH {type(e).__name__}: {str(e)[:160]} - the working copy is RENAMED ASIDE, not deleted")
        raise
    finally:
        if not saved:
            try:
                g.close_panel(TARGET)
            except Exception:
                pass
            # v1 / C: MEASURE BEFORE DELETING (Pre-decided 14). Deleting the working copy stays the rule;
            # capturing the reading first is now part of it.
            try:
                preload_reread(TARGET)
            except Exception as e:
                fact(f"C: preload_reread raised {type(e).__name__}: {str(e)[:110]} - the reading is UNREAD")
            try:
                if crashed:
                    # RUN 5 (cycle-36 judgement (d)): on the EXCEPTION path only, keep the copy so the state
                    # that produced the crash can be measured. The next run deletes it in S0.
                    aside = TARGET[:-3] + f"_crash_{time.strftime('%H%M%S')}.vi"
                    if os.path.exists(TARGET):
                        os.rename(TARGET, aside)
                        fact(f"working copy RENAMED ASIDE after a crash (NOT deleted): {aside}")
                    else:
                        fact("working copy RENAME ASIDE skipped - the file is not on disk")
                else:
                    if os.path.exists(TARGET):
                        os.remove(TARGET)
                    fact(f"working copy deleted (a broken VI is never written): {os.path.basename(TARGET)}")
            except Exception as e:
                fact(f"working copy NOT deleted/renamed ({str(e)[:60]})")
        g._lv = None
        m1 = md5(ORIGINAL)
        gate("S6b original md5 AFTER", m1 == ORIG_MD5, m1)
        fact(f"LabVIEW handles after: {labview_handles()} (before {h0})")
        fact(f"REFS final: {g.ref_counts()} (in-process VI Server refs; `live` should be 0 and "
             f"`cached_op_vis` is the bounded one-per-op-VI cache)")
        result["md5_after"] = m1
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)
    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== build_d1_routeb_v2: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
