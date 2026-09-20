r"""stage_d1_s3_focus - D1 STAGE S3 as `docs/cycle27-plan.md` Pre-decided 37(g) defines it: the WHOLE 1.5 FOCUS
node set is moved into loop a and re-wired, in ONE script with ONE `g.save()` to `claudeDev\D1_s3_loop15.vi`.

START FROM `claudeDev\D1_s2_loops.vi` (md5 6ff19497f2309e007a214660bb64b911, 475,707 B - `docs/cycle27-plan.md`
Pre-decided 37(a)). DESTINATION: **loop a = `WhileLoop #23032`, body `Diagram #23058`** - assigned by
`docs/cycle27-plan.md:1126-1131` (Pre-decided 37(h)), which says in terms: "cite this line, never re-derive it".
So it is cited, not re-derived.

THE SET (Pre-decided 37(g), `docs/cycle27-plan.md:1116-1125`), all currently on **`Diagram #639`** - the body of
`WhileLoop #637`, NOT `#686` (37(f), `docs/cycle27-plan.md:1106-1108`, measured
`tools/bench/diag_movein_set.log:41`, `:50`):
    `CaseStructure #10407` (autofocus) - `docs/d1-build-plan.md:305`
    `#48 ASI_adjust focus-subvi.vi`     - `docs/d1-build-plan.md:306`
    `#3529` `- Inc (PgDn)`   - a **ControlReferenceConstant** - `docs/d1-build-plan.md:330`
    `#3560` `+ Inc (PgUp)`   - a **ControlReferenceConstant** - `docs/d1-build-plan.md:331`
    `#3447` `Focus Step (F1)` - a **ControlReferenceConstant** - `docs/d1-build-plan.md:332`
    shift registers `#4334/#4344` (**the VISA session**) and `#4256/#4274` (`position [internal units]`)
    - `docs/d1-build-plan.md:359-360`

🔴 NO VI IS RUN (34(f), `docs/cycle27-plan.md:904-907`). The only VIs that execute are the BUILT op VIs - that is
   what scripting is. No new op, no new device (Pre-decided 2; user 2026-09-18 08:53).
🔴 No motor, no ASI, no camera, no GUI action. Rig state 조립; this build needs no instrument.
🔴 The ORIGINAL, `claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are never written. Every edit lands on
   `claudeDev\D1_s3_loop15.vi`, a fresh copy of the S2 artefact made by this script.

================================================================================================================
WHAT ALREADY EXISTS AND IS REUSED - checked before a line was written (CLAUDE.md "check what exists first":
`grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`)
================================================================================================================
  * `build_d1_v0.move_in` `:318` - THE BUILT MOVER (`OpMoveIn_v0.vi`). It is NOT in `tools/gscript.py`, which has
    only `move_out` `:2674` and `move_object` `:2299`. Nothing is hand-rolled for the move.
  * `build_d1_v0.owner_of` `:338` / `diag_index` `:357` - owner class/uid and Traverse index, both BY UID.
  * `build_opstopfromnode_v0.walk` `:129` - the BUILT per-diagram census: {uid: (Nodes[] index, label, rows)}
    with `gscript.node_terms_uid` `:925` rows carrying the four per-property error columns. This is the
    wired-terminal instrument 37(e) requires; no wire census is used as a gate anywhere in this file.
  * `build_opconnectnested_v1.connect_nested_v1` `:418` (`OpConnectNested_v1.vi`, cold 7/0,
    `tools/bench/test_opconnectnested_v1_cold.py`) - the BUILT writer that wires
    Diagram[src].Nodes[].Terminals[] into Diagram[sink].Nodes[].Terminals[], both addressed by index. This is the
    re-wiring op; `gscript.connect_terminals` `:2407` is top-level-only and `gscript.connect2` `:2633` takes a
    TOP-LEVEL source, so neither can wire two nodes that both sit inside a loop body.
  * `gscript.add_shift_reg` `:673` / `wire_sr` `:713` / `shift_reg` `:753` / `shift_reg_left` `:786` - the BUILT
    shift-register family (INDEX rows 37-39, named as the route at `docs/d1-build-plan.md:368-369`).
  * `gscript.save/exec_state/open_panel/close_panel/count/uids/report_all/ref_counts` - built, unchanged.
  * `diag_s2_scaffold` `fresh` `:155` / `Preload` `:167` / `file_facts` `:142` / `read_state` `:343` /
    `try_save` `:351` - cycle 50's measured harness, imported. Importing it runs no build.
  * `diag_d1_execstate_preload.run_condition` `:192` - the BUILT child-process ExecState reader, used ONLY on the
    SAVED file (34(l): an unsaved in-memory edit cannot survive the restart it does).
  * `stage_d1_s1.cold_subvi_table` `:377` / `compare_subvi_tables` `:408` / `log_table_diff` `:430` /
    `TIFF_SUBVI_KEY` `:246` / `PIN_SUBVI_ROWS` `:245` - S1's BUILT, already-FATAL D5 instrument (29(g),
    `docs/cycle27-plan.md:629-641`), invoked exactly as `stage_d1_s1.py:727-755` invokes it. Its one module-level
    side effect, `g._run.__defaults__ = (6.0, 180.0)`, is captured and restored.
  * `bench_prep.labview_handles`; `hash_probe.probe` (34(k), `docs/cycle27-plan.md:970-973`).
  * `tools/bench/d1_rewire_sources.json` - the MEASURED cut-terminal table (109 cut / 109 resolved); its
    **17 rows with `"dest": "1.5"`** are this stage's whole re-wiring job. They are read from the file at run
    time and every uid in them is re-resolved against the machine before use.
  * `tools/recipes/build_d1_routeb_v7.py` `:1266` `v1_connect` / `:1116` `s3c` - the v3->v7 machinery that died
    ten times. It is CITED, not imported: 34(i) (`docs/cycle27-plan.md:936-939`) says the next build is a SHORT
    script and that re-arming those bytes is what cost cycle 49 its launch.
Nothing new is built.

================================================================================================================
THE FIVE BINDING CONSTRAINTS, and where each one is visible in the code below
================================================================================================================
 (1) **`move_in` IS ONE NODE PER CALL AND SEVERS EVERY WIRE ON THE MOVED NODE, IN EITHER ORDER** - 37(d),
     `docs/cycle27-plan.md:1093-1100`, measured `tools/bench/diag_movein_set.log:75`, `:86`, `:101`.
     => `phase_move()` calls `move_in` once per uid, in a fixed order, and re-reads the moved node afterwards.
 (2) 🔴 **A WIRE COUNT CAN NEVER DETECT A CUT** - 37(e), `docs/cycle27-plan.md:1101-1105`: the whole-VI `Wire`
     census held 1905 -> 1905 -> 1905 while both ends of wire 4833 went bare and uid 4833 stayed in the list.
     => **every re-wiring gate in this file counts WIRED TERMINALS** (`term_state()` / `node_state()`), and the
     `Wire` and `LoopTunnel` deltas are printed as OBSERVATIONS with no expected value at all. The `LoopTunnel`
     delta is whatever the border crossings require; it is MEASURED, never predicted.
 (3) **EVERY ADDRESS IS A uid OR AN EXACT NAME, RE-READ IMMEDIATELY BEFORE USE** - 34(h),
     `docs/cycle27-plan.md:927-935`; **and every report re-reads by uid or by ownership traversal, never by array
     index** - 37(b), `docs/cycle27-plan.md:1080-1086`. => `node_state()` resolves owner -> Traverse index ->
     `walk` -> Nodes[] index at each call site and caches nothing; the Nodes[] index of `#48` was MEASURED to
     drift 11 -> 10 when `#3529` left the same diagram (`tools/bench/diag_movein_set.log:41` vs `:66`).
 (4) **A VALUE RETURNED BESIDE A NON-ZERO ERROR COLUMN HAS MEASURED NOTHING** - Pre-decided 14,
     `docs/cycle27-plan.md:147-150`; 35(d)(1), `:1014-1016`. => `cond_read()` scores `OpLoopEndRef_v0`'s four
     error columns and returns UNREAD; `term_state()` does the same for a terminal row, with the ONE documented
     exception `gscript.py:874` names - a BARE terminal legitimately carries `conn_err`/`wire_err` 1055 with
     `name_err`/`src_err` 0. Any other error pattern is UNREAD, and **no gate in this file accepts UNREAD**.
 (5) **GATE OUTPUT IS THE DOCUMENTED `  FAIL  ` / `  PASS  ` FORM** - 37(i), `docs/cycle27-plan.md:1132-1139`:
     the `  **FAIL**  ` the cycle-50/52 diagnostics printed is what blinded `guard_peer.py:73`'s `FAILURE_RE`.
     This file must not invent a third format, so it emits the form the regex documents.

================================================================================================================
🔴 THREE ARITHMETIC CONFLICTS BETWEEN THE BRIEF AND THE MEASURED FILES, STATED BEFORE THE RUN
================================================================================================================
A prediction contract exists to say what is expected BEFORE the machine answers. Three of the brief's pass
criteria are, on this project's own measured files, not reachable by this stage. They are stated here, gated as
the brief defines them, and left for the judgement session - a material session does not re-cut a stage.

 (X1) **`CaseStructure #10407` CANNOT RETURN TO ITS PRE-MOVE WIRED-TERMINAL COUNT IN THIS STAGE.** Its 7 cut
      rows in `tools/bench/d1_rewire_sources.json` are `:1749-1918`. Four are internal to the 1.5 set or its two
      shift registers (t3 <- `#48` t6; t4 -> SR `#4334`; t5 <- `#48` t5; t6 -> SR `#4256`). **Three are not**:
        t0 (the SELECTOR, wire 10799) <- `#10686 'x .and. y?'`  - `action "cross-loop:1.2->1.5"`, `:1773`
        t1 `# slices in stack` (wire 9635) <- LoopTunnel `#9641` of `#637` - `action "from-tunnel"`, `:1789`
        t2 `Index of closest\ncal image slice, bead 2` (wire 10990) <- `#10757` t1 `element` - `:1818`
      `#10686` and `#10757` are 1.2 nodes that this stage does not move, so they stay inside `WhileLoop #637`.
      Two sibling loops cannot be wired directly without changing the computation, which is why
      `docs/d1-build-plan.md:250` says 1.5 is "woken by the 1-element `Q_focus`" - and the queue path is
      explicitly DEFERRED BEHIND S3 by Pre-decided 36 (`docs/cycle27-plan.md:1024-1060`). 37(g)'s supporting
      sentence, "**none** of its sources stays on `#686`", is an argument about `#48`'s seven rows; it is
      accurate for `#48` and it does not cover `#10407`. This script MEASURES the three rows (it re-reads the
      owner of each named source uid rather than trusting this paragraph) and reports them; gate `W-10407` is
      still stated as the brief states it, and is **PREDICTED TO FAIL at 4 of 7**.
 (X2) **`ExecState` IS THEREFORE PREDICTED 0, NOT 1, AND THE SAVE IS PREDICTED REFUSED.** A Case Structure with
      a bare selector terminal is a broken VI, and so is a shift register left with a bare inside terminal -
      which is what `#637`'s own `#4334/#4344` and `#4256/#4274` become once `#10407` and `#48` leave, since
      this stage creates new registers on loop a and does not delete the old pair (37(g) does not name a
      deletion, and `delete_object` on a shift register is unverified here). The same wall was measured in cycle
      52: `tools/bench/diag_movein_set.log:101` onward, `ExecState` 0 after two moves, `g.save()` refused
      verbatim with `allow_broken` never set.
 (X3) **THE SubVI TABLE KEY CONTAINS THE DIAGRAM uid, SO MOVING `#48` NECESSARILY CHANGES ITS KEY.**
      `stage_d1_s1.py:389` keys the table `(diagram_uid, node_uid)`. `#48` is a SubVI; after the move its key is
      `(23058, 48)`, not `(639, 48)`. "the ORIGINAL minus exactly `(639, 22700)`, missing 0 / extra 0 / changed
      0" is therefore unsatisfiable by construction for any stage that moves a SubVI. This file runs BOTH
      comparisons and prints both: the brief-literal one as an OBSERVATION, and a MOVE-AWARE one as the FATAL
      gate, in which `(639, 48)` is re-keyed to `(<the owner uid this run actually measured for #48>, 48)` with
      the name and path required to be IDENTICAL. The new key is read from the machine, never assumed.

================================================================================================================
PREDICTION CONTRACT - each line is a printed GATE. Counts are `D1_s2_loops.vi` -> `D1_s3_loop15.vi`.
================================================================================================================
 G1  the ORIGINAL exists, md5 2a78e17c449cacdaf5da389818526859 (hash_probe, read-only).                    FATAL
 G2  `claudeDev\D1_s2_loops.vi` md5 6ff19497f2309e007a214660bb64b911, 475707 B, BEFORE the copy.            FATAL
 G3  the target copy is byte-identical to it.                                                              FATAL
 G4  baseline census == Diagram 173 / WhileLoop 6 / SubVI 97 / Comparison 17 / LoopTunnel 135 / Wire 1905.  FATAL
 G5  loop a is `WhileLoop #23032`, its body is `Diagram #23058`, and `#23058`'s owner is `#23032` whose
     owner is `Diagram #686` - all read by ownership traversal, never by index (37(b)/37(h)).               FATAL
 G6  all five set members are owned by `Diagram #639` before any edit (37(f)).                              FATAL
 G7  the BEFORE wired-terminal count of each set member, with ZERO UNREAD rows: #10407 7, #48 7,
     #3529 1, #3560 1, #3447 1 (measured `tools/bench/diag_movein_set.log:41`, `:50`).                      FATAL
 G8  the 17 `"dest": "1.5"` rows load from `tools/bench/d1_rewire_sources.json`, and the resolved source of
     each is CLASSIFIED BY MEASURING ITS OWNER, not by this file's table: internal / shift-register /
     cross-loop. The classification is REPORTED; the count of cross-loop rows is REPORTED.             REPORTED
 G9a-e each `move_in` moves exactly ONE node: the moved uid's owner becomes `Diagram #23058` and its wired
     count goes to 0 (37(d) - severed in either order).                                                    FATAL
 G10 after the five moves, `Diagram #639` no longer owns any set member.                                   FATAL
 G11 two shift registers are created on loop a and read back by uid (`add_shift_reg` -> `shift_reg`).       FATAL
 G12 re-wiring batch k (batch size 12, so ONE batch here - there are 9 wirable jobs): every job's NODE-side
     terminal ends WIRED, and for a node-to-node job the SAME wire uid reads back on the source. Per job.   FATAL
 G13 `Wire` delta and `LoopTunnel` delta after the re-wiring: REPORTED, no predicted value (37(e)).    REPORTED
 G14 the three cross-loop rows are re-read and their sources' owners reported: REPORTED, never wired.  REPORTED
 W-48 / W-3529 / W-3560 / W-3447  each node's WIRED-TERMINAL count returns to its pre-move value, with
     ZERO UNREAD rows. Predicted PASS (7 / 1 / 1 / 1).                                                      FATAL
 W-10407  the same criterion, stated as the brief states it. **PREDICTED FAIL at 4 of 7** - see (X1). The
     adjusted line (pre-move minus the MEASURED cross-loop rows) is printed beside it.                      FATAL
 G15 `ExecState` == 1 immediately before the save, in-instance with the ORIGINAL PRELOADED (34(l)).
     **PREDICTED 0** - see (X2).                                                                            FATAL
 G16 ONE `g.save()`, `allow_broken` False, `gui_save` NEVER called (29(d)). **PREDICTED REFUSED.**           FATAL
 G17 the saved file re-read in a FRESH child process: COLD 1 and PRELOADED 1 (34(l)).                       FATAL
 G18 SubVI TABLE, move-aware (X3): the saved artefact's COLD table equals the ORIGINAL's COLD table minus
     `(639, 22700)` with `(639, 48)` re-keyed to `#48`'s MEASURED new owner, missing 0 / extra 0 /
     changed 0, ZERO rows into `claudeDev\background VIs_COPY\`, no empty name or path.                     FATAL
 G18r the BRIEF-LITERAL comparison (`expect_missing` = {(639, 22700)} only): REPORTED, with its delta.  REPORTED
 G19 `WhileLoop` is still 6.                                                                                FATAL
 G20 no live VI Server reference is left open.                                                         non-fatal
 G21 the ORIGINAL's md5 is unchanged; so are `D1_s1_copy.vi` and `D1_s2_loops.vi`.                          FATAL

A census + readings JSON is written to `tools/bench/stage_d1_s3_focus.json` AFTER EVERY PHASE, so a failure still
leaves data on disk (CLAUDE.md "Big or blocked work is SPLIT into steps that each SAVE an intermediate artefact").
If a FATAL gate stops the run before the save, a SALVAGE step still attempts the ONE `g.save()` with
`allow_broken` False - a save that cannot legally happen is refused by `gscript.save` itself, and a save that CAN
happen leaves the user a file to open. `_SAVE_ATTEMPTED` guarantees `g.save()` is called at most once (37(g)).

  MATERIAL=1 py tools/bgrun.py --max-min 45 --log tools/bench/stage_d1_s3_focus.log \
      -- py -u tools/recipes/stage_d1_s3_focus.py
"""
import json
import os
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                             # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                              # noqa: E402
import diag_s2_scaffold as D                                                     # noqa: E402
import diag_d1_execstate_preload as D1ES                                         # noqa: E402
from bench_prep import labview_handles                                           # noqa: E402
from build_d1_v0 import move_in, owner_of, diag_index                            # noqa: E402
from build_opstopfromnode_v0 import walk as WALK                                 # noqa: E402
from build_opstopfromnode_v0 import loop_end_ref as LOOP_END_REF                 # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1             # noqa: E402
from hash_probe import probe as HASH                                             # noqa: E402
# S1's BUILT SubVI-table instrument (29(g)). Its module-level `g._run.__defaults__ = (6.0, 180.0)` is captured
# and restored so the edit half runs on the timeouts cycle 50/51/52 measured; the S1 defaults are re-applied
# around the G18 block, where that instrument was measured.
_RUN_DEFAULTS_BEFORE_S1 = g._run.__defaults__
from stage_d1_s1 import (cold_subvi_table, compare_subvi_tables, log_table_diff,  # noqa: E402
                         BG_COPY, PIN_SUBVI_ROWS, TIFF_SUBVI_KEY)
_RUN_DEFAULTS_S1 = g._run.__defaults__
g._run.__defaults__ = _RUN_DEFAULTS_BEFORE_S1

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"            # Pre-decided 37(a), verified twice (35/0 and 23/0)
S2_SIZE = 475707
TARGET = os.path.join(g.CLAUDEDEV, "D1_s3_loop15.vi")
OUT = os.path.join(BENCH, "stage_d1_s3_focus.json")
REWIRE_JSON = os.path.join(BENCH, "d1_rewire_sources.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

SIBLING_DIAG_UID = 686           # the FlatSequenceFrame diagram that HOLDS WhileLoop #637
FRAME_BODY_UID = 639             # WhileLoop #637's body - where the 1.5 set lives today (37(f))
FRAME_LOOP_UID = 637
LOOP_A_UID = 23032               # 37(h), docs/cycle27-plan.md:1126-1131 - CITED, never re-derived
BODY_A_UID = 23058               # 37(h), same line

# The set, in the order `move_in` is called. Sources before sinks is arbitrary - 37(d) measured that the wires
# are severed in EITHER order - so the order is fixed here only to make the log reproducible.
SET = [
    (3529, "- Inc (PgDn)", 1, (40, 60), "ControlReferenceConstant; docs/d1-build-plan.md:330"),
    (3560, "+ Inc (PgUp)", 1, (40, 170), "ControlReferenceConstant; docs/d1-build-plan.md:331"),
    (3447, "Focus Step (F1)", 1, (40, 280), "ControlReferenceConstant; docs/d1-build-plan.md:332"),
    (48, "ASI_adjust focus-subvi.vi", 7, (300, 170), "SubVI; docs/d1-build-plan.md:306"),
    (10407, "Case Structure", 7, (620, 60), "CaseStructure (autofocus); docs/d1-build-plan.md:305"),
]
SET_UIDS = [u for u, _n, _w, _p, _w2 in SET]
PRE_MOVE_WIRED = {u: w for u, _n, w, _p, _w2 in SET}     # the counts diag_movein_set.log:41/:50 measured

# The two shift registers of row 1.5 (docs/d1-build-plan.md:359-360). The OLD pair stays on `#637`; these are NEW
# registers created on loop a by the BUILT `add_shift_reg`, which is the route d1-build-plan.md:368-369 names.
SR_SPECS = [
    {"tag": "VISA", "old_right": 4334, "old_left": 4344, "y": 120,
     "right_in": (10407, "VISA out", 4), "left_in": (48, "VISA resource name", 3),
     "why": "docs/d1-build-plan.md:360 - the VISA session; rows d1_rewire_sources.json:1853 (to-sr) and :2006"},
    {"tag": "POSITION", "old_right": 4256, "old_left": 4274, "y": 220,
     "right_in": (10407, "position [internal units]", 6), "left_in": (48, "In position", 4),
     "why": "docs/d1-build-plan.md:359; rows d1_rewire_sources.json:1898 (to-sr) and :2024 (from-sr)"},
]

# The five wires INTERNAL to the 1.5 set, from the measured rows. (sink uid, sink name, sink t, src uid,
# src name, src t, evidence). Every index here is a STARTING POINT that is re-read by name against the live
# census before the call (34(h)); the name is the address, the integer only the fallback.
INTERNAL_JOBS = [
    (48, "-Inc reference", 0, 3529, "- Inc (PgDn)", 0, "w4833; d1_rewire_sources.json:1919-1945 / :2096-2125"),
    (48, "+Inc reference", 1, 3560, "+ Inc (PgUp)", 0, "w2819; d1_rewire_sources.json:1946-1972 / :2126-2155"),
    (48, "Focus inc reference", 2, 3447, "Focus Step (F1)", 0,
     "w1893; d1_rewire_sources.json:1973-1998 / :2156-2185"),
    (10407, "Outgoing Handle", 3, 48, "Outgoing Handle", 6, "w11232; d1_rewire_sources.json:1820-1846 / :2066"),
    (10407, "Out position", 5, 48, "Out position", 5, "w7388; d1_rewire_sources.json:1865-1891 / :2036"),
]

# The rows whose source stays inside `WhileLoop #637` - NOT wired by this stage (X1). Their owners are MEASURED
# at run time; this table only says which uid to go and look at.
CROSS_ROWS = [
    {"sink": 10407, "sink_t": 0, "sink_name": "", "src_uid": 10686, "src_name": "x .and. y?", "src_t": 0,
     "wire": 10799, "evidence": "d1_rewire_sources.json:1749-1774, action 'cross-loop:1.2->1.5'"},
    {"sink": 10407, "sink_t": 1, "sink_name": "# slices in stack", "src_uid": None, "src_name": "LoopTunnel 9641",
     "src_t": None, "wire": 9635, "evidence": "d1_rewire_sources.json:1775-1792, action 'from-tunnel'"},
    {"sink": 10407, "sink_t": 2, "sink_name": "Index of closest\ncal image slice, bead 2", "src_uid": 10757,
     "src_name": "element", "src_t": 1, "wire": 10990,
     "evidence": "d1_rewire_sources.json:1793-1819, action 'cross-loop:1.2->1.5'"},
]
# The reverse crossing: `#10407` t6 also feeds `#12589` t1, and `#12589` STAYS on 1.1 (docs/d1-build-plan.md:307,
# d1_rewire_sources.json:1899-1908). It is a SINK that this stage cannot restore; reported, never wired.
REVERSE_CROSSING = {"src": 10407, "src_t": 6, "sink": 12589, "sink_t": 1, "wire": 9113,
                    "evidence": "docs/d1-build-plan.md:307; d1_rewire_sources.json:1899-1908"}

BASELINE = {"Diagram": 173, "WhileLoop": 6, "SubVI": 97, "Comparison": 17, "LoopTunnel": 135, "Wire": 1905}
BATCH_SIZE = 12          # "batches of 10-15 rows"; there are 9 wirable jobs, so exactly ONE batch here

passes, fails, facts = [], [], []
_SAVE_ATTEMPTED = [False]
R = {"script": os.path.abspath(__file__), "stage": "D1 S3 (Pre-decided 37(g))", "no_vi_was_run": True,
     "loop_identity_cited": "docs/cycle27-plan.md:1126-1131 (Pre-decided 37(h)) - cited, never re-derived",
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5}, "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "target": {"path": TARGET}, "phases": {}, "node_states": [], "moves": [], "shift_regs": [], "wire_jobs": [],
     "cross_rows": [], "readings": {}, "saves": {}, "handles": {}, "hash_probe": [], "cond_reads": []}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=True):
    """37(i), `docs/cycle27-plan.md:1132-1139`: the DOCUMENTED format is `  FAIL  ` / `  PASS  `, which
    `tools/hooks/guard_peer.py:73`'s FAILURE_RE matches. The bolded form the cycle-50/52 diagnostics printed is
    the defect that blinded that gate; this file must not invent a third format."""
    (passes if ok else fails).append(name)
    line = "  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else "")
    print(line.encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def probe(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


def dump(phase=None):
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    if phase:
        R.setdefault("phases_done", []).append(phase)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)
    if phase:
        fact("PHASE %s: readings written to %s" % (phase, OUT))


# ------------------------------------------------------------------ Pre-decided 14: UNREAD is a third outcome
def term_state(r):
    """WIRED / BARE / UNREAD for ONE `node_terms_uid` row.

    `tools/gscript.py:874` documents the ONE legitimate error pattern: a bare terminal returns `wire` 0 with
    `conn_err`/`wire_err` == 1055 and `name_err`/`src_err` == 0 - there is no wire to return a reference for.
    EVERYTHING ELSE beside a value is UNREAD (Pre-decided 14, `docs/cycle27-plan.md:147-150`: a value returned
    beside an error has measured nothing). No gate in this file accepts UNREAD."""
    ne, se = int(r.get("name_err") or 0), int(r.get("src_err") or 0)
    ce, we = int(r.get("conn_err") or 0), int(r.get("wire_err") or 0)
    w = int(r.get("wire") or 0)
    if w:
        return "UNREAD" if (ne or se or ce or we) else "WIRED"
    if ne or se:
        return "UNREAD"
    if (ce and ce != 1055) or (we and we != 1055):
        return "UNREAD"
    return "BARE"


def node_state(tag, target, uid, expect_owner=None, quiet=False):
    """The live state of ONE node, addressed BY uid and re-resolved at the call site (34(h) / 37(b)):
    owner -> Traverse Diagram index -> that diagram's `walk` -> the node's Nodes[] index -> terminal rows.
    Nothing is cached across a mutation; the Nodes[] index of `#48` was MEASURED to drift 11 -> 10 when `#3529`
    left the same diagram (`tools/bench/diag_movein_set.log:41` vs `:66`)."""
    rec = {"tag": tag, "uid": uid, "owner_class": None, "owner_uid": None, "diagram_index": None,
           "node_index": None, "label": None, "rows": None, "wired": None, "bare": None, "unread": None,
           "error": None}
    try:
        cls, own = owner_of(target, uid)
        rec["owner_class"], rec["owner_uid"] = cls, own
        di = diag_index(target, own)
        rec["diagram_index"] = di
        w = WALK(target, di, limit=90)
        if uid not in w:
            rec["error"] = ("#%d is NOT in AbstractDiagram.Nodes[] of its owner %s #%s (walk saw %d)"
                            % (uid, cls, own, len(w)))
        else:
            ni, label, rows = w[uid]
            rec["node_index"], rec["label"] = ni, label
            rec["rows"] = [{"i": r["i"], "name": r["name"], "is_source": r["is_source"], "wire": r["wire"],
                            "state": term_state(r), "name_err": r["name_err"], "src_err": r["src_err"],
                            "conn_err": r["conn_err"], "wire_err": r["wire_err"]} for r in rows]
            rec["wired"] = sum(1 for r in rec["rows"] if r["state"] == "WIRED")
            rec["bare"] = sum(1 for r in rec["rows"] if r["state"] == "BARE")
            rec["unread"] = sum(1 for r in rec["rows"] if r["state"] == "UNREAD")
    except Exception as e:                                                        # noqa: BLE001
        rec["error"] = "%s: %s" % (type(e).__name__, e)
    R["node_states"].append(rec)
    if rec["rows"] is None:
        fact("NODE %s #%d: NOT READ - %s" % (tag, uid, rec["error"]))
    elif not quiet:
        fact("NODE %s #%d (owner %s #%s, Diagram index %s, Nodes[%s], label %r): %d terminals - "
             "%d WIRED / %d BARE / %d UNREAD%s"
             % (tag, uid, rec["owner_class"], rec["owner_uid"], rec["diagram_index"], rec["node_index"],
                rec["label"], len(rec["rows"]), rec["wired"], rec["bare"], rec["unread"],
                "" if expect_owner is None else "  (expected owner Diagram #%d)" % expect_owner))
        for r in rec["rows"]:
            print(("        t%-2d %-30s src=%-5s wire=%-6s %-6s errs(n/s/c/w)=%d/%d/%d/%d"
                   % (r["i"], repr((r["name"] or ""))[:30], r["is_source"], r["wire"], r["state"],
                      r["name_err"], r["src_err"], r["conn_err"], r["wire_err"]))
                  .encode("ascii", "replace").decode("ascii"), flush=True)
    return rec


def term_index(rec, name, want_i, is_source=None):
    """The LIVE terminal index for a (name, recorded index) pair. The NAME is the address; `want_i` is only the
    fallback, and only when the name is absent or not unique (34(h): names are stable, indices drift)."""
    rows = rec.get("rows") or []
    m = [r["i"] for r in rows if r["name"] == name and (is_source is None or r["is_source"] == is_source)]
    if len(m) == 1:
        return m[0], "by name %r" % name
    if any(r["i"] == want_i for r in rows):
        return want_i, "by recorded index %d (name %r matched %d rows)" % (want_i, name, len(m))
    return None, "UNRESOLVED (name %r matched %d rows; index %d absent)" % (name, len(m), want_i)


def cond_read(tag, target, loop_uid):
    """ONE conditional-terminal readback through `OpLoopEndRef_v0`, scored on its FOUR per-property error
    columns as well as its values (Pre-decided 14; the instrument contract is `build_d1_v0.py:848-853`,
    re-exported at `build_opstopfromnode_v0.py:340-344`). A non-empty column makes the reading UNREAD."""
    li = [o["uid"] for o in g.report_all(target, "WhileLoop")].index(loop_uid)   # re-read at the call site
    r = LOOP_END_REF(target, li)
    e1, e2 = (r.get("err") or "").strip(), (r.get("errs") or "").strip()
    rec = {"tag": tag, "loop_uid": loop_uid, "loop_index": li, "cond_term_uid": r.get("cond_term_uid"),
           "cond_wire_uid": r.get("cond_wire_uid"), "is_source": r.get("is_source"), "err": e1, "errs": e2,
           "outcome": "UNREAD" if (e1 or e2) else "READ"}
    R["cond_reads"].append(rec)
    fact("COND %s: outcome %s - WhileLoop #%d (index %d) conditional terminal #%s, wire %s; err %r errs %r"
         % (tag, rec["outcome"], loop_uid, li, rec["cond_term_uid"], rec["cond_wire_uid"], e1[:100], e2[:100]))
    return rec


def census(tag, target):
    c = {k: g.count(target, k) for k in ("Diagram", "WhileLoop", "SubVI", "Comparison", "LoopTunnel", "Wire")}
    R.setdefault("censuses", {})[tag] = c
    fact("class census %s: %r" % (tag, c))
    return c


def load_rewire_rows():
    """The 17 `"dest": "1.5"` rows of the MEASURED cut-terminal table, straight from the file."""
    with open(REWIRE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    rows = [r for r in data.get("rows", []) if r.get("dest") == "1.5"]
    R["rewire_source_file"] = {"path": REWIRE_JSON, "cut_terminals": data.get("cut_terminals"),
                               "resolved": data.get("resolved"), "unresolved": data.get("unresolved"),
                               "rows_dest_1_5": len(rows)}
    return rows


# ============================================================================== PHASES
def phase_0_files():
    print("\n=== PHASE 0: files only, zero LabVIEW", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500)" % R["handles"]["before"])
    o = probe("G1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("G1 the ORIGINAL exists and its md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"))
    s = probe("G2 the S2 artefact BEFORE the copy", S2_ARTEFACT)
    gate("G2 D1_s2_loops.vi md5 == %s and size == %d B" % (S2_MD5, S2_SIZE),
         s.get("md5") == S2_MD5 and s.get("size") == str(S2_SIZE),
         "md5 %s size %s" % (s.get("md5"), s.get("size")))
    D.fresh("G2b")
    fact("handles after the restart: %r" % labview_handles())
    if os.path.exists(TARGET):
        os.remove(TARGET)
        fact("removed a pre-existing %s before the copy" % os.path.basename(TARGET))
    shutil.copy2(S2_ARTEFACT, TARGET)
    t = probe("G3 the target copy", TARGET)
    gate("G3 the target copy is byte-identical to the S2 artefact", t.get("md5") == S2_MD5, t.get("md5", "?"))
    dump("0-files")


def phase_1_baseline():
    print("\n=== PHASE 1: baseline census, loop identity, the set, and the measured rewire rows", flush=True)
    R["phases"]["1"] = {}
    before = census("BEFORE any edit", TARGET)
    R["before_census"] = before
    gate("G4 baseline census == the verified S2 numbers %r" % BASELINE,
         all(before[k] == v for k, v in BASELINE.items()), repr(before))

    # G5: loop identity BY OWNERSHIP TRAVERSAL, never by index (37(b)).
    cls_body, own_body = owner_of(TARGET, BODY_A_UID)
    cls_loop, own_loop = owner_of(TARGET, LOOP_A_UID)
    fact("loop a (Pre-decided 37(h), docs/cycle27-plan.md:1126-1131 - CITED): Diagram #%d's owner reads %s #%s; "
         "WhileLoop #%d's owner reads %s #%s" % (BODY_A_UID, cls_body, own_body, LOOP_A_UID, cls_loop, own_loop))
    R["phases"]["1"]["loop_a"] = {"loop_uid": LOOP_A_UID, "body_uid": BODY_A_UID, "body_owner": own_body,
                                  "body_owner_class": cls_body, "loop_owner": own_loop,
                                  "loop_owner_class": cls_loop}
    gate("G5 Diagram #%d is owned by WhileLoop #%d, which is owned by Diagram #%d"
         % (BODY_A_UID, LOOP_A_UID, SIBLING_DIAG_UID),
         own_body == LOOP_A_UID and own_loop == SIBLING_DIAG_UID,
         "body owner %s #%s; loop owner %s #%s" % (cls_body, own_body, cls_loop, own_loop))
    cond_read("loop a BEFORE the stage", TARGET, LOOP_A_UID)

    # G6/G7: the set, BEFORE. Every member's owner and wired-terminal count, read by uid.
    ok_owner, ok_wired, ok_unread = True, True, True
    states = {}
    for uid, name, wired, _pos, why in SET:
        st = node_state("BEFORE", TARGET, uid, expect_owner=FRAME_BODY_UID)
        states[uid] = st
        fact("set member #%d %r - %s" % (uid, name, why))
        ok_owner = ok_owner and st["owner_uid"] == FRAME_BODY_UID
        ok_wired = ok_wired and st["wired"] == wired
        ok_unread = ok_unread and st["unread"] == 0
    R["phases"]["1"]["before_states"] = {str(u): {k: states[u][k] for k in
                                                 ("owner_uid", "node_index", "wired", "bare", "unread")}
                                         for u in states}
    gate("G6 all five set members are owned by Diagram #%d (the frame body, 37(f)) before any edit"
         % FRAME_BODY_UID, ok_owner,
         repr({u: states[u]["owner_uid"] for u in states}))
    gate("G7 BEFORE wired-terminal counts are %r and ZERO rows read UNREAD (Pre-decided 14)" % PRE_MOVE_WIRED,
         ok_wired and ok_unread,
         repr({u: (states[u]["wired"], states[u]["unread"]) for u in states}))

    # G8: the measured rewire rows, CLASSIFIED BY MEASURING EACH SOURCE'S OWNER.
    rows = load_rewire_rows()
    fact("loaded %d rows with dest '1.5' from %s (file totals: %s cut / %s resolved / %s unresolved)"
         % (len(rows), os.path.basename(REWIRE_JSON), R["rewire_source_file"]["cut_terminals"],
            R["rewire_source_file"]["resolved"], R["rewire_source_file"]["unresolved"]))
    classified = []
    for r in rows:
        src = r.get("source") or {}
        kind, src_uid = src.get("kind"), src.get("uid")
        if kind == "sr":
            cls_row, owner = "shift-register", None
        elif kind == "tunnel":
            cls_row, owner = "cross-loop", None
        elif kind == "node" and src_uid is not None:
            _c, owner = owner_of(TARGET, int(src_uid))          # MEASURED, not assumed
            cls_row = "internal" if int(src_uid) in SET_UIDS else "cross-loop"
        elif r.get("action") == "source-side":
            cls_row, owner = "source-side (its sinks carry the row)", None
        else:
            cls_row, owner = "UNCLASSIFIED", None
        classified.append({"sink_uid": r.get("uid"), "i": r.get("i"), "name": r.get("name"),
                           "wire": r.get("wire"), "action": r.get("action"), "src_kind": kind,
                           "src_uid": src_uid, "src_owner_measured": owner, "class": cls_row})
    R["phases"]["1"]["rewire_rows"] = classified
    counts = {}
    for c in classified:
        counts[c["class"]] = counts.get(c["class"], 0) + 1
    for c in classified:
        fact("ROW sink #%s t%s %r wire %s action %r -> class %s (source kind %r uid %r, measured owner %r)"
             % (c["sink_uid"], c["i"], (c["name"] or "")[:34], c["wire"], c["action"], c["class"],
                c["src_kind"], c["src_uid"], c["src_owner_measured"]))
    gate("G8 the 17 dest-1.5 rows are classified BY MEASURING each source's owner: %r" % counts,
         True, "REPORTED - no expected value", fatal=False)
    dump("1-baseline")
    return states


def phase_2_move():
    print("\n=== PHASE 2: five `move_in` calls, ONE NODE PER CALL (37(d))", flush=True)
    fact("37(d), docs/cycle27-plan.md:1093-1100: `move_in` takes one uid per call and SEVERS every wire on the "
         "moved node in EITHER order. It is build_d1_v0.py:318, not in gscript.py. Measured: "
         "tools/bench/diag_movein_set.log:75 / :86 / :101.")
    for uid, name, wired, pos, _why in SET:
        bi = diag_index(TARGET, BODY_A_UID)          # re-read immediately before use (34(h))
        rec = {"uid": uid, "name": name, "body_diagram_uid": BODY_A_UID, "body_diagram_index": bi,
               "position": list(pos), "wired_before": wired}
        try:
            echoed = move_in(TARGET, uid, bi, pos)
            rec["echoed_uid"] = echoed
            fact("move #%d %r -> Diagram #%d [index %d] at %r; the op echoed uid %r (37(d): the echo is NOT the "
                 "moved object - both cycle-52 calls echoed 23035)" % (uid, name, BODY_A_UID, bi, pos, echoed))
        except Exception as e:                                                    # noqa: BLE001
            rec["error"] = "%s: %s" % (type(e).__name__, e)
            fact("move #%d RAISED %s: %s" % (uid, type(e).__name__, e))
        st = node_state("AFTER move #%d" % uid, TARGET, uid, expect_owner=BODY_A_UID)
        rec["after"] = {k: st[k] for k in ("owner_uid", "node_index", "wired", "bare", "unread")}
        R["moves"].append(rec)
        gate("G9 move #%d: the node is now owned by Diagram #%d and its wired count is 0 (severed, 37(d))"
             % (uid, BODY_A_UID),
             st["owner_uid"] == BODY_A_UID and st["wired"] == 0 and st["unread"] == 0,
             "owner %r wired %r bare %r unread %r" % (st["owner_uid"], st["wired"], st["bare"], st["unread"]))
        dump("2-move-%d" % uid)
    still = [u for u in SET_UIDS if (owner_of(TARGET, u)[1] == FRAME_BODY_UID)]
    gate("G10 Diagram #%d no longer owns any set member" % FRAME_BODY_UID, not still,
         "still on the frame body: %r" % still)
    R["after_moves_census"] = census("AFTER the five moves", TARGET)
    dump("2-move")


def phase_3_shift_regs():
    print("\n=== PHASE 3: two shift registers on loop a (`add_shift_reg`, gscript.py:673)", flush=True)
    fact("docs/d1-build-plan.md:368-369 names `add_shift_reg` + `wire_sr` as the route. The OLD pair on #637 "
         "(#4334/#4344, #4256/#4274) is NOT deleted by this stage - 37(g) names no deletion and "
         "`delete_object` on a shift register is unverified here. Their state is reported in PHASE 6.")
    for spec in SR_SPECS:
        li = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(LOOP_A_UID)   # re-read (34(h))
        rec = {"tag": spec["tag"], "loop_index": li, "why": spec["why"], "old_pair":
               [spec["old_right"], spec["old_left"]]}
        try:
            new_uid = g.add_shift_reg(TARGET, li, y_position=spec["y"])
            rec["new_right_uid"] = new_uid
            fact("SR %s: add_shift_reg(loop index %d, y=%d) -> new RightShiftRegister #%s"
                 % (spec["tag"], li, spec["y"], new_uid))
        except Exception as e:                                                    # noqa: BLE001
            rec["error"] = "%s: %s" % (type(e).__name__, e)
            fact("SR %s: add_shift_reg RAISED %s: %s" % (spec["tag"], type(e).__name__, e))
        rec["reg_index"] = len(R["shift_regs"])
        try:
            rd = g.shift_reg(TARGET, li, rec["reg_index"])
            rec["readback"] = rd
            fact("SR %s: shift_reg(loop %d, reg %d) reads uid %r class %r"
                 % (spec["tag"], li, rec["reg_index"], rd.get("uid"), rd.get("class")))
        except Exception as e:                                                    # noqa: BLE001
            rec["readback_error"] = "%s: %s" % (type(e).__name__, e)
            fact("SR %s: shift_reg readback RAISED %s: %s" % (spec["tag"], type(e).__name__, e))
        R["shift_regs"].append(rec)
        gate("G11 SR %s created on loop a and read back by uid" % spec["tag"],
             bool(rec.get("new_right_uid")) and rec.get("readback", {}).get("uid") == rec.get("new_right_uid"),
             "created %r; readback uid %r; errors %r / %r"
             % (rec.get("new_right_uid"), (rec.get("readback") or {}).get("uid"), rec.get("error"),
                rec.get("readback_error")))
        dump("3-sr-%s" % spec["tag"])


def _wire_one(job):
    """ONE re-wiring job. Every address is resolved NOW: owner -> diagram index -> Nodes[] index -> terminal
    index BY NAME. The pass criterion is the NODE terminal's own state (37(e): a wire count can never detect a
    cut, so nothing here counts wires).

    `job["sink_uid"]`/`["sink_name"]`/`["sink_t"]` always address the NODE SIDE of the job. For a `node` job
    that node side IS the sink. For a `sr` job it is the node that the register is wired to, and
    `gscript.wire_sr` `:717-722` decides the direction: `RightIn` takes the node's terminal as the SOURCE into
    the right register (so the terminal is `is_source` True), `LeftIn` feeds the left register's inside terminal
    INTO the node's terminal (so it is `is_source` False). Both variants need `node_index` + `term_index`."""
    kind = job["kind"]
    node_is_source = (kind == "sr" and job.get("variant") == "RightIn")
    sink_st = node_state("wire job %s node" % job["tag"], TARGET, job["sink_uid"], quiet=True)
    st_i, why_s = term_index(sink_st, job["sink_name"], job["sink_t"], is_source=node_is_source)
    job["sink_addr"] = {"diagram_index": sink_st["diagram_index"], "node_index": sink_st["node_index"],
                        "term_index": st_i, "resolved": why_s, "owner_uid": sink_st["owner_uid"],
                        "node_is_source": node_is_source}
    if st_i is None or sink_st["node_index"] is None:
        job["result"] = "NODE SIDE NOT ADDRESSABLE"
        return False
    if kind == "node":
        src_st = node_state("wire job %s src" % job["tag"], TARGET, job["src_uid"], quiet=True)
        sr_i, why_r = term_index(src_st, job["src_name"], job["src_t"], is_source=True)
        job["src_addr"] = {"diagram_index": src_st["diagram_index"], "node_index": src_st["node_index"],
                           "term_index": sr_i, "resolved": why_r, "owner_uid": src_st["owner_uid"]}
        if sr_i is None or src_st["node_index"] is None:
            job["result"] = "SOURCE NOT ADDRESSABLE"
            return False
        dw, es, err = CONNECT_V1(TARGET, sink_st["diagram_index"], sink_st["node_index"], st_i,
                                 src_st["diagram_index"], src_st["node_index"], sr_i, V1_LABELS)
        job["connect"] = {"wire_delta": dw, "exec_state": es, "error": str(err)[:160]}
    else:                                    # kind == "sr"
        li = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(LOOP_A_UID)   # re-read (34(h))
        try:
            # BOTH variants take the node address (gscript.py:742 writes index_node/index_term unconditionally
            # for every variant but `LeftOutCtl`); the variant alone decides which end is the source.
            g.wire_sr(job["variant"], TARGET, li, job["reg_index"],
                      node_index=sink_st["node_index"], term_index=st_i)
            job["connect"] = {"variant": job["variant"], "loop_index": li, "reg_index": job["reg_index"],
                              "node_index": sink_st["node_index"], "term_index": st_i}
        except Exception as e:                                                    # noqa: BLE001
            job["connect"] = {"variant": job["variant"], "error": "%s: %s" % (type(e).__name__, e)}
    after = node_state("wire job %s node AFTER" % job["tag"], TARGET, job["sink_uid"], quiet=True)
    row = next((r for r in (after["rows"] or []) if r["i"] == st_i), None)
    job["sink_after"] = row
    if not row or row["state"] != "WIRED":
        job["result"] = "NODE TERMINAL STILL %s" % (row["state"] if row else "UNREADABLE")
        return False
    job["wire_uid"] = row["wire"]
    if kind == "node":
        src_after = node_state("wire job %s src AFTER" % job["tag"], TARGET, job["src_uid"], quiet=True)
        srow = next((r for r in (src_after["rows"] or []) if r["i"] == job["src_addr"]["term_index"]), None)
        job["src_after"] = srow
        same = bool(srow) and srow["state"] == "WIRED" and srow["wire"] == row["wire"]
        job["result"] = "WIRED w%s (same uid on both ends: %s)" % (row["wire"], same)
        return same
    job["result"] = ("WIRED w%s (shift-register %s; the register's own terminal is not a Nodes[] row, so the "
                     "node side is the whole pass criterion here)" % (row["wire"], job["variant"]))
    return True


def phase_4_rewire():
    print("\n=== PHASE 4: re-wiring, in batches of %d rows, EVERY GATE COUNTING WIRED TERMINALS (37(e))"
          % BATCH_SIZE, flush=True)
    jobs = []
    for sink_uid, sink_name, sink_t, src_uid, src_name, src_t, ev in INTERNAL_JOBS:
        jobs.append({"tag": "int-%d.t%d" % (sink_uid, sink_t), "kind": "node", "sink_uid": sink_uid,
                     "sink_name": sink_name, "sink_t": sink_t, "src_uid": src_uid, "src_name": src_name,
                     "src_t": src_t, "evidence": ev})
    for k, spec in enumerate(SR_SPECS):
        ru, rn, rt = spec["right_in"]
        lu, ln, lt = spec["left_in"]
        jobs.append({"tag": "sr-%s-RightIn" % spec["tag"], "kind": "sr", "variant": "RightIn", "reg_index": k,
                     "sink_uid": ru, "sink_name": rn, "sink_t": rt, "evidence": spec["why"],
                     "note": "gscript.py:718 - the node's terminal is the SOURCE into the right register, so it "
                             "is looked up with is_source True and its own state is the pass criterion"})
        jobs.append({"tag": "sr-%s-LeftIn" % spec["tag"], "kind": "sr", "variant": "LeftIn", "reg_index": k,
                     "sink_uid": lu, "sink_name": ln, "sink_t": lt, "evidence": spec["why"]})
    fact("%d wirable jobs (%d internal wires + %d shift-register sides); batch size %d => %d batch(es). The "
         "three cross-loop rows and the one reverse crossing are NOT jobs - see PHASE 5."
         % (len(jobs), len(INTERNAL_JOBS), 2 * len(SR_SPECS), BATCH_SIZE,
            (len(jobs) + BATCH_SIZE - 1) // BATCH_SIZE))
    for b in range(0, len(jobs), BATCH_SIZE):
        batch = jobs[b:b + BATCH_SIZE]
        bn = b // BATCH_SIZE + 1
        print("\n--- batch %d: %d rows" % (bn, len(batch)), flush=True)
        for job in batch:
            ok = _wire_one(job)
            R["wire_jobs"].append(job)
            fact("JOB %s (%s): %s   [%s]" % (job["tag"], job["kind"], job.get("result"), job["evidence"]))
            gate("G12 batch %d job %s: the NODE terminal ends WIRED (and for a node-to-node job the SAME wire "
                 "uid reads back on the source)" % (bn, job["tag"]), ok,
                 "%s; node addr %r; connect %r" % (job.get("result"), job.get("sink_addr"), job.get("connect")))
        dump("4-rewire-batch%d" % bn)
    after = census("AFTER the re-wiring", TARGET)
    R["after_rewire_census"] = after
    for key in ("Wire", "LoopTunnel"):
        gate("G13 %s %d -> %d (delta %+d) - REPORTED, NO predicted value: 37(e) makes a wire count blind to a "
             "cut, and the LoopTunnel delta is whatever the border crossings require"
             % (key, BASELINE[key], after[key], after[key] - BASELINE[key]), True, "", fatal=False)
    dump("4-rewire")


def phase_5_cross():
    print("\n=== PHASE 5: the rows this stage CANNOT wire - measured, reported, never wired (X1)", flush=True)
    for row in CROSS_ROWS:
        rec = dict(row)
        if row["src_uid"] is not None:
            try:
                cls, own = owner_of(TARGET, int(row["src_uid"]))
                rec["src_owner_class"], rec["src_owner_uid"] = cls, own
                rec["src_inside_frame_loop"] = (own == FRAME_BODY_UID)
            except Exception as e:                                                # noqa: BLE001
                rec["owner_error"] = "%s: %s" % (type(e).__name__, e)
        R["cross_rows"].append(rec)
        fact("CROSS sink #%s t%s %r <- %r (uid %r): measured owner %s #%s; inside the frame loop body #%d: %r. "
             "[%s]" % (row["sink"], row["sink_t"], (row["sink_name"] or "")[:34], row["src_name"],
                       row["src_uid"], rec.get("src_owner_class"), rec.get("src_owner_uid"), FRAME_BODY_UID,
                       rec.get("src_inside_frame_loop"), row["evidence"]))
    rc = dict(REVERSE_CROSSING)
    try:
        cls, own = owner_of(TARGET, REVERSE_CROSSING["sink"])
        rc["sink_owner_class"], rc["sink_owner_uid"] = cls, own
    except Exception as e:                                                        # noqa: BLE001
        rc["owner_error"] = "%s: %s" % (type(e).__name__, e)
    R["reverse_crossing"] = rc
    fact("CROSS (reverse) #%d t%d -> #%d t%d (w%d): #%d's measured owner is %s #%s. [%s]"
         % (rc["src"], rc["src_t"], rc["sink"], rc["sink_t"], rc["wire"], rc["sink"],
            rc.get("sink_owner_class"), rc.get("sink_owner_uid"), rc["evidence"]))
    n_cross = sum(1 for r in R["cross_rows"] if r.get("src_inside_frame_loop") or r["src_uid"] is None)
    R["cross_unresolvable_count"] = n_cross
    gate("G14 %d of #10407's 7 cut rows have a source this stage does not move (MEASURED); they need the "
         "Q_focus path, which Pre-decided 36 defers BEHIND S3 - REPORTED, never wired" % n_cross,
         True, "", fatal=False)
    dump("5-cross")


def phase_6_acceptance():
    print("\n=== PHASE 6: the per-node WIRED-TERMINAL gates (37(e)) - never a wire count", flush=True)
    finals = {}
    for uid, name, wired, _pos, _why in SET:
        st = node_state("FINAL", TARGET, uid, expect_owner=BODY_A_UID)
        finals[uid] = st
    R["final_states"] = {str(u): {k: finals[u][k] for k in
                                  ("owner_uid", "node_index", "wired", "bare", "unread")} for u in finals}
    n_cross = R.get("cross_unresolvable_count", 0)
    for uid, name, wired, _pos, _why in SET:
        st = finals[uid]
        adjusted = wired - (n_cross if uid == 10407 else 0)
        line = ("W-%d %r: WIRED terminals %r of %d before the move (adjusted for the %d MEASURED cross-loop "
                "rows: %d); BARE %r; UNREAD %r" % (uid, name, st["wired"], wired,
                                                   n_cross if uid == 10407 else 0, adjusted, st["bare"],
                                                   st["unread"]))
        fact(line)
        gate("W-%d the wired-terminal count returns to its pre-move value %d with ZERO UNREAD rows" % (uid, wired),
             st["wired"] == wired and st["unread"] == 0,
             "observed %r wired / %r unread; adjusted target %d" % (st["wired"], st["unread"], adjusted))
    # the OLD shift-register pair on #637, reported (X2)
    for spec in SR_SPECS:
        for side in ("old_right", "old_left"):
            try:
                cls, own = owner_of(TARGET, spec[side])
                fact("OLD SR %s %s #%d: owner %s #%s (this stage does not delete it - 37(g) names no deletion)"
                     % (spec["tag"], side, spec[side], cls, own))
            except Exception as e:                                                # noqa: BLE001
                fact("OLD SR %s %s #%d: owner read RAISED %s: %s" % (spec["tag"], side, spec[side],
                                                                     type(e).__name__, e))
    cond_read("loop a AFTER the stage", TARGET, LOOP_A_UID)
    dump("6-acceptance")


def phase_7_save():
    print("\n=== PHASE 7: ExecState with the ORIGINAL preloaded (34(l)), then the ONE save", flush=True)
    es = D.read_state("pre_save_in_instance_preloaded", TARGET)
    R["readings"]["pre_save_in_instance_preloaded"] = es
    gate("G15 ExecState == 1 immediately before the save (1 = runnable, 0 = broken); PREDICTED 0, see (X2)",
         es == 1, "exec_state = %r" % es)
    _SAVE_ATTEMPTED[0] = True
    sv = D.try_save("s3", TARGET)
    R["saves"]["s3"] = sv
    gate("G16 ONE g.save() returned bytes with allow_broken=False (gui_save never called, 29(d))",
         sv["exception"] is None and sv["returned_bytes"],
         "exception %r returned %r" % (sv["exception"], sv["returned_bytes"]))
    dump("7-save")


def phase_8_verify():
    print("\n=== PHASE 8: the SAVED artefact - child-process ExecState, then the SubVI TABLE", flush=True)
    for tag, pre in (("S3-COLD", False), ("S3-PRELOAD", True)):
        try:
            res = D1ES.run_condition(tag, TARGET, pre)
            R["readings"][tag] = res.get("execstate")
            fact("CHILD %s (preload=%s): ExecState %r, rc %r"
                 % (tag, pre, res.get("execstate"), res.get("child_rc", res.get("rc"))))
        except Exception as e:                                                    # noqa: BLE001
            R["readings"][tag] = "RAISED %s: %s" % (type(e).__name__, e)
            fact("CHILD %s raised %s: %s" % (tag, type(e).__name__, e))
    gate("G17 the saved artefact reads COLD 1 / PRELOADED 1 in a fresh process (34(l))",
         R["readings"].get("S3-COLD") == 1 and R["readings"].get("S3-PRELOAD") == 1,
         "COLD %r PRELOADED %r" % (R["readings"].get("S3-COLD"), R["readings"].get("S3-PRELOAD")))
    probe("the saved artefact, final", TARGET)

    print("\n--- G18: the SubVI TABLE, move-aware (X3), against the ORIGINAL's COLD table", flush=True)
    g.reset()
    g._run.__defaults__ = _RUN_DEFAULTS_S1
    s3_tbl, s3_rec = cold_subvi_table("G18a-S3FOCUS-COLD", TARGET)
    orig_tbl, orig_rec = cold_subvi_table("G18b-ORIG-COLD", ORIGINAL)
    # The MOVE-AWARE expectation: #48's key carries the diagram uid (stage_d1_s1.py:389), so moving it MUST
    # re-key it. The new key is the owner this run actually measured for #48 in PHASE 6, never an assumption.
    moved_owner = None
    for st in reversed(R["node_states"]):
        if st["uid"] == 48 and st["tag"] == "FINAL":
            moved_owner = st["owner_uid"]
            break
    R["subvi_48_new_owner_measured"] = moved_owner
    expect_missing = {TIFF_SUBVI_KEY}
    reference = dict(orig_tbl)
    old48, new48 = (FRAME_BODY_UID, 48), (moved_owner, 48)
    rekeyed = False
    if moved_owner is not None and old48 in reference:
        reference[new48] = reference.pop(old48)
        rekeyed = True
    fact("G18 move-aware reference: #48's SubVI key %r re-keyed to %r (re-keyed: %s); the ONE deleted key stays "
         "%r = #22700 IMAQ Write TIFF File 2 (37(c), docs/cycle27-plan.md:1087-1092)"
         % (old48, new48, rekeyed, TIFF_SUBVI_KEY))
    cmp_move = compare_subvi_tables(s3_tbl, reference, expect_missing)
    cmp_lit = compare_subvi_tables(s3_tbl, orig_tbl, expect_missing)
    R["subvi_census"] = {"s3_artefact": s3_rec, "original": orig_rec}
    R["subvi_compare_move_aware"] = cmp_move
    R["subvi_compare_brief_literal"] = cmp_lit
    fact("G18 row counts: S3 artefact %s vs ORIGINAL %s (expected %d vs %d); bait directory %s"
         % (s3_rec["n_rows"], orig_rec["n_rows"], PIN_SUBVI_ROWS - 1, PIN_SUBVI_ROWS, BG_COPY))
    if not cmp_move["equal"]:
        log_table_diff("G18 move-aware: S3 artefact vs the re-keyed ORIGINAL", cmp_move)
    gate("G18r BRIEF-LITERAL comparison (expect_missing = {(639, 22700)} only): missing %d / extra %d / "
         "changed %d - REPORTED, and (X3) predicts it CANNOT be 0/0/0 once a SubVI changes diagrams"
         % (len(cmp_lit["missing"]), len(cmp_lit["extra"]), len(cmp_lit["changed"])), True, "", fatal=False)
    ok_a = cmp_move["equal"]
    ok_b = s3_rec["into_background_vis_copy"] == 0
    ok_c = s3_rec["empty_rows"] == 0
    gate("G18a the S3 table is EXACTLY the ORIGINAL's table minus (%d, %d) with #48 re-keyed, every surviving "
         "row identical in BOTH name and path" % TIFF_SUBVI_KEY, ok_a,
         "missing=%d extra=%d changed=%d not_deleted=%s bad_key=%s"
         % (len(cmp_move["missing"]), len(cmp_move["extra"]), len(cmp_move["changed"]), cmp_move["not_deleted"],
            cmp_move["expected_key_absent_from_reference"]), fatal=False)
    gate("G18b ZERO rows of the S3 table point into claudeDev\\background VIs_COPY\\", ok_b,
         "%d rows, first keys %s" % (s3_rec["into_background_vis_copy"], s3_rec["background_vis_copy_keys"]),
         fatal=False)
    gate("G18c no row of the S3 table has an empty name or an empty path", ok_c,
         "%d rows, first keys %s" % (s3_rec["empty_rows"], s3_rec["empty_keys"]), fatal=False)
    dump("8-verify")
    gate("G18 FATAL the saved S3 artefact's SubVI table is accepted against the ORIGINAL (a AND b AND c)",
         ok_a and ok_b and ok_c, "a=%s b=%s c=%s" % (ok_a, ok_b, ok_c))


def main():
    print("=== stage_d1_s3_focus  %s   (D1 S3, Pre-decided 37(g); NO VI IS RUN, 34(f); no new op)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    phase_0_files()
    with D.Preload("S3"):
        g.open_panel(TARGET)                 # required before ANY scripting edit (skill rule)
        time.sleep(1.0)
        phase_1_baseline()
        phase_2_move()
        phase_3_shift_regs()
        phase_4_rewire()
        phase_5_cross()
        phase_6_acceptance()
        phase_7_save()
        try:
            g.close_panel(TARGET)
        except Exception as e:                                                    # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    phase_8_verify()
    wl = g.count(TARGET, "WhileLoop")
    gate("G19 WhileLoop is still %d" % BASELINE["WhileLoop"], wl == BASELINE["WhileLoop"], "observed %d" % wl)


def salvage():
    """CLAUDE.md "a step is not done until it has left a file": if a FATAL gate stopped the run before PHASE 7,
    still attempt the ONE `g.save()` with `allow_broken` False. `gscript.save` refuses a broken VI by itself, so
    this can only ever leave a LEGAL file - and `_SAVE_ATTEMPTED` keeps `g.save()` to exactly one call (37(g))."""
    if _SAVE_ATTEMPTED[0]:
        return
    _SAVE_ATTEMPTED[0] = True
    print("\n--- SALVAGE: the run stopped before PHASE 7; attempting the ONE save anyway (allow_broken False)",
          flush=True)
    try:
        es = g.exec_state(TARGET)
        R["readings"]["salvage_exec_state"] = es
        fact("SALVAGE exec_state(%s) = %r (NOT under Preload - recorded as such)"
             % (os.path.basename(TARGET), es))
        sv = D.try_save("salvage", TARGET)
        R["saves"]["salvage"] = sv
    except Exception as e:                                                        # noqa: BLE001
        R["saves"]["salvage"] = {"exception": "%s: %s" % (type(e).__name__, e)}
        fact("SALVAGE raised %s: %s" % (type(e).__name__, e))


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at the first FATAL gate: %s" % s, flush=True)
        rc = 1
        salvage()
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("\nUNHANDLED %s: %s" % (type(e).__name__, e), flush=True)
        rc = 1
        salvage()
    finally:
        try:
            g.reset()
        except Exception:                                                         # noqa: BLE001
            pass
        refs = None
        try:
            refs = g.ref_counts()
        except Exception:                                                         # noqa: BLE001
            pass
        R["ref_counts_end"] = refs
        try:
            R["handles"]["after"] = labview_handles()
        except Exception:                                                         # noqa: BLE001
            R["handles"]["after"] = None
        print("\n--- close-out", flush=True)
        fact("refs at end: %r (every reference this script opened is closed by its opener)" % (refs,))
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"].get("after"), R["handles"].get("before")))
        gate("G20 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,), fatal=False)
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy.vi", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops.vi", S2_ARTEFACT, S2_MD5)):
            d = probe("G21 %s after the run" % tag, path)
            R.setdefault("untouched", {})[tag] = d.get("md5")
            if d.get("md5") != pin:
                gate("G21 %s md5 unchanged" % tag, False, "%s != %s" % (d.get("md5"), pin), fatal=False)
                rc = 1
            else:
                gate("G21 %s md5 unchanged" % tag, True, d.get("md5", "?"), fatal=False)
        dump("close-out")
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== ARTEFACT: %s" % TARGET, flush=True)
        print("=== NO VI WAS RUN (34(f)); no new op; no motor, no ASI, no camera, no GUI action.", flush=True)
        sys.exit(rc)
