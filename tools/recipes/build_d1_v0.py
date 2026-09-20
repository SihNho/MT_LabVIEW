r"""build_d1_v0.py - D1: rows 1.1 / 1.2 / 1.5 / 1.7 / 1.8 / 1.9 built inside a COPY of the original.

ONE script, one bgrun, one log (CLAUDE.md "usage discipline": build -> gates -> bookkeeping in a single runner).
Written from `docs/d1-build-plan.md` REV 4; every section reference below is to that file.

    MATERIAL=1 py tools/bgrun.py --max-min 45 --log tools/bench/build_d1_v0.log \
        -- py -u tools/recipes/build_d1_v0.py

===============================================================================================================
THE TRANSPORT IS DECIDED - plan s11c (judgement session, 2026-09-17): QUEUES ONLY.  s0-BLOCKER RESOLVED.
===============================================================================================================
  * 1.5's wake-up      = a 1-ELEMENT DBL queue `Q_focus`. 1.2 owns the frame counter, evaluates the 25-frame
                         cadence and enqueues the slice index ON A TICK ONLY, TIMEOUT 0 (full => skip, never
                         blocks the frame path - rule 1c by construction).
  * the reverse crossing = `#12589` STAYS ON 1.1 (plan s11.3 resolved). 1.5 writes `#10407` t6's value into a
                         1-ELEMENT queue `Q_focusback`; 1.1 POLLS it with TIMEOUT 0 into `#12589` t1.
  * the stop of 1.2/1.5/1.7 = END-OF-STREAM SENTINELS on the queues they already consume
                         (`stage2-assembly-step-c.md:45`, `frame-ownership-design.md:102-103`). No second reader
                         of `stop (end)`, so `ControlTerminal #642` stays in 1.1 and NO `Local` is needed.
  * Local / user event / DVR: NOT used in D1 (measured alternatives, not refuted).

SENTINEL ENCODING (plan s9a) - a value the kernel can never produce, and THE WRITER MUST NOT WRITE IT:
  Q_meta / Q_rmeta / Q_focus -> buffer number / slice index  **-1**   (both are indices >= 0)
  Q_res / Q_good             -> an **empty array**                    (the kernel always returns >= 1 element)
  1.7 tests the dequeued Q_rmeta value BEFORE appending: -1 => exit, append nothing, extend nothing, drain,
  then call `#6384`.

===============================================================================================================
WHAT THIS FILE BUILDS TODAY, AND WHAT IT DOES NOT - measured against the fleet, 2026-09-17
===============================================================================================================
PHASE "relocate" (implemented, and what this run executes): the STRUCTURAL relocation - 3 loops, 20 node moves,
the seam swap, and the S3b census diff that IS the re-wire list. It does NOT save and does NOT cold-open: the
moves CUT border wires (plan s2b), so the artefact is deliberately not persisted.

PHASE "full" (NOT implemented - `NotImplementedError`, naming the gap): the connective tissue. Two of its three
parts have a built route and are only unwritten; ONE HAS NO ROUTE AT ALL and is a judgement call:
  (a) 8 queues + enqueue/dequeue + element wiring + tunnels + SR wiring + ControlTerminal moves + exit_while
      -> every op EXISTS and is verified (`queue_node`, `wire`, `set_index_mode`, `add_shift_reg`/`wire_sr`,
         `move_in`, `exit_while`); the pattern is `tools/recipes/build_track_v6_queue.py` (162/162). UNWRITTEN.
  (b) the LITERALS (queue bounds 20 / 1, timeout 0, sentinel -1) - `create_control` is the only value placer in
      the fleet and it ADDS A PANEL CONTROL, which contradicts the plan's own "ControlTerminal still 114".
      `Terminal.Create Constant` 6349C00 is CATALOGUED ONLY (`docs/NAMES.md:213`) and an op for it is a NEW op,
      frozen by `docs/cycle15-plan.md:104`. BUT a route exists with BUILT ops: the original itself carries donor
      constants of exactly the needed values (`tools/bench/opconstvaluen_scan.json`, 180 numerics:
      value 0 x69, 1 x36, 20 x2 (uid 451 rep 1, uid 16022 rep 3), -1 x1 (uid 4609 rep 3), 25 x1 (uid 25175)),
      so `copy_by_index` (row 39, verified on built-in primitives) + `move_in` (12/0) places them with no new op.
      MEASURED, UNWRITTEN - see CONST_DONORS below.
  (c) plan s7.1's STREAMING TSV WRITE has NO construction route: placing a file-I/O primitive needs either
      `New VI Object` (the skill's own line: "cannot create most node types (error 1054)") or a donor copy, and
      no donor in this project holds an open/write/close chain. This is the ONE thing D1 cannot build today.

===============================================================================================================
WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md "before creating any new op/tool/recipe")
===============================================================================================================
  * `OpMoveIn_v0.vi` - BUILT, ExecState 1, UID control label 'UID 3' (STATUS OPEN 19b; plan s2b 12/0). Reparents
    a plain node, a CaseStructure WITH ITS FRAMES, and a ControlTerminal (plan s2c 9/0). `move_in()` here is
    `tools/recipes/probe_move_ctlterm_v0.py:160-178` verbatim, not a re-implementation.
  * `OpOwnerChain_v1` / `read_owner` - any uid -> its owner, with the five error columns and the identity echo
    (`archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:29`). Imported.
  * `OpLoopEndRef_v0` - a While loop's CONDITIONAL TERMINAL, 16/0; S4 is the gate spec decision 5 was built for.
  * queues: `g.queue_node(obtain|enqueue|dequeue|release, ...)`; loops: `g.loop_in('while', ...)`;
    registers: `g.add_shift_reg` + `g.wire_sr`; tunnels: `g.tunnels` + `g.set_index_mode`;
    stop: `g.exit_while`; subVI: `g.drop_subvi`; delete: `g.delete_object`;
    readers: `g.report_all`, `g.node_terms_uid`, `g.panel_wiring`, `g.new_since`, `g.count`, `g.uids`.
    All in `docs/toolkit-capabilities.md`.
  * `build_track_v6_core.walk()/term()` - the (name, is_source) terminal readers. NEVER key a terminal by name
    alone (`archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:24-29`).
  * `tools/bench/bench_prep.labview_handles()` - the number HANDLE_LIMIT and STATUS OPEN 23 are stated against.
  * the BEFORE census: `tools/bench/d1_step0_census.json` (47 nodes on diagram 43, 5 on 19, 132 tunnels,
    14 shift registers, 114 panel rows, 10 OpWireSource_v5 answers). S3b diffs against it.
  * `net_map` is NOT used (truncating walker, `tools/gscript.py:2352-2355`), and because REMOVING it also removes
    its junk-Invoke purge side effect (`build_opownerchain_v1.py:231-243`), S5 purges explicitly.

===============================================================================================================
PREDICTION CONTRACT  (plan s10; counts are the ones a machine checks)
===============================================================================================================
PHASE "relocate" runs S0 S1 S2 S3 S3b S3c(create only) S3d(read) S4(read) and STOPS - no save, no cold re-open.
S1q/S3c-wiring/S4b-write/S4s/S5/S6 belong to PHASE "full" and are NOT executed; each is marked SKIPPED-PHASE in
the log so no gate silently passes by absence.

 S0  TRANSPORT is a mechanism with a creator in the fleet -> "queue" (plan s11c). Original md5
     2a78e17c449cacdaf5da389818526859 read BEFORE. `OpMoveIn_v0.vi` present. LabVIEW handles recorded.
 S1  the D1 target is a fresh copy of the original and opens with, BEFORE any edit:
     Diagram 171, Node 626, Wire 1902, LoopTunnel 132, ControlTerminal 114, WhileLoop 3, Local 8.
     (ExecState is NOT gated - a headless copy of the original reads 0, plan s2b.)
 S2  three new While loops on Diagram #686 (Traverse index 19): WhileLoop 3 -> 6, Diagram 171 -> 174;
     #637 still exists and still owns #6810 and CaseStructure #22082 (#22700 is DELETED by S1t, plan s11h).
 S1t (plan s11h) the FIXTURE TIFF writer is deleted BEFORE any move: #22700 and #23020 gone, no staying node
     left with a bare named input, ExecState unchanged. The true original has neither node - measured
     read-only at SubVI 97 / Function 179 / Node 622 vs the working copy's 98 / 181 / 626
     (tools/bench/diag_true_original_tiff.log, 6/0, both md5s unchanged).
 S1q (PHASE full) 8 queues obtained: Q_free/Q_work bounded 20, Q_meta/Q_res/Q_good/Q_rmeta unbounded,
     Q_focus and Q_focusback bounded 1; Local still 8 (no Local, no user event, no DVR is created).
 S3  23 objects reparented (17 -> 1.2, 5 -> 1.5, 1 -> 1.7; plan s11c keeps #12589 on 1.1, and plan s5a lists 18
     rows under 1.2 because #5058 is one of them and it is DELETED, not moved; the 5 on 1.5 are #10407, #48 and
     the three CONTROL REFERENCES #3529/#3560/#3447 that plan s11e.3 added as move rows), each verified by
     OpOwnerChain_v1
     as uid -> <that loop's body Diagram> -> <that WhileLoop>; #12589, #11639 and ControlTerminal #642 still
     owned by Diagram#639; Diagram count unchanged BY THE MOVES;
     #5058 deleted and GPU_kernel_v1.vi dropped into 1.2 (SubVI 98 -> 98).
 S3b the census diff IS the re-wire list (s11a.2): node_terms of every moving node before and after; the set
     that went wired->bare must be a SUPERSET of s8's 13 crossings, and every member must be re-wired
     (tunnel, queue or shift register). Gate: wires cut == wires re-wired.
 S3c 8 shift registers created and wired (4 on 1.2, 2 on 1.5, 2 on 1.7); 6 ControlTerminals reparented into
     1.2; ControlTerminal still 114; all 114 panel_wiring labels present.
 S3d the 6 whole-array seam inputs cross NON-INDEXED: tunnels() reports IndexMode 0 for `cross size`,
     `# of bead 4 packs`, `4 pack remainder`, `Array of cal clusters`, `Real-space cosine window`,
     `Cosine bandpass\nfor Hilbert `.
 S4  (relocate) OpLoopEndRef_v0 still reads #637 -> terminal 648, wire 3457, source #11639, and each new loop's
     conditional terminal reads back as UNWRITTEN (wire 0) - the honest state after a relocation-only phase.
     (full) each new loop's conditional terminal is driven by its own sentinel test.
 S4s (PHASE full) the sentinel enqueues exist with the literal element (-1 / empty array); 1.7's append is gated
     by the -1 test; no new panel object (ControlTerminal 114, Local 8).
 S5  junk Invokes purged (new_since('Invoke') empty), remove_bad_wires_scripted, ExecState 1 WARM, saved,
     file size recorded.
 S6  cold re-open in a restarted LabVIEW: ExecState 1, Diagram 174, WhileLoop 6, ControlTerminal 114;
     original md5 unchanged AFTER.

ExecState is meaningless between S2 and S4 - the moves CUT border wires (plan s2b: Wire -7, LoopTunnel -2 for
two moves). It is read at S5 and S6 only, and never used as a progress signal.

FAILURE BUDGET 2 (CLAUDE.md s3): any gate failing stops the run and reports. No repair pass, no second
construction inside the same run.
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
import gscript as g                                      # noqa: E402
import build_track_v6_core as B                          # noqa: E402
from bench_prep import labview_handles                   # noqa: E402
from build_opownerchain_v1 import read_owner             # noqa: E402
from build_opownerchain_v1 import OP as OP_OWNER         # noqa: E402
# The THIRD op (plan §11j.1), BUILT and functional 22/0 (tools/bench/build_opcreateconstonterm_v0.log):
# `Terminal.Create Constant` 6349C00 on a BODY node's terminal -> a typed constant, already wired, carrying the
# value passed in. Imported, never re-implemented.
from build_opcreateconstonterm_v0 import create_const_on_term as CONST_ON_TERM   # noqa: E402
# The FOURTH op (plan §11p.1 / §11q.1), BUILT and SAVED 2026-09-17, ExecState 1 warm AND cold, functional test
# 7/0 (tools/bench/test_opconnectnested_v1_cold.log): `Terminal.Connect Wire` 6349C03 with BOTH ends addressed
# as Diagram[d].Nodes[n].Terminals[t] on TWO DIFFERENT nested diagrams; LabVIEW creates the tunnels itself
# (LoopTunnel 0 -> 2 in the test). Used here for every row whose end HAS NO NAME, which is what 5001 means.
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1              # noqa: E402

# ---------------------------------------------------------------------------- THE DECISION (plan s11c)
# Set by the judgement session 2026-09-17: QUEUES ONLY. S0 still checks that the chosen mechanism has a CREATOR
# in the fleet today, so this is a decision the machine re-verifies rather than a comment.
TRANSPORT = "queue"

# PHASE "relocate" = the structural relocation, implemented below and executed by default.
# PHASE "full"     = relocate + the connective tissue; NOT written (see the header). `--full` raises, naming it.
PHASE = "relocate"

# A gate may NEVER be keyed to "impossible" (rev-4 review A1: this project formally withdrew exactly that claim
# about `Local` on 2026-09-17, `archive/peer/2026-09-17-priorart-ctlterm-move.md:601-608`, and rev 4 reinstated it
# here). So each row says only what has a CREATOR TODAY - a fact about the fleet's contents - and S0 refuses on
# "not decided" or "creator not built yet", never on a capability claim.
#   mechanism -> (gscript attribute that must exist, what is on disk right now)
TRANSPORT_CREATORS = {
    "queue":      ("queue_node", "OpQueueObtain/Enqueue/Dequeue/Release_v0 - EXERCISED, core 162/162"),
    "queue1":     ("queue_node", "the same four ops, bound to 1 element = the project's own recorded latest-value "
                                 "transport (restructure-plan-4.6.md:55 'local variable / 1-element queue')"),
    "user_event": ("user_event", "UNEXERCISED: vi.lib\\Erdos Miller\\LV-Scripting ships Create Create/Generate/"
                                 "Register for/Unregister for/Destroy User Event + Create Event Structure - the "
                                 "same folder the queue ops were wrapped from. No op wraps them YET."),
    "dvr":        ("dvr_node", "UNEXERCISED: Create New DVR / In Place Element DVR / Delete DVR on disk; no op YET"),
    "local":      ("create_local", "no creator on disk and none in the donor library; the route is seed + creator "
                                   "+ a `Control Name` writer (the OpSetIndexMode_v0/OpSetLabel_v0 shape). "
                                   "UNMEASURED, NOT impossible."),
}

# ---------------------------------------------------------------------------- constants, all measured
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
CLAUDEDEV = g.CLAUDEDEV
# A UNIQUE WORKING-COPY NAME PER RUN. Measured, run 3 (build_d1_v0_run3.log): the file on this path was deleted
# and re-copied from the md5-verified original, and the census still read run 2's EDITED state
# (Diagram 173, Node 630, WhileLoop 6) - run 2 failed at S3 and returned WITHOUT closing the target, so LabVIEW
# served the VI from MEMORY and the disk overwrite was invisible. The project already recorded this class
# (`archive/peer/2026-09-17-moveinto-stale-in-memory-vi.md`; STATUS "START HERE" 4; plan s2a's gate P1z) and its
# remedy is exactly this: a uniquely named copy per run, created and deleted in the same run.
RUN_STAMP = time.strftime("%H%M%S")
TARGET = os.path.join(CLAUDEDEV, f"Track_v6_D1_GPU_{RUN_STAMP}.vi" if PHASE != "full"
                      else "Track_v6_D1_GPU.vi")
OPIN = os.path.join(CLAUDEDEV, "OpMoveIn_v0.vi")
UID_LABEL = "UID 3"                                      # STATUS OPEN 19b, measured when OpMoveIn_v0 was built
GPU_KERNEL = os.path.join(CLAUDEDEV, "GPU_kernel_v1.vi")
LABELS = os.path.join(ROOT, "tools", "bench", "opwiresource_v5_labels.json")
CENSUS = os.path.join(ROOT, "tools", "bench", "d1_step0_census.json")
OUT = os.path.join(ROOT, "tools", "bench", "build_d1_v0.json")
CONST_LABELS_PATH = os.path.join(ROOT, "tools", "bench", "opcreateconstonterm_labels.json")
CONST_LABELS = (json.load(open(CONST_LABELS_PATH, encoding="utf-8"))
                if os.path.exists(CONST_LABELS_PATH) else None)
V1_LABELS_PATH = os.path.join(ROOT, "tools", "bench", "opconnectnested_v1_labels.json")
V1_LABELS = (json.load(open(V1_LABELS_PATH, encoding="utf-8"))
             if os.path.exists(V1_LABELS_PATH) else None)
# MEASURED 2026-09-17, tools/bench/diag_tunnelsource_onehop.log (7 pass / 2 fail) + d1_tunnel_sources.json: the
# one-hop read of §11r, run on the real VI. Of the 18 `from-tunnel` rows, the OUTER wire's single source terminal
# is owned by a **FlatSequenceInnerTunnel** in 14 rows, by a **LeftShiftRegister of #637** in 2, and by a NODE
# (`SubVI #27605`, diagram 19) in 1; one row does not advance. Only the NODE case is addressable as
# Diagram[].Nodes[].Terminals[], so only it is routed through OpConnectNested_v1 - the rest are reported with the
# MEASURED owner class instead of run 7's literal "further out through more unnamed tunnels" (prior-art A3).
TUNNEL_SOURCES_PATH = os.path.join(ROOT, "tools", "bench", "d1_tunnel_sources.json")
TUNNEL_SOURCES = {}
if os.path.exists(TUNNEL_SOURCES_PATH):
    for _r in json.load(open(TUNNEL_SOURCES_PATH, encoding="utf-8")).get("rows", []):
        TUNNEL_SOURCES[(_r["sink_uid"], _r["sink_term"])] = _r

SIBLING_DIAG_UID = 686        # the FlatSequenceFrame diagram that HOLDS WhileLoop #637 (main-vi-stop-and-save s0)
FRAME_LOOP_UID = 637
FRAME_BODY_UID = 639
KERNEL_UID = 5058             # the seam - DELETED, replaced by GPU_kernel_v1.vi
CTLTERM_STOP_UID = 642        # the ONE `stop (end)` ControlTerminal (control uid 7) - s11c: it STAYS in 1.1
COND_TERM_UID = 648           # #637's conditional terminal (OpLoopEndRef_v0, 16/0)
COND_WIRE_UID = 3457
COND_SRC_UID = 11639

# BEFORE counts - the whole-VI census the build asserts at S1 (plan s10 / d1_step0_census.json)
# Diagram was 171 here and in plan s10's S1 row. MEASURED WRONG, run 1 (build_d1_v0.log 07:13): a fresh copy of
# the md5-verified original reads Diagram **170**, with all seven other classes matching exactly. The 171 is a
# transcription of the probe's POST-loop-creation number: probe_move_into_v0.log:217 "scratch copy: Node 626,
# Diagram 170", then :220 creates a While loop (+1 Diagram), then :227 "Diagram count 171 -> 171". So the
# pre-edit truth is 170 and every derived expectation drops by one (S2: 170 -> 173, S6: 173).
BEFORE = dict(Diagram=170, Node=626, Wire=1902, LoopTunnel=132, ControlTerminal=114, WhileLoop=3, Local=8,
              SubVI=98)
# EXPECT = BEFORE, adjusted by the edits this run makes before a gate reads it. S1t (plan §11h) deletes the
# FIXTURE TIFF writer, so `SubVI` is one lower from that point on and the seam gate must not read the pre-delete
# number. Keeping BEFORE immutable keeps S1's census honest.
EXPECT = dict(BEFORE)

# plan s5a + s11c + s11e.3 - the move table, by census key. 23 moves + 1 delete (#5058) + 1 drop (GPU_kernel_v1).
# #12589 is NOT here: s11c keeps it on 1.1 so w12070 -> #11639 is never cut (s11.3 resolved).
#
# s11e.3 (judgement, 2026-09-17, from rev4c prior-art A3): #3447 `Focus Step (F1)`, #3529 `- Inc (PgDn)` and
# #3560 `+ Inc (PgUp)` are CONTROL REFERENCES, not Locals (main-vi-panel-map.md:403,:409-419;
# camera-acquisition-facts.md:333-334), and each goes WHERE ITS MEASURED CONSUMER GOES. Measured consumer:
# `#48 ASI_adjust focus-subvi.vi` t0/t1/t2 by wires 4833 / 2819 / 1893 (d1_step0_census.json.focus_other_inputs;
# run 4's own cut list confirms all three went wired->bare when #48 moved). #48 -> 1.5, so these -> 1.5.
# They are NOT `Diagram.Nodes[]` members (a Constant is a GObject, not a Node), which is exactly why the
# 47-node diagram-43 census never listed them and s5a had no row for them. `move_in` addresses by UID through
# `UID to GObject Reference.vi`, so the class does not enter the call.
CTLREF_TO_15 = [3529, 3560, 3447]
MOVE_TABLE = {
    "1.2": [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 1359, 2222, 2626, 6104, 8885, 9833,
            11261, 29874, 10686],
    "1.5": [10407, 48] + CTLREF_TO_15,
    "1.7": [376],
}
# plan s11c - what must STILL be owned by the frame loop body after the moves, because the stop paths stay whole
# #22700 was REMOVED from this list 2026-09-17 (plan §11h): S1t DELETES it, so asking afterwards whether it is
# "still owned by the frame loop body" is a stale gate, not a check. Run 6 measured exactly that - the only
# failure in 57, and the owner read echoed `'SubVI'#6810` because a deleted uid resolves to whatever now sits at
# that Traverse position. #23020/#23175/#22703 were never in this list.
STAY_ON_11 = [6810, 22082, 12589, 11639]

# plan s9 - the EIGHT queues and their bounds. PHASE "full" obtains them; PHASE "relocate" only records the plan.
QUEUES = {
    "Q_free": 20, "Q_work": 20,            # the image-refnum pool (decisions.md:22)
    "Q_meta": 0,                           # 0 = unbounded
    "Q_res": 0, "Q_good": 0, "Q_rmeta": 0,
    "Q_focus": 1,                          # s11c: 1.5's wake-up, written by 1.2 on the tick, timeout 0
    "Q_focusback": 1,                      # s11c: the reverse crossing, polled by 1.1 with timeout 0
}
# plan s9a - the sentinel encoding. A value the kernel can never produce; the writer must not write the row.
SENTINELS = {"Q_meta": -1, "Q_rmeta": -1, "Q_focus": -1, "Q_res": "empty array", "Q_good": "empty array"}
# the literals PHASE "full" needs, and the DONOR CONSTANTS in the original that carry them
# (tools/bench/opconstvaluen_scan.json, 180 numerics; copy_by_index + move_in, both built ops, no new op).
CONST_DONORS = {0: 3130, 1: 3683, 20: 451, -1: 4609, 25: 25175}
# plan s5d - the ControlTerminals that move into 1.2 with the nodes that read them. Identified by EFFECT
# (the panel_wiring row whose connected wire changes), never by a uid->control lookup, which does not exist.
CTLTERM_CONTROLS_12 = ["Auto-Reset", "Reset Tracking", "Z/dZ", "Correction Factor", "min value",
                       "Force (pN) vs Extension (nm) "]

# plan s5c - the 8 registers that move, by their RIGHT/LEFT uids in the original
SHIFT_REGS = {
    "1.2": [(1147, 1142, "x,y,z array out"), (5796, 5805, "Bead is good? array out"),
            (119, 2972, "pos in cal image out"), (7311, 11001, "Value")],
    "1.5": [(4256, 4274, "position [internal units]"), (4334, 4344, "VISA out  <- THE VISA SESSION")],
    "1.7": [(15, 51, "total data array out"), (24, 1108, "error out")],
}

# plan s8 - the 6 whole-array seam inputs that must cross NON-INDEXED (IndexMode 0)
NON_INDEXED = ["cross size", "# of bead 4 packs", "4 pack remainder", "Array of cal clusters",
               "Real-space cosine window", "Cosine bandpass\nfor Hilbert "]
# plan s8 - the 13 wired crossings the census diff must at least contain
EXPECTED_CROSSINGS = [5637, 3040, 373, 5859, 505, 5975, 121, 42, 3512, 3646, 7429, 3912, 4027]

passes, fails, facts = [], [], []
_OL = None


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
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


def move_in(target, uid, dest_diagram_index, position):
    """probe_move_ctlterm_v0.py:160-178 verbatim. The Move returns NO reference to the object at its new home
    (archive/peer/2026-08-28-copy-nodes-between-vis.md:51), so every check afterwards is a uid-addressed re-read."""
    g.ensure_loaded(target)
    vi = g.op(OPIN)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", int(dest_diagram_index))
    vi.SetControlValue("index 2", 0)
    vi.SetControlValue("index 3", 0)
    vi.SetControlValue("error in (no error)", (False, 0, ""))
    vi.SetControlValue("error in", (True, 1, "neutralised creator"))
    vi.SetControlValue("Class Name 3", "")
    vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue(UID_LABEL, int(uid))
    vi.SetControlValue("position", tuple(int(v) for v in position))
    g._run(vi)
    return int(vi.GetControlValue("UID"))


def owner_of(target, uid, strict=True):
    global _OL
    if _OL is None:
        with open(LABELS, encoding="utf-8") as f:
            _OL = json.load(f)
    import build_opownerchain_v1 as OB
    vi = g.op(OP_OWNER)
    saved = OB.MAIN
    try:
        OB.MAIN = target
        r = read_owner(vi, _OL, uid)
    finally:
        OB.MAIN = saved
    if strict and (r["uid_back"] != int(uid) or r["errs"]):
        raise RuntimeError(f"owner_of({uid}) is not an answer: echoed {r['cls_back']!r}#{r['uid_back']}, "
                           f"errors {r['errs'][:120]!r}")
    return r["ownercls"], r["owner_uid"]


def diag_index(target, uid):
    return [o["uid"] for o in g.report_all(target, "Diagram")].index(uid)


_WALKS = {}


def wmap(target, diagram_index, fresh=False):
    """ONE `build_track_v6_core.walk` per diagram, cached. `walk` is `node_labels` + up to 80 `node_terms_uid`
    calls (~0.8 s each), so the previous per-node `terms_of` cost a FULL diagram walk per node: 30 nodes of
    diagram 43 would have been ~30 x 40 s PER PASS, twice - past this run's bgrun deadline before the first
    gate. Mutations invalidate it explicitly (`fresh=True`), never by guesswork."""
    key = (target, int(diagram_index))
    if fresh or key not in _WALKS:
        _WALKS[key] = B.walk(target, diagram_index)
    return _WALKS[key]


def terms_of(target, diagram_index, uid, fresh=False):
    """{term index: (name, is_source, wire)} for one node, out of the cached walk of its diagram."""
    rec = wmap(target, diagram_index, fresh).get(int(uid))
    if not rec:
        return {}
    return {r["i"]: (r["name"], r["is_source"], r["wire"]) for r in rec[2]}


def sr_census(target, loop_index, n_regs=14):
    """Every shift register of one While loop: its OUTSIDE wire (the final value that LEAVES the loop) and its
    INSIDE wire (the body's source). Added 2026-09-17 for prior-art finding A1
    (`archive/peer/2026-09-17-priorart-priorart-d1-build-rev4b.md`): the S3b census walks DIAGRAMS, and a shift
    register is not a node on one, so the register whose body source a move CUTS is invisible to it. A1's
    measured case: `#4256 position [internal units]` is fed by `#10407` t6 (w9113) - a node that MOVES to 1.5 -
    and its final value is the sole feed of `Focus position` on `#7202 Global motor pos.vi`, on DIAGRAM 19
    (`frame-loop-wire-graph.md:410,:424`, `main-vi-state.md:44,:89-91,:130-131`,
    `restructure-plan-4.6.md:348,:354` - "no field of Global motor pos.vi gains a second writing loop")."""
    out = {}
    for r in range(n_regs):
        try:
            right = g.shift_reg(target, loop_index, r, "WhileLoop")
            out[right.get("uid") or f"reg{r}"] = dict(
                out_wire=right["out"]["wire"], in_wires=[t["wire"] for t in right["inside"]],
                errors=right.get("errors"), i=r)
        except Exception as e:
            out[f"reg{r}"] = dict(error=str(e)[:80], i=r)
    return out


# ============================================================================== S0
def s0():
    print("\n=== S0: preconditions", flush=True)
    m0 = md5(ORIGINAL)
    if not gate("S0a original md5 BEFORE", m0 == ORIG_MD5, m0):
        return None
    if not gate("S0b OpMoveIn_v0.vi present", os.path.exists(OPIN), OPIN):
        return None
    if not gate("S0c GPU_kernel_v1.vi present", os.path.exists(GPU_KERNEL), GPU_KERNEL):
        return None
    h0 = labview_handles()
    fact(f"LabVIEW handles before: {h0} (fresh-instance baseline ~31,500)")

    if TRANSPORT is None:
        gate("S0d the cross-loop TRANSPORT is decided", False,
             "TRANSPORT is None - NOT 'impossible', UNDECIDED. docs/d1-build-plan.md s0-BLOCKER: s11b.1 decided "
             "LOCAL variables and no Local creator exists TODAY (97 gscript functions, 97 op VIs, no "
             "vi-server-ids entry, no Create Local.vi in the donor library, no donor Local bound to stop (end)/a "
             "slice index/a counter). Whether one CAN be built is unmeasured. Four candidates are on disk - "
             "queue (exercised), 1-element queue (the project's own latest-value transport), user event and DVR "
             "(present in vi.lib\\Erdos Miller\\LV-Scripting, unexercised). The choice settles 1.5's wake-up, the "
             "reverse crossing AND the stop read in the three new loops at once, and it is JUDGEMENT.")
        return None
    fn, why = TRANSPORT_CREATORS.get(TRANSPORT, (None, "unknown mechanism - not one of "
                                                       f"{sorted(TRANSPORT_CREATORS)}"))
    if not gate(f"S0d the chosen TRANSPORT {TRANSPORT!r} has a creator BUILT in the fleet today",
                bool(fn) and hasattr(g, fn), why):
        return None
    fact(f"TRANSPORT = {TRANSPORT!r} via gscript.{fn} - {why}")
    return h0


# ============================================================================== S1
def s1():
    print("\n=== S1: the D1 target", flush=True)
    if os.path.exists(TARGET):
        os.remove(TARGET)
    shutil.copy2(ORIGINAL, TARGET)
    # S1z - the peer's discriminating test for run 3's failure, in one line
    # (`archive/peer/2026-09-17-d1-s1-stale-in-memory-copy.md`): hash the DESTINATION after the copy and BEFORE
    # any LabVIEW open. If this passes and the census still reads an edited VI, the disk file is innocent and
    # LabVIEW served a resident VI from memory; if it fails, the copy/save path is the culprit. Without it the
    # two explanations are indistinguishable from the log, which is what run 3 actually cost.
    mt = md5(TARGET)
    if not gate("S1z the working copy on DISK is byte-identical to the original, before LabVIEW sees it",
                mt == ORIG_MD5, f"{mt} (want {ORIG_MD5}) at {TARGET}"):
        return False, {}
    g.open_panel(TARGET)
    got = {cls: g.count(TARGET, cls) for cls in BEFORE}
    fact(f"BEFORE census: {got}")
    ok = all(got[c] == BEFORE[c] for c in BEFORE)
    gate("S1 the copy matches the BEFORE census", ok,
         f"{ {c: (BEFORE[c], got[c]) for c in BEFORE if got[c] != BEFORE[c]} } (empty = all match)")
    # "headlessly" WITHDRAWN 2026-09-17 (plan s11g.4 / s2b): this line HAD THE PANEL OPEN four lines above, so
    # headlessness was never what distinguished 0 from 1. The record splits 3-3 on PRELOAD - 1 whenever the
    # ORIGINAL hierarchy is GetVIReference'd before the copy is opened, 0 whenever it is not - and the
    # controlled pair has not been run. Not gated either way.
    fact(f"ExecState of the fresh copy: {g.exec_state(TARGET)} (0 or 1; the discriminator is PRELOAD, not "
         f"headlessness - plan s2b; NOT gated)")
    return ok, got


# ============================================================================== S1t  (plan §11h)
# THE PER-FRAME TIFF WRITER IS NOT ORIGINAL BEHAVIOUR, and this runs BEFORE the moves.
# `docs/fixture-recording.md:8-20` records FOUR nodes INSERTED into the working copy on 2026-09-01 for fixture
# recording; `tools/bench/diag_true_original_tiff.log` (6/0, read-only, both md5s unchanged) then measured the
# TRUE original `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` at SubVI 97 / Function 179 / Node 622
# against the working copy's 98 / 181 / 626 - i.e. those four nodes are the WHOLE difference, and none of their
# uids exists in the original. So plan §5a's "#22700 stays 1.1 - unconditional, exactly as the original has it"
# is WITHDRAWN (§11h) and D1 deletes the writer instead of relocating it.
TIFF_DELETE = [(22700, "SubVI", "IMAQ Write TIFF File 2"), (23020, "Function", "Build Path")]
# Inserted in the same pass but NOT deleted here, deliberately (§11h): #23175 `Strip Path` is a measured
# collateral SINK of #376's w5090 net (plan §7.2b) and #22703 `Format Into String` branches the frame-index
# subtract #5119 - both are sinks on nets whose other ends stay, so removing them is a separate change. After
# #23020 goes they are dead-but-legal (a source with no sink cannot break a VI). Reported, left standing.
TIFF_LEFT_STANDING = [(23175, "Strip Path"), (22703, "Format Into String")]


def bare_named_sinks(target, diagram_index, fresh=False):
    """{(node uid, terminal index): name} for every NAMED input terminal on the diagram that carries NO wire.
    This is the census phase P run 2 did not have: a delete bares a SINK silently - no broken wire, nothing for
    Remove Bad Wires - and pins ExecState at 0 (plan §2a)."""
    out = {}
    for uid, rec in wmap(target, diagram_index, fresh).items():
        for r in rec[2]:
            if not r["is_source"] and r["wire"] == 0 and r["name"]:
                out[(uid, r["i"])] = r["name"]
    return out


def s1t():
    print("\n=== S1t: delete the FIXTURE TIFF writer before any move (plan §11h)", flush=True)
    d43 = diag_index(TARGET, FRAME_BODY_UID)
    es0 = g.exec_state(TARGET)
    bare0 = bare_named_sinks(TARGET, d43)
    counts0 = {c: g.count(TARGET, c) for c in ("SubVI", "Function", "Node", "Wire")}
    fact(f"S1t BEFORE: diagram 43 is Traverse index {d43}; counts {counts0}; "
         f"{len(bare0)} bare named sinks; ExecState {es0}")
    for uid, cls, label in TIFF_DELETE:
        order = [o["uid"] for o in g.report_all(TARGET, cls)]
        if uid not in order:
            gate(f"S1t #{uid} ({label}) present before deletion", False, f"not found among {cls}")
            continue
        g.delete_object(TARGET, cls, order.index(uid), verify=False)
        if cls in EXPECT:
            EXPECT[cls] -= 1
    g.remove_bad_wires_scripted(TARGET)
    gone = []
    for uid, cls, label in TIFF_DELETE:
        present = uid in {o["uid"] for o in g.report_all(TARGET, "Node")}
        gate(f"S1t #{uid} ({label}) is GONE", not present, "still present" if present else "")
        gone.append(not present)
    counts1 = {c: g.count(TARGET, c) for c in ("SubVI", "Function", "Node", "Wire")}
    bare1 = bare_named_sinks(TARGET, d43, fresh=True)
    new_bare = {k: v for k, v in bare1.items() if k not in bare0}
    gate("S1t no STAYING node was left with a bare named input", not new_bare,
         f"newly bare {sorted((u, i, n) for (u, i), n in new_bare.items())[:8]}")
    es1 = g.exec_state(TARGET)
    gate("S1t ExecState unchanged across the deletion", es1 == es0, f"{es0} -> {es1}")
    fact(f"S1t AFTER: counts {counts1}; delta {dict((k, counts1[k] - counts0[k]) for k in counts0)}; "
         f"{len(bare1)} bare named sinks (was {len(bare0)})")
    for uid, label in TIFF_LEFT_STANDING:
        still = uid in {o["uid"] for o in g.report_all(TARGET, "Node")}
        fact(f"S1t LEFT STANDING (§11h, deliberate): #{uid} {label} present={still} - dead-but-legal once "
             f"#23020 is gone; a source with no sink cannot break a VI")
    return all(gone)


# ============================================================================== S2
def s2():
    print("\n=== S2: three new While loops on Diagram #686", flush=True)
    sib_i = diag_index(TARGET, SIBLING_DIAG_UID)
    fact(f"Diagram#{SIBLING_DIAG_UID} (holder of WhileLoop#{FRAME_LOOP_UID}) is Traverse index {sib_i}")
    loops = {}
    for row, loc in (("1.2", (2600, 2600)), ("1.5", (2600, 3400)), ("1.7", (2600, 4200))):
        dg0, wl0 = g.uids(TARGET, "Diagram"), g.uids(TARGET, "WhileLoop")
        g.loop_in("while", TARGET, sib_i, loc)
        new_dg, new_wl = g.new_since(TARGET, "Diagram", dg0), g.new_since(TARGET, "WhileLoop", wl0)
        if len(new_dg) != 1 or len(new_wl) != 1:
            gate(f"S2 loop {row} created", False, f"+{len(new_dg)} diagrams, +{len(new_wl)} while loops")
            return None
        # the destination index comes from new_since's OWN `i` (docs/NAMES.md:511-534 - three runs were burned
        # deriving it from a whole-VI report_all listing), and is re-verified by listing the diagram's contents.
        loops[row] = dict(loop=new_wl[0]["uid"], body=new_dg[0]["uid"],
                          body_i=new_dg[0].get("i", diag_index(TARGET, new_dg[0]["uid"])))
        fact(f"{row}: WhileLoop #{loops[row]['loop']}, body Diagram #{loops[row]['body']} "
             f"at Traverse index {loops[row]['body_i']}")
    ok = gate("S2 three loops where there was one",
              g.count(TARGET, "WhileLoop") == BEFORE["WhileLoop"] + 3
              and g.count(TARGET, "Diagram") == BEFORE["Diagram"] + 3,
              f"WhileLoop {g.count(TARGET, 'WhileLoop')} (want {BEFORE['WhileLoop'] + 3}), "
              f"Diagram {g.count(TARGET, 'Diagram')} (want {BEFORE['Diagram'] + 3})")
    still = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")]
    gate("S2b #637 still exists", FRAME_LOOP_UID in still, f"WhileLoops {still}")
    for uid in STAY_ON_11 + [CTLTERM_STOP_UID]:
        try:
            _c, ou = owner_of(TARGET, uid)
            gate(f"S2c #{uid} still owned by the frame loop body", ou == FRAME_BODY_UID,
                 f"owner {ou} (want Diagram#{FRAME_BODY_UID})")
        except Exception as e:
            gate(f"S2c #{uid} still owned by the frame loop body", False, f"UNRESOLVED READ: {str(e)[:150]}")
    return loops if ok else None


# ============================================================================== S3 / S3b
def s3(loops):
    print("\n=== S3: move 23 objects (s11c: #12589 stays on 1.1; s11e.3 adds the 3 control refs), "
          "delete #5058, drop GPU_kernel_v1", flush=True)
    frame_i = diag_index(TARGET, FRAME_BODY_UID)

    # --- S3b part 1: the BEFORE terminal census (s11a.2). This, not s8's static table, is the authoritative
    #     re-wire list: whatever went wired->bare is what the move cut.
    #
    #     REV 4b, after `archive/peer/2026-09-17-priorart-priorart-d1-build-rev4.md` B3 (`already-measured`):
    #     censusing ONLY the moving nodes cannot see the failure that stopped phase P's run 2. A LabVIEW wire is a
    #     NET, and a net's other sinks can be nodes that DO NOT MOVE - measured for `#376`:
    #       w3268 (frame-loop-wire-graph.md:151) t7 `x`            -> also #2136 #3191 #10068 #1114 #29240, ALL stay
    #       w5090 (:167)                          t11 `selected path` -> also #23175 Strip Path,            stays
    #     Moving #376 bares six terminals on nodes outside a moving-nodes-only census, on BOTH passes, and the
    #     signature is a SILENT bare terminal - no broken wire, nothing for Remove Bad Wires, ExecState pinned at 0
    #     (d1-build-plan.md s2a; tools/bench/diag_movein_p1_break.log 5/5). ExecState is not read until S5, so
    #     nothing else would catch it either. So the census covers the moving nodes PLUS every node on this diagram
    #     that shares a wire with one of them.
    #     WIDENED AGAIN 2026-09-17 for prior-art finding A1 (rev4b review): the census walked DIAGRAM 43 only,
    #     so two classes of collateral were invisible - nodes on DIAGRAM 19 (where `#7202 Global motor pos.vi`
    #     consumes `#4256`'s final value, `frame-loop-wire-graph.md:410`) and the SHIFT REGISTERS themselves,
    #     which are not nodes on any diagram and therefore cannot appear in a walk. Both are censused now.
    outer_i = diag_index(TARGET, SIBLING_DIAG_UID)          # "diagram 19" - the frame loop's own holder
    frame_by = wmap(TARGET, frame_i)
    outer_by = wmap(TARGET, outer_i)
    moving = [u for uids in MOVE_TABLE.values() for u in uids]
    moving_wires = {r["wire"] for u in moving if u in frame_by for r in frame_by[u][2] if r["wire"]}
    neighbours = sorted({u for u, (_n, _l, rows) in frame_by.items()
                         if u not in moving and any(r["wire"] in moving_wires for r in rows)})
    outer_nodes = sorted(outer_by)
    fact(f"S3b net neighbours on diagram 43 (stay put, share a net with a mover): {neighbours}")
    fact(f"S3b diagram 19 (A1) censused whole: {outer_nodes} "
         f"- plan s5b lists only [637, 6384, 2048, 781, 27605]")
    before_terms = {uid: terms_of(TARGET, frame_i, uid) for uid in list(moving) + neighbours}
    before_outer = {uid: terms_of(TARGET, outer_i, uid) for uid in outer_nodes}
    loop_i_637 = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(FRAME_LOOP_UID)
    before_sr = sr_census(TARGET, loop_i_637)
    n_wired_before = sum(1 for t in before_terms.values() for (_n, _s, w) in t.values() if w)
    fact(f"BEFORE terminal census: {len(before_terms)} nodes on d43 ({len(moving)} moving + {len(neighbours)} "
         f"net-neighbours), {n_wired_before} wired terminals; {len(before_outer)} nodes on d19; "
         f"{len(before_sr)} shift registers of #637")

    moved, y = [], 60
    for row, uids in MOVE_TABLE.items():
        body_uid, loop_uid = loops[row]["body"], loops[row]["loop"]
        for uid in uids:
            # A TRAVERSE INDEX IS NOT A HANDLE - measured, run 2 (build_d1_v0_run2.log:19-21): all THREE new body
            # diagrams reported Traverse index **20** at creation, because each new one is inserted at the same
            # position and pushes the previous one down (the WhileLoop list afterwards reads
            # [1135, 1134, 1133, 25380, 637, 15173] - the new ones in REVERSE creation order). The index cached
            # for 1.2 therefore addressed 1.7's body, and `#5540` landed in Diagram#1215/WhileLoop#1135.
            # `tools/gscript.py:833-836` already says it: identify by uid, never by a cached Traverse index.
            # So the destination is re-resolved FROM ITS UID immediately before every single move.
            body_i = diag_index(TARGET, body_uid)
            move_in(TARGET, uid, body_i, (60, y))
            y += 120
            try:
                oc, ou = owner_of(TARGET, uid)
                oc2, ou2 = owner_of(TARGET, ou) if ou else (None, None)
                ok = (ou == body_uid and ou2 == loop_uid)
            except Exception as e:
                oc = ou = oc2 = ou2 = f"<{str(e)[:60]}>"
                ok = False
            moved.append((row, uid, ok))
            if not gate(f"S3 #{uid} -> {row}", ok,
                        f"owner {oc}#{ou} (want Diagram#{body_uid}); owner(owner) {oc2}#{ou2} "
                        f"(want WhileLoop#{loop_uid})"):
                return None
        # identity gate on the destination BEFORE the next row's mutations (docs/NAMES.md:511-534)
        try:
            on_body = [r["uid"] for r in g.node_labels(TARGET, diag_index(TARGET, body_uid))]
        except Exception as e:
            on_body = f"<node_labels: {str(e)[:60]}>"
        fact(f"{row} body Diagram#{body_uid} now holds {on_body}")

    d_after_moves = g.count(TARGET, "Diagram")
    gate("S3a the moves destroyed no frame diagram", d_after_moves == BEFORE["Diagram"] + 3,
         f"Diagram {d_after_moves} (want {BEFORE['Diagram'] + 3}) - structures keep their frames (plan s2b P3)")

    # --- the seam: delete #5058, drop GPU_kernel_v1.vi into 1.2
    ids = [o["uid"] for o in g.report(TARGET, "SubVI")]
    if KERNEL_UID not in ids:
        gate("S3e #5058 found for deletion", False, "not in report('SubVI')")
        return None
    g.delete_object(TARGET, "SubVI", ids.index(KERNEL_UID), verify=False)
    sv0 = g.uids(TARGET, "SubVI")
    g.drop_subvi(TARGET, GPU_KERNEL, diag_index(TARGET, loops["1.2"]["body"]), (900, 400))
    new_k = g.new_since(TARGET, "SubVI", sv0)
    if not gate("S3e #5058 deleted and GPU_kernel_v1 dropped into 1.2", len(new_k) == 1
                and g.count(TARGET, "SubVI") == EXPECT["SubVI"],
                f"new subVI {new_k}, SubVI count {g.count(TARGET, 'SubVI')} (want {EXPECT['SubVI']} = the BEFORE "
                f"census {BEFORE['SubVI']} minus what S1t deleted)"):
        return None
    kernel_new = new_k[0]["uid"]
    fact(f"GPU_kernel_v1.vi is uid {kernel_new} on 1.2")

    # --- S3b part 2: the AFTER census, and the diff. The net-neighbours are re-read on the diagram they never
    #     left (frame_i); the moving nodes on the diagram they landed on.
    after_terms = {}
    for row, uids in MOVE_TABLE.items():
        bi = diag_index(TARGET, loops[row]["body"])     # never the cached index - run 2's S3 failure
        wmap(TARGET, bi, fresh=True)
        for uid in uids:
            after_terms[uid] = terms_of(TARGET, bi, uid)
    frame_i = diag_index(TARGET, FRAME_BODY_UID)        # re-resolved, never cached (run 2's S3 failure)
    wmap(TARGET, frame_i, fresh=True)
    for uid in neighbours:
        after_terms[uid] = terms_of(TARGET, frame_i, uid)

    # --- A1: diagram 19 and the shift registers, re-read after the moves
    outer_i = diag_index(TARGET, SIBLING_DIAG_UID)
    wmap(TARGET, outer_i, fresh=True)
    outer_cut = []
    for uid, before in before_outer.items():
        after = terms_of(TARGET, outer_i, uid)
        for i, (nm, src, w) in before.items():
            if w and (i not in after or not after[i][2]):
                outer_cut.append((uid, i, nm, src, w))
    gate("S3b-d19 no node on diagram 19 lost a wire (A1: #7202 Global motor pos.vi lives here)",
         not outer_cut, f"{outer_cut}")
    after_sr = sr_census(TARGET, [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(FRAME_LOOP_UID))
    sr_changed = [(k, before_sr[k], after_sr.get(k)) for k in before_sr if after_sr.get(k) != before_sr[k]]
    for k, b, a in sr_changed:
        print(f"      SR   #{k} changed: before {b} -> after {a}", flush=True)
    fact(f"S3b-sr shift registers of #637 whose wiring changed: {[k for k, _b, _a in sr_changed]} "
         f"(A1 predicts #4256 `position [internal units]`, whose body source #10407 moved to 1.5, and whose "
         f"FINAL value is the sole feed of `Focus position` on #7202 - it must be re-created on 1.5 AND its "
         f"outside consumer re-routed, `restructure-plan-4.6.md:348,:354`)")
    cut = []
    for uid, before in before_terms.items():
        after = after_terms.get(uid, {})
        for i, (nm, src, w) in before.items():
            if w and (i not in after or not after[i][2]):
                cut.append((uid, i, nm, src, w))
    fact(f"S3b census diff: {len(cut)} terminals went wired->bare = the authoritative re-wire list")
    for row in cut:
        tag = "STAYED-BUT-BARED" if row[0] in neighbours else "moved"
        print(f"      cut  #{row[0]} t{row[1]} {row[2]!r} {'OUT' if row[3] else 'IN'} was w{row[4]}  [{tag}]",
              flush=True)
    cut_wires = {r[4] for r in cut}
    missing = [w for w in EXPECTED_CROSSINGS if w not in cut_wires]
    gate("S3b the cut set covers plan s8's 13 wired crossings", not missing,
         f"not cut: {missing} (a crossing that survived the move is a crossing the move did not have to cut)")
    # The B3 gate proper: a node that did NOT move must not lose a wire. If it did, a shared net was bared and
    # the VI is silently unfixable by Remove Bad Wires - the phase-P run-2 signature.
    # GATE SPEC FIXED 2026-09-17 (run 4's first fail; STATUS OPEN 27b). `neighbours` is "shares a net with a
    # mover AND is not itself in MOVE_TABLE" - and #5058 satisfies both, because it is DELETED rather than moved.
    # Its 13 terminals therefore showed up as "collateral" in run 4, which is a gate-spec defect, not a build
    # defect: those 13 wires ARE plan s8's 13 crossings and the S3b gate two lines up REQUIRES them in the cut
    # set. A deleted node is not a "staying node". It is excluded here by uid and kept in `cut`.
    # ⚠️ uid REUSE: after the delete, `drop_subvi(GPU_kernel_v1.vi)` came back with uid 5058 again (run 4,
    # `S3e` FACT). That is why the after-pass must never be allowed to resolve 5058 "through" the new kernel -
    # it is read on the FRAME diagram, where the new kernel does not live, so it correctly reads {}.
    staying = [u for u in neighbours if u != KERNEL_UID]
    collateral = [r for r in cut if r[0] in staying]
    fact(f"S3b-collateral: #{KERNEL_UID} excluded from 'staying nodes' - it is DELETED, and the GPU kernel "
         f"was re-issued the same uid (uid reuse); its {sum(1 for r in cut if r[0] == KERNEL_UID)} cut "
         f"terminals are plan s8's crossings and stay in the re-wire list")
    gate("S3b-collateral no STAYING node was bared by a move (rev-4 review B3)", not collateral,
         f"{collateral} - these must be re-wired from their original source before ExecState is read")
    return dict(moved=moved, cut=cut, kernel=kernel_new, frame_i=frame_i,
                outer_cut=outer_cut, sr_changed=[(k, b, a) for k, b, a in sr_changed])


# ============================================================================== S3c / S3d
def s3c(loops):
    print("\n=== S3c: 8 shift registers, 6 control terminals (plan s5d count corrected)", flush=True)
    panel_before = g.panel_wiring(TARGET)
    made = []
    for row, regs in SHIFT_REGS.items():
        loop_uids = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")]
        li = loop_uids.index(loops[row]["loop"])
        # The op takes a TRAVERSE index, and `report_all`'s order is assumed to be that order. Assumed indices are
        # this project's recorded way to edit the wrong object (docs/NAMES.md:511-534;
        # archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md), so it is CHECKED, by a
        # typed read that returns the loop's own uid.
        seen = g.loop_cast(TARGET, li, class_name="WhileLoop")   # -> {loop_uid, n_wire_uid, shift_reg_uids, errors}
        if not gate(f"S3c index {li} really is {row}'s WhileLoop #{loops[row]['loop']}",
                    seen["loop_uid"] == loops[row]["loop"] and not seen["errors"],
                    f"loop_cast({li}) -> loop_uid {seen['loop_uid']}, errors {seen['errors']}"):
            return panel_before, made
        for (right, left, name) in regs:
            uid = g.add_shift_reg(TARGET, li, y_position=120 + 60 * len(made), class_name="WhileLoop")
            made.append((row, uid, name, right, left))
            fact(f"{row}: shift register created uid {uid} for {name!r} (was #{right}/#{left})")
    gate("S3c 8 shift registers created", len(made) == 8, f"{len(made)} created")
    # wiring each side is a per-register step that needs the body node index AT THAT MOMENT (wire_sr's contract:
    # indices are creation-order, read with node_terms_uid just before the call) - done in wire_registers().

    moved_ct = []
    for label in CTLTERM_CONTROLS_12:
        row = next((r for r in panel_before if r["label"] == label), None)
        if row is None:
            fact(f"control {label!r} has no panel_wiring row - tab/cluster nested (gscript.py:640); skipped")
            continue
        moved_ct.append(label)
    fact(f"ControlTerminals to move into 1.2, by control label: {moved_ct}")
    return panel_before, made


def s3d(loops, kernel_uid):
    """The 6 loop-invariant seam inputs must reach the kernel through NON-INDEXED tunnels (plan s8; rule 1a -
    "whole-array parameters must cross loop borders non-indexed"). They are identified by the WIRE on the kernel's
    own named terminal, never by the tunnel's `out_name`: a LoopTunnel's outer terminal is frequently unnamed
    (`d1_step0_census.json` carries `"out_name": ""` for #5569 and #5752), so name-matching a tunnel would gate on
    nothing and PASS silently."""
    print("\n=== S3d: whole arrays cross NON-INDEXED", flush=True)
    # GATE SPEC FIXED 2026-09-17 (run 4's second fail). This gate asks whether the SIX loop-invariant seam
    # inputs reach the kernel through NON-INDEXED LoopTunnels. Those tunnels are created by PHASE "full"'s
    # re-wiring; in PHASE "relocate" nothing is re-wired at all (the moves only CUT), so all six resolve as
    # `unresolved` by construction. Asserting it in the relocate phase gates on the phase boundary, not on the
    # build. It is ARMED ONLY IN PHASE "full".
    if PHASE != "full":
        print("  SKIPPED-PHASE  S3d: the 6 seam tunnels do not exist until PHASE 'full' re-wires the seam",
              flush=True)
        return None
    kt = terms_of(TARGET, diag_index(TARGET, loops["1.2"]["body"]), kernel_uid, fresh=True)
    want = {nm: w for (nm, src, w) in kt.values() if nm in NON_INDEXED and not src}
    by_inner = {}
    for i in range(g.count(TARGET, "LoopTunnel")):
        try:
            t = g.tunnels(TARGET, i)
        except Exception:
            continue
        if not t["uid"]:
            continue
        for w in t["in_wires"]:
            if w:
                by_inner[w] = t
    bad, missing = [], []
    for nm in NON_INDEXED:
        w = want.get(nm)
        if not w:
            missing.append(nm)
            continue
        t = by_inner.get(w)
        if t is None:
            missing.append(f"{nm} (w{w}: no tunnel carries it)")
        elif t["index_mode"] != 0:
            bad.append((nm, t["uid"], t["index_mode"]))
    fact(f"seam tunnels: {[(nm, want.get(nm), (by_inner.get(want.get(nm)) or {}).get('uid')) for nm in NON_INDEXED]}")
    return gate("S3d the 6 whole-array seam inputs cross non-indexed (IndexMode 0)",
                not bad and not missing, f"auto-indexed {bad}; unresolved {missing}")


# ============================================================================== S4
OP_LOOPENDREF = os.path.join(CLAUDEDEV, "OpLoopEndRef_v0.vi")
LOOPENDREF_LABELS = os.path.join(ROOT, "tools", "bench", "oploopendref_labels.json")
_LER = None


def loop_end_ref(target, loop_index):
    """A While loop's CONDITIONAL TERMINAL, through OpLoopEndRef_v0 (16/0). Driven exactly as
    `tools/recipes/build_oploopendref_v0.py:340-370` drives it - the labels file maps FP LABEL -> meaning, so it
    is inverted here, every output is POISONED before the run, and the four per-property error columns are read,
    because "no error out" is not a verdict that a property resolved (toolkit-capabilities.md:234-238)."""
    global _LER
    if _LER is None:
        with open(LOOPENDREF_LABELS, encoding="utf-8") as f:
            _LER = {v: k for k, v in json.load(f).items()}
    lab = _LER
    vi = g.op(OP_LOOPENDREF)
    for k in ("CondTermUID", "CondWireUID", "LoopUID"):
        vi.SetControlValue(lab[k], 0)
    vi.SetControlValue(lab["IsSource"], False)
    for k in ("LoopEndRefErr", "IsSourceErr", "ConnWireErr", "WireUIDErr"):
        try:
            vi.SetControlValue(lab[k], (False, 0, ""))
        except Exception:
            pass
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "WhileLoop")
    vi.SetControlValue("index", int(loop_index))
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:100]}"
    errs = " ".join(x for x in (g._err(vi, lab[k]) or ""
                                for k in ("LoopEndRefErr", "IsSourceErr", "ConnWireErr", "WireUIDErr")) if x)
    return dict(loop_uid=int(vi.GetControlValue(lab["LoopUID"])),
                cond_term_uid=int(vi.GetControlValue(lab["CondTermUID"])),
                is_source=bool(vi.GetControlValue(lab["IsSource"])),
                cond_wire_uid=int(vi.GetControlValue(lab["CondWireUID"])), err=err, errs=errs)


def s4(loops):
    print("\n=== S4: conditional terminals", flush=True)
    loop_uids = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")]
    r = loop_end_ref(TARGET, loop_uids.index(FRAME_LOOP_UID))
    ok = (r["loop_uid"] == FRAME_LOOP_UID and r["cond_term_uid"] == COND_TERM_UID
          and r["cond_wire_uid"] == COND_WIRE_UID and not r["errs"])
    gate("S4a #637's conditional terminal is untouched", ok,
         f"loop {r['loop_uid']}, term {r['cond_term_uid']} (want {COND_TERM_UID}), wire {r['cond_wire_uid']} "
         f"(want {COND_WIRE_UID}, source #{COND_SRC_UID}); errs {r['errs'][:80]!r}")
    for row in ("1.2", "1.5", "1.7"):
        rr = loop_end_ref(TARGET, loop_uids.index(loops[row]["loop"]))
        # GATE SPEC FIXED 2026-09-17 per plan s11e.4 (run 4's third/fourth/fifth fails). An UNWIRED conditional
        # terminal legitimately reports **error 1055 on the `Connected Wire` read** - there is no wire to return
        # a reference for. Run 4 read terms 1183 / 1204 / 1225 with wire 0 on all three, which IS the correct
        # relocate-phase answer, and failed only because the gate also demanded an empty error column. So the
        # gate compares the TERMINAL UID and `wire == 0`; the error text is reported, never gated.
        if PHASE == "full":
            gate(f"S4b {row}'s conditional terminal is WRITTEN", bool(rr["cond_wire_uid"]),
                 f"term {rr['cond_term_uid']}, wire {rr['cond_wire_uid']} (0 = the loop never stops - plan s4); "
                 f"errs {rr['errs'][:80]!r}")
        else:
            # relocate phase: the sentinel test that will drive it is PHASE "full" work, so the honest
            # prediction is UNWRITTEN. Asserting it, rather than skipping it, is what makes the phase boundary
            # machine-checkable instead of a sentence in a docstring.
            gate(f"S4b {row}'s conditional terminal is reachable and UNWRITTEN (relocate phase)",
                 rr["cond_term_uid"] != 0 and rr["cond_wire_uid"] == 0,
                 f"term {rr['cond_term_uid']} (want != 0), wire {rr['cond_wire_uid']} (want 0); "
                 f"errs {rr['errs'][:80]!r} (1055 on an unwired terminal is EXPECTED - s11e.4, not gated)")
    return ok


# ============================================================================== S5 / S6
def s5(inv0):
    print("\n=== S5: purge, remove bad wires, ExecState, save", flush=True)
    junk = g.new_since(TARGET, "Invoke", inv0)
    for o in junk:
        ids = [x["uid"] for x in g.report(TARGET, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(TARGET, "Invoke", ids.index(o["uid"]), verify=False)
    fact(f"purged {len(junk)} junk Invoke(s) left by the move_in runs: {[o['uid'] for o in junk]}")
    left = g.new_since(TARGET, "Invoke", inv0)
    gate("S5a every junk Invoke is gone", not left, f"still present {left}")
    g.remove_bad_wires_scripted(TARGET)
    es = g.exec_state(TARGET)
    ok = gate("S5 ExecState 1 WARM", es == 1, f"ExecState {es}")
    if ok:
        g.save(TARGET)
        fact(f"saved; file size {os.path.getsize(TARGET)} bytes")
    return ok


def s6():
    print("\n=== S6: cold re-open in a restarted LabVIEW", flush=True)
    g._lv = None
    # `tools/lv_restart.py` does its work at MODULE level (kill -> start -> poll -> 45 s settle), so it is run as
    # a SUBPROCESS, never imported. Standing restart permission, CLAUDE.md s3.
    import subprocess
    try:
        rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                            capture_output=True, text=True, timeout=600)
        fact(f"lv_restart rc={rc.returncode}: {(rc.stdout or '').strip().splitlines()[-1:]}")
    except Exception as e:
        fact(f"lv_restart failed ({str(e)[:80]}) - S6 then measures only a fresh COM session, not a cold LabVIEW")
    g._lv = None
    es = g.exec_state(TARGET)
    got = {c: g.count(TARGET, c) for c in ("Diagram", "WhileLoop", "ControlTerminal")}
    fact(f"cold: ExecState {es}, {got}, size {os.path.getsize(TARGET)} bytes")
    return gate("S6 cold re-open is runnable and the census holds",
                es == 1 and got["Diagram"] == BEFORE["Diagram"] + 3
                and got["WhileLoop"] == BEFORE["WhileLoop"] + 3
                and got["ControlTerminal"] == BEFORE["ControlTerminal"],
                f"ExecState {es}, {got}")


# ============================================================================== PHASE "full" - the RE-WIRE stage
# §11j.2 (judgement, 2026-09-17): "the re-wire source map is completed inside the build from `d1_step0_census.json`
# + `main_vi_nodeterms.json` … and written to `tools/bench/d1_rewire_sources.json` as a by-product". Done by
# `tools/bench/d1_rewire_map.py`, imported here - **109 of 109 cut terminals resolved** (STATUS OPEN 28b's "45 of
# 82" was a poorer join that omitted constants, control terminals, loop tunnels and the eight moving shift
# registers; a shift register is neither a node on a diagram nor a LoopTunnel, so no earlier census could hold it).
#
# EVERY row is ATTEMPTED and SCORED, including the ones whose end has NO NAME. That is deliberate:
# `gscript.wire` is name-addressed ("a MISSING destination name raises 5001 inside the Op") and the only
# index-addressed wire creators reach a TOP-LEVEL source (`connect_terminals` :2202, `connect2` :2428), so a
# structure's SELECTOR or an unnamed tunnel on a nested diagram has no documented route. CLAUDE.md's rule is that
# the second time a failure class is explained by inference it gets MEASURED instead - so the build tries them and
# the log says what LabVIEW did, per row, rather than a docstring saying what it would have done.
REWIRE_ACTIONS = ("same-loop", "from-kernel", "from-const", "from-sr", "to-sr", "from-ctl", "from-tunnel")


def class_index(target, classes=("SubVI", "Function", "CaseStructure", "ForLoop", "WhileLoop", "Comparison",
                                 "IndexArray", "BuildArray", "Property", "Invoke", "Constant",
                                 "ControlReferenceConstant", "DigitalNumericConstant")):
    """uid -> (Traverse class, index in that class's Traverse listing). `gscript.wire` addresses a node as
    Traverse(Class Name)[index], so the index must come from THAT class's own ordered listing (report_all), never
    from a whole-VI listing - `docs/NAMES.md:511-534` is three runs' worth of that lesson."""
    out = {}
    for cls in classes:
        try:
            for i, o in enumerate(g.report_all(target, cls)):
                out.setdefault(o["uid"], (cls, i))
        except Exception:
            continue
    return out


def phase_full_rewire(loops, regs, r3):
    print("\n=== F0: the re-wire SOURCE MAP, completed inside the build (§11j.2)", flush=True)
    sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
    import d1_rewire_map as M
    payload = M.build_map(r3["cut"])
    out_map = os.path.join(ROOT, "tools", "bench", "d1_rewire_sources.json")
    with open(out_map, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
    fact(f"F0 source map: {payload['resolved']}/{payload['cut_terminals']} resolved, "
         f"by action {payload['by_action']} -> {out_map}")
    gate("F0 every cut terminal has a resolved source (STATUS OPEN 28b's 45/82 closed)",
         payload["unresolved"] == 0, f"unresolved {payload['unresolved']}")

    rows = [r for r in payload["rows"] if r["action"].split(":")[0] in REWIRE_ACTIONS]
    fact(f"F1 rows to re-wire: {len(rows)} (the other {payload['cut_terminals'] - len(rows)} are source-side, "
         f"from-stay or cross-loop - queue endpoints, the stage after this one)")

    ci = class_index(TARGET)
    done, failed, noroute = [], [], []
    v1_rows = []            # (tag, sink diagram index, sink node index, sink term, wire uid right after the call)
    reg_by_row = {}
    for row, uid, name, right, left in regs:
        reg_by_row.setdefault(row, []).append((uid, name, right, left))

    def node_index_on(diagram_index, uid):
        w = wmap(TARGET, diagram_index)
        return w[uid][0] if uid in w else None

    def v1_connect(tag, dest, sink_uid, sink_t, src_uid, src_t, src_where, why):
        """OpConnectNested_v1: both ends by INDEX. `src_where` is a loop row ('1.2'/'1.5'/'1.7') or 'outer' for
        the diagram that HOLDS the loops (#686). Returns True when the sink's wire went 0 -> non-zero; the
        DECISIVE gate (the wire survives Remove Bad Wires, §11q.1's T2c) is applied once, after every row."""
        sink_d = diag_index(TARGET, loops[dest]["body"])
        sink_n = node_index_on(sink_d, sink_uid)
        src_d = (diag_index(TARGET, SIBLING_DIAG_UID) if src_where == "outer"
                 else diag_index(TARGET, loops[src_where]["body"]))
        src_n = node_index_on(src_d, src_uid)
        if sink_n is None or src_n is None:
            noroute.append((tag, f"{why}: sink node {sink_uid} index {sink_n} / source node {src_uid} index "
                                 f"{src_n} on diagrams {sink_d}/{src_d}"))
            return False
        dw, es, err = CONNECT_V1(TARGET, sink_d, sink_n, sink_t, src_d, src_n, src_t, V1_LABELS)
        rows_after = g.node_terms(TARGET, sink_d, sink_n)
        wire = next((r["wire"] for r in rows_after if r["i"] == sink_t), 0)
        if wire:
            v1_rows.append((tag, sink_d, sink_n, sink_t, wire))
            done.append((tag, f"OpConnectNested_v1 D[{src_d}].N[{src_n}].T[{src_t}] -> D[{sink_d}].N[{sink_n}]."
                              f"T[{sink_t}] wire {wire} (delta {dw}, ExecState {es}) [{why}]"))
            return True
        failed.append((tag, f"OpConnectNested_v1 left the sink BARE (delta {dw}, ExecState {es}, "
                            f"err {err[:70]!r}) [{why}]"))
        return False

    for r in rows:
        act = r["action"].split(":")[0]
        src = r.get("source") or {}
        dest = r.get("dest")
        sink_uid, sink_t, sink_name = r["uid"], r["i"], r["name"]
        tag = f"#{sink_uid} t{sink_t} {sink_name!r} <- {act} {src.get('uid')}"
        try:
            if act == "from-const":
                # the ONE thing OpCreateConstOnTerm_v0 exists for: a typed literal ON the bare sink terminal,
                # carrying the SAME value the original constant carried (rule 1a - same value, same route).
                body_i = diag_index(TARGET, loops[dest]["body"])
                w = wmap(TARGET, body_i, fresh=True)
                n_i = w[sink_uid][0] if sink_uid in w else None
                loop_i = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(loops[dest]["loop"])
                if n_i is None:
                    raise RuntimeError("the moved node is not on its destination diagram")
                res = CONST_ON_TERM(TARGET, loop_i, n_i, sink_t, CONST_LABELS, value=src.get("val"))
                ok = bool(res.get("created_uid")) and not res.get("inv_err")
                (done if ok else failed).append((tag, f"value {src.get('val')!r} -> uid {res.get('created_uid')}"
                                                      f" {res.get('inv_err', '')[:60]}"))
                continue
            if act in ("from-sr", "to-sr"):
                regs_here = reg_by_row.get(src.get("row") or dest or "", [])
                ridx = next((i for i, (u, nm, rr, ll) in enumerate(regs_here) if rr == src.get("right")), None)
                body_i = diag_index(TARGET, loops[src.get("row") or dest]["body"])
                w = wmap(TARGET, body_i, fresh=True)
                n_i = w[sink_uid][0] if sink_uid in w else None
                loop_i = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(
                    loops[src.get("row") or dest]["loop"])
                if ridx is None or n_i is None:
                    raise RuntimeError(f"register {src.get('right')} or node {sink_uid} not found")
                g.wire_sr("LeftIn" if act == "from-sr" else "RightIn", TARGET, loop_i, ridx,
                          node_index=n_i, term_index=sink_t)
                done.append((tag, f"wire_sr {'LeftIn' if act == 'from-sr' else 'RightIn'} reg[{ridx}]"))
                continue
            if act == "from-ctl":
                lbl = src.get("label")
                if not lbl or not sink_name:
                    noroute.append((tag, f"control {lbl!r} / sink name {sink_name!r} - wire_control is "
                                         f"name-addressed on BOTH ends"))
                    continue
                s_cls, s_i = ci.get(sink_uid, (None, None))
                g.wire_control(TARGET, [lbl], s_cls, s_i, [sink_name])
                done.append((tag, f"wire_control {lbl!r} -> {sink_name!r}"))
                continue
            # same-loop / from-kernel / from-tunnel: a NODE source, wired by NAME where both ends HAVE names, and
            # by INDEX through OpConnectNested_v1 where either end has none (that is exactly what 5001 means).
            if act == "from-tunnel":
                # §11r, MEASURED (diag_tunnelsource_onehop.log): the OLD tunnel is a CARRIER; the value's real
                # source is the single source terminal on the tunnel's OUTER wire. Its owner class decides.
                ts = TUNNEL_SOURCES.get((sink_uid, sink_t))
                if not ts:
                    noroute.append((tag, f"tunnel #{src.get('uid')} outer wire w{r.get('outer_wire')}: not in "
                                         f"d1_tunnel_sources.json - run tools/bench/diag_tunnelsource_onehop.py"))
                    continue
                if not ts.get("ok"):
                    hop = (ts.get("hops") or [{}])[-1]
                    noroute.append((tag, f"tunnel #{src.get('uid')} outer wire w{r.get('outer_wire')}: its source "
                                         f"terminal is owned by {hop.get('owner_class') or ts.get('why')} "
                                         f"uid {hop.get('owner_uid')} - NOT a node, so no "
                                         f"Diagram[].Nodes[].Terminals[] address exists (MEASURED)"))
                    continue
                if ts.get("diagram") != 19:
                    noroute.append((tag, f"resolved source #{ts['owner_uid']} is on census diagram "
                                         f"{ts.get('diagram')}, not the loops' own diagram 19"))
                    continue
                v1_connect(tag, dest, sink_uid, sink_t, ts["owner_uid"], ts["term"], "outer",
                           f"from-tunnel resolved one hop to {ts['owner_class']} #{ts['owner_uid']} "
                           f"t{ts['term']} {ts.get('term_name')!r}")
                continue
            if not sink_name or not src.get("name"):
                if src.get("kind") == "node" and src.get("i") is not None and dest:
                    v1_connect(tag, dest, sink_uid, sink_t, src["uid"], src["i"], dest,
                               f"unnamed end (sink {sink_name!r}, source {src.get('name')!r})")
                else:
                    noroute.append((tag, f"unnamed end (sink {sink_name!r}, source {src.get('name')!r}) and the "
                                         f"source is not a node on a body diagram ({src.get('kind')})"))
                continue
            s_uid, s_name = src["uid"], src["name"]
            s_cls, s_i = ci.get(s_uid, (None, None))
            d_cls, d_i = ci.get(sink_uid, (None, None))
            if s_cls is None or d_cls is None:
                raise RuntimeError(f"no Traverse class/index for source {s_uid} ({s_cls}) or sink {sink_uid}")
            try:
                g.wire(TARGET, s_cls, s_i, s_name, d_cls, d_i, sink_name, branch=True)
                done.append((tag, f"{s_cls}[{s_i}].{s_name!r} -> {d_cls}[{d_i}].{sink_name!r}"))
            except Exception as e:
                # run 7: `Get Outputs.vi` / `Get Controls.vi` raise 5001 on names LabVIEW itself carries
                # (newlines, duplicates). The index-addressed op does not look a name up at all - so the
                # name-addressed failure is RETRIED by index before it is scored as a failure.
                if src.get("kind") == "node" and src.get("i") is not None and dest:
                    v1_connect(tag, dest, sink_uid, sink_t, src["uid"], src["i"], dest,
                               f"retry by index after {str(e)[:60]}")
                else:
                    failed.append((tag, str(e)[:160]))
        except Exception as e:
            failed.append((tag, str(e)[:160]))
    # §11q.1's decisive gate, applied to every wire OpConnectNested_v1 made: `remove_bad_wires_scripted` DELETES a
    # broken wire and LEAVES a good one - the discriminator wire-uid equality cannot make (docs/NAMES.md:861-863,
    # test_opconnectnested_v1.log:24-27 where a wire with the same uid on both ends took ExecState 1 -> 0).
    if v1_rows:
        es_before_rbw = g.exec_state(TARGET)
        g.remove_bad_wires_scripted(TARGET)
        survived, died = [], []
        for tg, sd, sn, st, wire in v1_rows:
            after = next((x["wire"] for x in g.node_terms(TARGET, sd, sn) if x["i"] == st), 0)
            (survived if after == wire else died).append((tg, wire, after))
        fact(f"F1v OpConnectNested_v1 wires: {len(v1_rows)} made, {len(survived)} SURVIVED "
             f"remove_bad_wires_scripted, {len(died)} deleted by it; ExecState before RBW {es_before_rbw}, "
             f"after {g.exec_state(TARGET)}")
        for tg, w0, w1 in died:
            print(f"      RBW-DELETED {tg}  wire {w0} -> {w1}", flush=True)
        gate("F1v every index-addressed wire SURVIVES Remove Bad Wires (i.e. none is broken)", not died,
             f"{len(died)} of {len(v1_rows)} deleted")
    for t, d in done:
        print(f"      WIRED    {t}  {d}", flush=True)
    for t, d in failed:
        print(f"      FAILED   {t}  {d}", flush=True)
    for t, d in noroute:
        print(f"      NO-ROUTE {t}  {d}", flush=True)
    fact(f"F1 re-wire attempted {len(rows)}: WIRED {len(done)}, FAILED {len(failed)}, NO-ROUTE {len(noroute)}")
    gate("F1 every routable cut terminal was re-wired", not failed,
         f"{len(failed)} failed: {[t for t, _ in failed][:6]}")
    gate("F1b every cut terminal HAS a route with today's ops", not noroute,
         f"{len(noroute)} have none: {[t for t, _ in noroute][:8]}")
    return dict(wired=done, failed=failed, noroute=noroute, map=payload["by_action"])


# ============================================================================== main
SKIPPED_PHASE = [
    ("S1q", "8 queues obtained (Q_free/Q_work 20, Q_meta/Q_res/Q_good/Q_rmeta unbounded, Q_focus/Q_focusback 1)"),
    ("S3c-wiring", "the 8 created shift registers wired to their body nodes (wire_sr)"),
    ("S3c-ctlterm", "the 6 ControlTerminals reparented into 1.2 (plan s5d)"),
    ("S3b-rewire", "every cut terminal re-wired through a tunnel / queue / SR (wires cut == wires re-wired)"),
    ("S4b-write", "the three sentinel tests driving the new loops' conditional terminals"),
    ("S4s", "the sentinel enqueues (-1 / empty array) and 1.7's do-not-write-the-sentinel gate"),
    ("S5", "junk purge / remove bad wires / ExecState 1 WARM / save / file size"),
    ("S6", "cold re-open in a restarted LabVIEW"),
]


def main():
    global PHASE
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    if "--full" in sys.argv:
        PHASE = "full"
    if "--explain-full" in sys.argv:
        raise NotImplementedError(
            "PHASE 'full' is not written. STATE OF THE THREE BLOCKERS, 2026-09-17 (each corrected against a "
            "measurement, not carried forward):\n"
            "  (a) queues/enqueues/dequeues/tunnels/SR wiring/ControlTerminal moves/exit_while - every op EXISTS "
            "(the queue ops' own evidence is test_opqueue.log 7/7; the ASSEMBLY pattern is "
            "build_track_v6_queue.py, whose 162/162 belongs to Track_v6_CPU_queue_v0.vi). Only UNWRITTEN.\n"
            "  (b) the sentinel COMPARISON and its LITERAL inside a loop body - NO LONGER BLOCKED. "
            "`OpCreateEqual_v0` and `OpCreateConst_v0` were built 2026-09-17 (plan s11g.1, route (c)) and are "
            "FUNCTIONAL 23/0 (tools/bench/build_opsentinel_ops_run3.log): both land on a NAMED subdiagram, and "
            "the Equal?'s Boolean then drives that loop's conditional terminal through OpStopFromNode_v0, "
            "ExecState 1.\n"
            "  (c) THE ONE THING LEFT, and it is JUDGEMENT (prior-art B2, "
            "archive/peer/2026-09-17-priorart-priorart-d1-sentinel-ops.md): HOW THE CONSTANT REACHES `Equal?`'s "
            "`y`. A Constant is a GObject, not a Node, so no `Get Outputs` reaches it, and Create Constant.vi's "
            "`Terminal` output dies with its op's dataflow (archive/2026-08-31-status-full-assembly-narrative.md"
            ":531-534, 'one fused op'). The two candidate answers - a FUSED create-const-and-connect op, or "
            "`Constant.Terminal` 634AC04 -> `Terminal.Connect Wire` 6349C03 (both halves already built inside "
            "OpConstValueN_v1 / OpStopFromNode_v0) - are a THIRD op either way, beyond the two s11g.1 "
            "authorises.\n"
            "  (d) plan s7.1's STREAMING TSV is NOT a D1 blocker any more: s11f.1 moved it to D2 after s7.3 "
            "measured that #376 save trace.vi already saves PERIODICALLY.")
    print(f"PHASE = {PHASE!r}  (structural relocation only; --full is not implemented)", flush=True)
    g._lv = None
    t0 = time.time()
    h0 = s0()
    if h0 is None:
        print("\nSTOP at S0. Nothing was copied, opened or edited; the original was only READ.", flush=True)
        print(f"\n=== build_d1_v0: {len(passes)} pass, {len(fails)} fail -> {', '.join(fails)} ===", flush=True)
        return 2

    result = {}
    try:
        ok, got = s1()
        if not ok:
            return 1
        inv0 = g.uids(TARGET, "Invoke")
        if not s1t():                       # plan §11h - the fixture TIFF writer goes BEFORE any move
            return 1
        loops = s2()
        if not loops:
            return 1
        r3 = s3(loops)
        if not r3:
            return 1
        panel_before, regs = s3c(loops)
        rew = None
        if PHASE == "full":
            # PHASE "full", stage 1 of 2: the RE-WIRE. Stage 2 (the eight queues, their endpoints, the sentinels
            # and #6384's new carrier) is listed in SKIPPED_PHASE and is NOT executed, because a sink that has no
            # route in stage 1 cannot be given one by a queue either - the log below says, per row, which.
            rew = phase_full_rewire(loops, regs, r3)
        s3d(loops, r3["kernel"])
        s4(loops)
        panel_after = g.panel_wiring(TARGET)
        before_by = {(r["uid"], r["label"]): r["wire"] for r in panel_before}
        after_by = {(r["uid"], r["label"]): r["wire"] for r in panel_after}
        gate("S3c panel survived: 114 rows, every label present",
             len(panel_after) == BEFORE["ControlTerminal"] and set(before_by) == set(after_by),
             f"{len(panel_after)} rows; lost {sorted(set(before_by) - set(after_by))[:5]}")
        gate("S3c ControlTerminal count unchanged", g.count(TARGET, "ControlTerminal") == BEFORE["ControlTerminal"],
             f"{g.count(TARGET, 'ControlTerminal')}")
        if PHASE == "full":
            print("\n=== PHASE 'full' stage 2 NOT executed - not silently passed:", flush=True)
            for nm, what in SKIPPED_PHASE[:6]:
                print(f"  SKIPPED-PHASE  {nm}: {what}", flush=True)
            fact(f"ExecState after the re-wire stage: {g.exec_state(TARGET)} "
                 f"(1 is only possible once EVERY cut terminal is re-wired AND the queue endpoints exist)")
            if s5(inv0):
                s6()
            else:
                g.close_panel(TARGET)
                try:
                    os.remove(TARGET)
                    fact(f"working copy deleted (not saved - a broken VI is never written): {TARGET}")
                except Exception as e:
                    fact(f"working copy NOT deleted ({str(e)[:60]})")
        else:
            print("\n=== PHASE 'relocate' ends here. NOT executed, and NOT silently passed:", flush=True)
            for nm, what in SKIPPED_PHASE:
                print(f"  SKIPPED-PHASE  {nm}: {what}", flush=True)
            fact(f"ExecState after the relocation: {g.exec_state(TARGET)} "
                 f"(0 is EXPECTED - the moves CUT border wires, plan s2b; nothing is re-wired in this phase)")
            fact("the target is NOT saved and NOT cold-opened: a relocation-only artefact is a broken VI, and "
                 "the skill forbids cold-loading a broken-saved VI headless (recompile spin)")
            g.close_panel(TARGET)
            try:
                os.remove(TARGET)
                fact(f"working copy deleted: {TARGET}")
            except Exception as e:
                fact(f"working copy NOT deleted ({str(e)[:60]}) - delete before the next run")
        result = dict(phase=PHASE, loops=loops, moved=r3["moved"], cut=r3["cut"], regs=regs, rewire=rew,
                      outer_cut=r3.get("outer_cut"), sr_changed=r3.get("sr_changed"),
                      queues=QUEUES, sentinels=SENTINELS, const_donors=CONST_DONORS,
                      size=os.path.getsize(TARGET) if os.path.exists(TARGET) else 0)
    finally:
        g._lv = None
        m1 = md5(ORIGINAL)
        gate("S6b original md5 AFTER", m1 == ORIG_MD5, m1)
        fact(f"LabVIEW handles after: {labview_handles()} (before {h0})")
        result["md5_after"] = m1
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)

    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== build_d1_v0: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
