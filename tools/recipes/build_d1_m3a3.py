r"""build_d1_m3a3.py - D1 staged build, RE-CUT 2026-09-22 AS **STAGE M3a-3b: ROW D ALONE**.

RE-CUT **IN PLACE**, NOT COPIED TO A `_v2` (CLAUDE.md, "Big or blocked work is SPLIT ... A full-length
retry under a new file name (`_v8`) is forbidden"; `cycle_runner.py` counts a renamed recipe as the same
recipe anyway). Runs 1 and 2 of this same file delivered ROW C; this cut deletes Row C from the row table
and carries it as a read-only PRECONDITION instead, so nothing already in the bed is redone.

PINNED ASTCHECK, run BEFORE the build, never after (Pre-decided 98(3)):
    py tools/bench/c60c_astcheck.py "tools/recipes/build_d1_m3a3.py" --route owner
`--route owner` because this file CREATES NO OBJECT and calls `move_in` NOWHERE (Pre-decided 62).

WHAT THIS STAGE IS. Input = **the bed** `claudeDev\D1_s3b_m3a3_20260922_081056.vi` (md5 33ef524e...,
306,951 B - run 2's accepted output, 26 gates pass / 2 fail where BOTH fails are the pre-decided Row-D
deferral). ROW C IS ALREADY IN IT AND IS NOT REDONE. This stage re-sources the ONE remaining downstream
consumer - the VISA session - from the OLD loop `#637` onto the NEW loop `#23032`'s RIGHT register.

THE ROW TABLE (Pre-decided 104 as amended by 111; Row C shown only to say it is DONE):

  ROW C - POSITION.  DONE IN THE BED, run 2. `Global #7202 'Global motor pos.vi'` t0 'Focus position'
                     reads `RightShiftRegister #23895`. Asserted here as a PRECONDITION, read-only,
                     never rebuilt (gate C0).
  ROW D - HANDLE.    delete wire 7506 ; SOURCE = NEW reg0 RIGHT #23868 OUTER = (Diagram #686 traverse
                     idx 19, Nodes[21] = loop #23032, t1 'Outgoing Handle', is_source True, BARE -
                     `tools/bench/diag_c75b_loopterms.log:76`, bare list `:82`) -> SINK =
                     `FlatSequenceInnerTunnel #7468` **LeftTerm #7488**, the end carrying wire 7506.

WHY THE SINK ADDRESS CHANGED (Pre-decided 109/110/111, measured by `tools/bench/diag_c77_rowd_addr.log`).
Run 2's P0 predicted `#7468`'s terminal is indexed on the owning `FlatSequence #681` NODE's terminal
table on `Diagram #686`. **That table does not exist**: `#686` has 27 `Nodes[]` rows and `#681` is in
none of them, `owner_of(#681)` is `TopLevelDiagram #536`, and `find_node` misses ALL THREE FlatSequences
(#43914 nested, #12938 and #681 top-level; 173/173 diagrams, 635 nodes, 0 scan errors) - so the miss
tracks the **class**, not the owner: a `FlatSequence` is a direct child of `GObject` and never a `Node`,
therefore never a `Nodes[]` member. 107's PROHIBITION stands unchanged (no owner walk - an owner chain
terminates SILENTLY at a `FlatSequenceFrame`, error 1055, `docs/toolkit-capabilities.md:61`; no improvised
address; no GUI fallback); only its prescribed ROUTE is replaced, by the reader we already own:
`OpFsInnerTunnelTerm_v0` on uid 7468 answers with every error column empty - `LeftTerm #7488 wire #7506`,
`RightTerm #7471 wire #7448` - and a control read on an unrelated FSIT #123 answers the same way, so the
capability is of the CLASS, not of the target.

RE-CUT AGAIN 2026-09-22 (cycle 69/80) TO **ROUTE A, THE SWAPPED CALL** - Pre-decided 115/116/117/118,
from `archive/peer/2026-09-22-c79-rowd-writer.md` (claude/hypothesis, opus max, ANSWERED). THE PREVIOUS
CUT HALTED AT ITS OWN GATE W1, and that halt is now known to rest on a CONVENTION, not a measurement:
`docs/NAMES.md:847`'s "6349C03 is invoked on the SINK" is marked "labviewwiki, adopted" and the wiki
page does not say it (Pre-decided 115). The W1 CENSUS is not disputed - 4/4 maps declaring method
6349C03 take a (diagram, `Nodes[]`, `Terminals[]`) sink and 0 take a uid - but what it proves is "no
writer in the FLEET takes a uid SINK", not "this wire cannot be written".

THE ROUTE (Pre-decided 116-A, the review's own cheapest test, run BEFORE any construction):
`OpConnectFromWire_v0` WITH THE ROLES EXCHANGED. Its SOURCE half is ALREADY uid-addressed (`wire_uid` +
a `Wire.Terms[]` index, property 6371003), so it is handed the FSIT TERMINAL #7488 - the true SINK - and
its (diagram, `Nodes[]`, `Terminals[]`) triple is handed the NEW loop's BARE `Outgoing Handle` - the
true SOURCE, which IS index-addressable. The Invoke then sits on the BARE terminal and receives #7488 as
`Wire Source`. NOTHING NEW IS BUILT.

THE MEASUREMENT - THREE ARMS, IN THIS ORDER; the first two on DATED SCRATCH COPIES that are DELETED.
 ARM A1  DELETE-THEN-CONNECT (Pre-decided 106's ordering). Delete wire 7506, THEN make the swapped call
         with `wire_uid` 7506. The known tension: 106 requires the delete first (an already-wired sink
         is a MEASURED silent no-op, `tools/gscript.py:2522-2523`), but the swapped call resolves #7488
         FROM wire 7506, which the delete destroys. A DEAD WIRE UID FAILING IS A LEGITIMATE AND EXPECTED
         OUTCOME - it is recorded VERBATIM, never worked around.
 ARM A2  CONNECT-THEN-DELETE. Resolve #7488 and its `Wire.Terms[]` index while 7506 is ALIVE, make the
         swapped call, and delete 7506 ONLY IF the connect reported success.
 ARM 3   THE BED, and ONLY if A1 or A2 passed every gate on its scratch (Pre-decided 116-A: "If A works,
         Row D proceeds on it in the same dispatch and NOTHING NEW IS BUILT"). If BOTH fail the run
         STOPS: Route B (`OpConnectByUid`) is EXPENSIVE CONSTRUCTION and gets a FRESH CYCLE (Pre-decided
         116-B). No op is built here, no address is improvised, and the bed is not touched.

THE PREDICTION CONTRACT, WRITTEN BEFORE THE RUN.
 W1 (FILES ONLY, BEFORE LabVIEW IS TOUCHED AT ALL - the first gate in the run). Every row has a WRITER
    bound to its sink kind. Row D's sink kind `tunnel_uid` is bound to the SWAPPED call, whose op VI
    `OpConnectFromWire_v0.vi` must be on disk (W0) and must OPEN over COM (W0b) BEFORE the first
    mutation. Run 1's whole cost was this ordering being absent: its delete ran and THEN the writer
    raised `com_error 5507 File not found` in `GetVIReference`, leaving `Global #7202` t0 BARE - a
    dropped consumer and a rejected artefact.
    ⚠️ MEASURED 2026-09-22 09:2x, `tools/bench/c78_rowd_writer.log`: of the FOUR label maps declaring
    method 6349C03 address their SINK as (`index`, `index 2`, `index 3`) = (diagram, `Nodes[]`,
    `Terminals[]`), and the count of writers whose SINK is addressed by a UID is 0. That is WHY the
    roles are EXCHANGED here rather than a uid-sink writer being built: the census says what the fleet's
    writers take, not what the method requires (Pre-decided 115).
 C0 (PRECONDITION, read-only, asserted not rebuilt, ONCE PER ARM). The net carried by `Global #7202` t0
    'Focus position' still has EXACTLY ONE source terminal of ANY owner class and it is
    `RightShiftRegister #23895` (Row C, delivered in the bed). PD85 violations 0 on the walk. If C0
    fails the arm target is not what this stage was told it is: STOP, delete nothing. C0 IS ALSO THE
    READER CALIBRATION for gate (ii) below - see P3b.
 P0 (ROW D's SINK). `OpFsInnerTunnelTerm_v0` on uid 7468 returns `LeftTerm` = a terminal uid with its
    error column empty, and that terminal carries wire 7506. Anything else - an error column, a missing
    uid, or a face carrying a different wire - is a FAILED PREDICTION: STOP, delete nothing, improvise
    nothing (Pre-decided 107's prohibition, which 109 leaves untouched).
 P1 The loop border `#23032` resolves live at Diagram idx 19, Nodes[21], t1 'Outgoing Handle',
    is_source True and BARE (`diag_c75b_loopterms.log:76`, bare list `:82`). THIS IS THE INVOKE SITE.
 P2 (THE SOURCE HALF OF THE SWAPPED CALL). `OpWireSource_v5` walks `Wire.Terms[]` BY INDEX, so the index
    it reports for the NON-source row of wire 7506 IS the `Wire.Terms[]` index the swapped call needs.
    PREDICTION: exactly one non-source row with a real owner, and that owner is
    `FlatSequenceInnerTunnel #7468`. If it is not unique the arm STOPS - no index is guessed.
 P3 THE ACCEPTANCE (Pre-decided 85 + 106 + 111 + 117, not relaxed), asserted on an ORDERED SECOND,
    IDEMPOTENT pass (`wire_delta` 0), NEVER in the pass that makes the connection (Pre-decided 94):
      (i)   the wire the SINK terminal #7488 carries afterwards has EXACTLY ONE source terminal of ANY
            owner class (counted before any class filter - Pre-decided 77) and it is `#23868`'s OUTER;
      (ii)  PRE-DECIDED 117, THE BRANCH GATE - that source terminal's OWNER is on the NEW side (P3b);
      (iii) the OLD loop `#637` and the OLD register `#4334` are OFF the net entirely - a silent branch
            of 7506 would leave one of them on it, which passes every count-shaped check and is a
            rule-1a computation change;
      (iv)  PD85 violations 0 on EVERY walk of the arm, or no walk in it is believed;
      (v)   the op's OWN `Wire.Is Broken?` 6371004 readback is FALSE on the SEPARATE ordered pass.
    Hop count is an OUTPUT, never a criterion (Pre-decided 90).
 P3b (THE READER CALIBRATION, so gate (ii) is stated in the MACHINE's vocabulary and not in a guess).
    Pre-decided 117 is written as "`OpWireSource_v5` must report that source terminal's OWNER ==
    `WhileLoop #23032`", and the peer wrote the branch signature as `WhileLoop #637`. THE MACHINE HAS
    ALREADY ANSWERED THIS, in the DELIVERED Row C of this very file: `build_d1_m3a3_run2.log:182` reads
    the accepted sink net as `[('RightShiftRegister', 23895)]` for the ANALOGOUS terminal (the other
    RIGHT register's OUTER on the SAME loop #23032), and `:72` reads the OLD side as
    `('RightShiftRegister', 4256)`, not `WhileLoop #637`. This reader names the SHIFT REGISTER, never
    the loop. So gate (ii) is evaluated as "the owner is #23868, the NEW register whose OUTER that
    terminal is, and neither #4334 nor #637 appears anywhere on the net" - 117's SUBSTANCE in the
    reader's own vocabulary - while 117's LITERAL form (`owner == 23032`) is ALSO evaluated and REPORTED
    beside it, together with this arm's own live Row-C calibration reading from C0. Both numbers are
    printed; nothing is quietly substituted, and the discrepancy is carried to the judgement session.
 P4 `LANDED` IS SOURCE IDENTITY (Pre-decided 106). Never "the sink is still wired", never a wired-count
    delta: `connect_from_wire` into an already-wired sink is a MEASURED SILENT NO-OP that passed a gate
    five runs running (`tools/bench/build_d1_m3a1.log:1174,:1875,:2593,:3311`; cause
    `tools/gscript.py:2522-2523`). ARM A1 IS THAT ORDERING; ARM A2 IS THE OTHER ONE, AND WHICH OF THEM
    WORKS IS THE MEASUREMENT, NOT AN ASSUMPTION.
 P5 DEAD ENDS, RECORDED SO THEY ARE NOT RE-TRIED (Pre-decided 118): `Tunnel.Inside Terminals[]` 6356000
    and `Tunnel.Outside Terminal` 6356001 can NEVER address #7468 (a `FlatSequenceInnerTunnel` is not a
    `Tunnel`; its real properties are `Left Terminal` 1C3A9000 / `Right Terminal` 1C3A9001);
    `Node.Connect Wires` needs both ends to be `Node`s; `Create Described Wire` is itself a `Terminal`
    method. None of them is called here.

THE TWO DEFECTS THE c76 / c76b GATES NAMED, FIXED HERE.
  (1) `%`-FORMAT `TypeError`. Every FACT line now goes through `_f()`, which formats inside a try and,
      on `TypeError`, prints the template and the argument count and records an OUR-CODE DEFECT (H9)
      instead of killing the phase. A formatting bug is a bug of OURS - never a machine refusal
      (Pre-decided 100 SS2) - and it must never again be able to abort a run that had already mutated.
  (2) `GetVIReference` `com_error`. `open_op()` replaces the bare `safe()` wrapper around `g.op(...)`:
      a `com_error` there is OUR code (a path that is not on disk, a broken op VI), so it becomes a
      NAMED GATE FAILURE carrying the RAW error text plus an H9 defect record - never a FACT line that
      a later phase silently steps past. Run 1 died precisely in that blind spot, AFTER a delete.

PRIOR ART. `archive/peer/2026-09-22-priorart-c75-m3a3.md` (all five verdicts ACCEPTED by the cycle-65
judgement session, none refuted) is the prior-art discharge for THIS stage - its row table names Row D
explicitly - and `archive/peer/2026-09-22-c76b-m3a3-run2-failpred.md` (claude/hypothesis, ANSWERED,
disposed) is the failed-prediction review of run 2, whose "cheapest discriminating measurement" was run
in full as `tools/bench/diag_c77_rowd_addr.log`. Findings carried into this cut:
  - A3/A4  -> the row pairing is the machine's (Pre-decided 104/105), not STATUS NEXT's transpose.
  - B2     -> delete-before-connect is mandatory and `LANDED` is source identity (P4).
  - B3     -> `delete_by_uid` / `pd85_violations` / `wire_walk` / `print_walk` / `node_view` are
              IMPORTED from `build_d1_m3a1`, never rewritten; no owner walk anywhere.
  - B4     -> the consumer nets, the Global's terminal index and both owning diagrams are CITED from
              `diag_c73_m3a2_rows.log` / `diag_c75_m3a3_rows.log` / `diag_c75b_loopterms.log` /
              `build_d1_m3a3_run2.log`, NOT re-measured (Pre-decided 108).
  - c76b   -> a `FlatSequence` is never addressed through `Nodes[]` again, and `diag_index(#681)` is
              never used as a membership test (it RAISES `ValueError: 681 is not in list`).

WHAT IS REUSED AND WHAT IS NOT (Pre-decided 108 - the helpers are reused, not rewritten).
  imported and called: `build_d1_m3a1`'s `node_census` / `new_nodes` / `find_node` / `node_view` /
    `terms_at` / `term_state` / `delete_by_uid` (:583) / `pd85_violations` (:811) / `print_walk` (:823);
    `build_opfstunnelterm_v2.read_tunnel` for the sink address (the op is 38/38,
    `tools/bench/build_opfstunnelterm_v2_run1.log:160-161`).
  NOT called, and why, stated rather than left silent:
    - `build_d1_m3a1.wire_walk` (:844) binds to THAT module's own `WORK` path; the one-line wrapper
      below calls `OpWireSource_v5` on THIS run's TARGET and hands the result to the imported
      `print_walk`, so the printing and the PD85 precondition are the imported code.
    - `build_d1_m3a1.identity_gate` (:857) is the Pre-decided 70 BORDER-ROW test: it PASSES only when a
      `LoopTunnel` uid is both a new sink on the source wire and the one source of the sink wire. This
      row creates no LoopTunnel, so that gate cannot apply; the applicable test is Pre-decided
      85/106/111's one-source identity, coded in `acceptance()` below.
    - `build_d1_m3a1.step_6_sixth_row` (:1530) is the tunnel-sink RESOLUTION SHAPE - the entry
      identified by WHAT IT CARRIES, never a carried index and never a guessed name. PHASE 0 keeps that
      shape and changes only the table it reads, from the owning structure's `Nodes[]` row (which does
      not exist for a FlatSequence) to the tunnel's OWN table, read by uid with zero hops.

RULE COMPLIANCE.
  rule 1  - the ORIGINAL, S1, S2 and the bed are READ ONLY, md5-gated at both ends. The input artefact is
            COPIED once with shutil and never opened over COM; H2 proves its md5 is unchanged.
  rule 1a - the artefact is STILL NOT computation-equivalent to the original and is NEVER RUN (34(f),
            Pre-decided 97). Equivalence is claimed at the end of the M3 chain, never at a stage boundary.
            No Local, no substitute source, no improvised address: a row that cannot be resolved STOPS.
  rule 1b - rig assembled: no motor, no ASI, no camera. `tools/motor_gate.py` is not called.
  rule 1c - nothing here touches a frame path.
  GUI     - the ONLY GUI act reachable is `gscript.gui_save` via `save(allow_broken=True)` on a broken VI
            (Pre-decided 88/96/101), with USER RULE 17:5x in full and the captures ASSERTED to exist. The
            caller does NOT pre-quote the capture paths: `gscript.q()` quotes exactly once (the measured
            cause of M3a-1's missing captures, `build_d1_m3a1.log:3402`).
  split   - the stage always leaves a file (user, 2026-09-19). `ExecState` is NEVER a criterion and never
            a discriminator here (Pre-decided 89/97); its cause is formally OPEN.
"""
import json
import os
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
import build_d1_m3a1 as M                                                          # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index                                                 # noqa: E402
# `build_d1_v0.owner_of` is DELIBERATELY NOT IMPORTED: Pre-decided 107's prohibition (an owner chain
# terminates SILENTLY at a FlatSequenceFrame, error 1055) is enforced by this file owning no owner-walk
# verb at all, rather than by remembering not to call one.
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS             # noqa: E402
from build_opconnectfromwire_v0 import connect_from_wire as CONNECT_FROM_WIRE      # noqa: E402
from build_opconnectfromwire_v0 import OP as OP_CONNECT_FROM_WIRE                  # noqa: E402
from build_opfstunnelterm_v2 import read_tunnel as READ_FSIT                       # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")

# ---------------------------------------------------------------- the pins, all read from files
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5), ("S1 D1_s1_copy", S1_ARTEFACT, S1_MD5),
        ("S2 D1_s2_loops", S2_ARTEFACT, S2_MD5), ("THE BED", BED, BED_MD5))
TOOL_PINS = (os.path.join(ROOT, "tools", "gscript.py"),
             os.path.join(BENCH, "c60c_astcheck.py"))

# THE INPUT ARTEFACT - **THE BED**, M3a-3 run 2's accepted output, WITH ROW C ALREADY IN IT.
# NEVER MODIFIED, NEVER OPENED, NEVER RUN (34(f)). Run 1's artefact `D1_s3b_m3a3_20260922_075611.vi`
# (md5 2461a749...) is REJECTED and must never be used as a bed: its delete ran and its rebuild raised,
# so `Global #7202` t0 is BARE there - a dropped consumer.
INPUT = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3_20260922_081056.vi")
INPUT_MD5 = "33ef524e0b6b193a158c9221474c68e3"
INPUT_BYTES = 306951

STAMP = time.strftime("%Y%m%d_%H%M%S")
BED_TARGET = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3b_%s.vi" % STAMP)
TARGET_PREFIX = "D1_s3b_m3a3b_"
# THE SCRATCH COPIES the two measurement arms run on. Dated, unique per run, DELETED in the same run
# (CLAUDE.md: "Scratch VIs: unique name per run, created and deleted in the same run").
SCRATCH_A1 = os.path.join(g.CLAUDEDEV, "SCRATCH_rowdA1_%s.vi" % STAMP)
SCRATCH_A2 = os.path.join(g.CLAUDEDEV, "SCRATCH_rowdA2_%s.vi" % STAMP)
# `TARGET` IS THE **CURRENT** TARGET and is re-pointed by `set_target()` at each arm. Every phase below
# reads this module global at CALL time, so one assignment re-points the whole file at the arm's own
# file; nothing carries a path in a closure.
TARGET = BED_TARGET
OUT = os.path.join(BENCH, "build_d1_m3a3b.json")
# THE WRITER'S OWN OP VI, CHECKED ON DISK BEFORE ANY LabVIEW CALL (gate W0 in phase_files).
# RUN 1 (2026-09-22 07:56) DIED HERE: `gscript.connect_nested_v2` EXISTS as a def - `c60c_astcheck` gate 4
# verifies exactly that and PASSED it - but `OpConnectNested_v2.vi` IS NOT ON DISK in claudeDev, so the call
# raised `com_error 5507 (Hex 0x7) File not found` inside `GetVIReference`, AFTER the row's wire had already
# been deleted. A gscript verb existing is NOT its op VI existing; this file checks the file itself.
CFW_LABELS = json.load(open(os.path.join(BENCH, "opconnectfromwire_v0_labels.json"),
                            encoding="utf-8"))

# ---------------------------------------------------------------- the topology, all RE-MEASURED live
TOP = 0
D686 = 686            # the diagram that carries the loop borders, the consumers and both wires
LOOP_A = 23032        # the NEW WhileLoop - its RIGHT registers are this stage's sources
FLATSEQ = 681         # owner of FlatSequenceInnerTunnel #7468 - NEVER addressed through Nodes[] (PD 110)
TUNNEL_D = 7468       # Row D's sink OBJECT (a FlatSequenceInnerTunnel)
TUNNEL_D_TERM = 7488  # Row D's sink TERMINAL - LeftTerm, the end carrying wire 7506 (PD 109/111)
OLD_LOOP = 637        # the OLD WhileLoop - NOT censused here (Pre-decided 108: cited, not re-measured)
OLD_LOOP_TERM_NAME = "Outgoing Handle"   # #637 t10, wire 7506's SOURCE side, must be OFF the net after

# ROW C's PRECONDITION - asserted read-only, NEVER rebuilt (it is already in the bed, run 2).
ROWC = {"tag": "C POS (PRECONDITION ONLY)", "sink_uid": 7202, "sink_name": "Focus position",
        "expect_source_uid": 23895, "expect_source_class": "RightShiftRegister",
        "evidence": "tools/bench/build_d1_m3a3_run2.log - sink net 25231 has exactly ONE source terminal "
                    "of ANY class, RightShiftRegister #23895, PD85 violations 0, asserted on the ordered "
                    "idempotent second pass (wire_delta 0); the OLD #4256 is OFF the net"}

# (tag, wire to delete, old source, new RIGHT register, its border terminal name, the sink)
# ROW C IS GONE FROM THIS TABLE ON PURPOSE - it is in the bed and is not redone (the brief, and
# CLAUDE.md's "a step is not done until it has left a file": the file exists, so the step is done).
ROWS = [
    {"tag": "D VISA", "wire": 7506, "old_source": 4334, "new_reg": 23868,
     "src_name": "Outgoing Handle", "src_expect_term": 1,
     "sink_kind": "tunnel_uid", "sink_uid": TUNNEL_D, "sink_term_uid": TUNNEL_D_TERM,
     "sink_name": None, "sink_expect_node": None, "sink_expect_term": None,
     "why": "wire 7506 carries the VISA SESSION out of the OLD loop #637 (t10 'Outgoing Handle') into "
            "`FlatSequenceInnerTunnel #7468` LeftTerm #7488. Its new source is the NEW loop's VISA "
            "register #23868 RIGHT OUTER, or the VISA path keeps reading a loop the restructure is "
            "replacing (rule 1a, Pre-decided 69)."},
]

# ============================================================ THE WRITER TABLE - gate W1 reads THIS
# A writer is bound to a SINK KIND, not to a row. A row with no writer is NOT ATTEMPTED - it is never
# approximated, never routed through a Local, never clicked (rule 1a; Pre-decided 107's prohibition,
# left untouched by 109).
#
# PRE-DECIDED 116-A: `tunnel_uid` is now bound to `OpConnectFromWire_v0` WITH THE ROLES EXCHANGED. The
# op's SOURCE half is already uid-addressed (`wire_uid` + a `Wire.Terms[]` index, 6371003), so it takes
# the FSIT TERMINAL #7488 - the true SINK - and its index triple takes the NEW loop's BARE border
# terminal - the true SOURCE. The 6349C03 census (0 writers with a uid SINK) is NOT overturned; it is
# side-stepped, because "the Invoke sits on the sink" was a CONVENTION of our one donor lineage and not
# a property of the method (Pre-decided 115).
WRITERS = {
    # sink kind -> (callable, the op VI that must be on disk, how the sink is addressed)
    "tunnel_uid": (CONNECT_FROM_WIRE, OP_CONNECT_FROM_WIRE,
                   "THE SWAPPED CALL: the TERMINAL UID #%d is handed to the op's uid-addressed SOURCE "
                   "half (wire_uid + Wire.Terms[] index) and the Invoke sits on the NEW loop's BARE "
                   "border terminal, addressed as (diagram idx, Nodes[] idx, Terminals[] idx)"
                   % TUNNEL_D_TERM),
}

# ============================================================ THE THREE ARMS (Pre-decided 116)
# A1 first because it is Pre-decided 106's ordering; A2 second because it is the only other ordering the
# swapped call admits. THE BED ARM IS NOT IN THIS TABLE - it is built in main() from the WINNER, and only
# if there is one.
DELETE_FIRST = "DELETE-THEN-CONNECT"
CONNECT_FIRST = "CONNECT-THEN-DELETE"
ARMS = [
    {"name": "A1", "ordering": DELETE_FIRST, "target": SCRATCH_A1, "scratch": True,
     "why": "Pre-decided 106's MEASURED ordering: connect_from_wire into an ALREADY-WIRED sink is a "
            "silent no-op (gscript.py:2522-2523), so the delete precedes the connect. The tension this "
            "arm measures: the swapped call resolves terminal #%d FROM wire %d, and the delete destroys "
            "that wire, so `UID to GObject Reference.vi` may refuse the dead uid. A REFUSAL HERE IS A "
            "LEGITIMATE, EXPECTED OUTCOME and is recorded verbatim." % (TUNNEL_D_TERM, ROWS[0]["wire"])},
    {"name": "A2", "ordering": CONNECT_FIRST, "target": SCRATCH_A2, "scratch": True,
     "why": "The other ordering: resolve #%d and its Wire.Terms[] index while wire %d is ALIVE, make the "
            "swapped call, and delete wire %d ONLY IF the connect reported success. The hazard this arm "
            "measures is the one the c79 review named: an already-wired terminal handed to `Wire Source` "
            "is BRANCHED (gscript.py:2522-2523), which would leave the OLD source on the net - a "
            "rule-1a computation change that passes every count-shaped check (Pre-decided 117)."
            % (TUNNEL_D_TERM, ROWS[0]["wire"], ROWS[0]["wire"])},
]

RUN_DEADLINE_S = 45 * 60.0       # the `bgrun --max-min` this file is launched under
RESERVE_S = 420.0                # held back for the save and the hygiene tail
ROW_MIN_S = 300.0

T_START = time.time()
passes, fails, facts, refusals = [], [], [], []
# OUR-CODE DEFECTS - Python exceptions raised by THIS SCRIPT, kept SEPARATE from machine refusals
# (Pre-decided 100 SS2): a bug of ours must never be reported as "a mutator call the machine refused".
defects = []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "target": BED_TARGET, "input": INPUT,
     "task": "STAGE M3a-3b = ROW D ALONE, ROUTE A (Pre-decided 115/116/117/118): delete wire 7506 and "
             "re-source the VISA consumer `FlatSequenceInnerTunnel #7468` LeftTerm #7488 from the NEW "
             "loop #23032's RIGHT register #23868 OUTER, using `OpConnectFromWire_v0` WITH THE ROLES "
             "SWAPPED. THREE ARMS: A1 delete-then-connect and A2 connect-then-delete, each on its own "
             "dated SCRATCH copy of the bed (deleted in this run); then, ONLY if one of them passed "
             "every gate, the same ordering on THE BED, saved as the stage artefact. NOTHING IS BUILT.",
     "route_selection_rule": "Pre-decided 116-A: if A works, Row D proceeds on it in the SAME dispatch "
                             "and nothing new is built. 116-B: if BOTH orderings fail, Route B "
                             "(`OpConnectByUid`) is EXPENSIVE CONSTRUCTION and gets a FRESH CYCLE - it "
                             "is NOT improvised at the end of this dispatch, and no op is built here.",
     "pinned_astcheck": 'py tools/bench/c60c_astcheck.py "tools/recipes/build_d1_m3a3.py" --route owner',
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "gating_policy": "hygiene + PHASE 0 + the per-row acceptance gates + the save. A negative "
                      "MEASUREMENT is a FACT line; a row that never happened is a FAIL.",
     "row_table_source": "docs/cycle27-plan.md Pre-decided 104 (the CORRECTED table; STATUS NEXT's "
                         "sentence was transposed - prior-art finding A3)",
     "artefact_is_not_computation_equivalent":
         "AFTER M3a-3 THE ARTEFACT IS STILL NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL (Pre-decided 97). "
         "It is BROKEN BY DESIGN and is NEVER RUN (34(f)).",
     "execstate_policy": "ExecState is NEVER a criterion and NEVER a discriminator (Pre-decided 89/97); "
                         "its cause is formally OPEN. It is logged as a timeline FACT only.",
     "is_broken_policy": "`OpConnectFromWire_v0`'s own `Wire.Is Broken?` 6371004 readback IS ORDERED "
                         "AFTER the write by its gate W7b (build_opconnectfromwire_v0.py:414), which is "
                         "why Pre-decided 116's acceptance may use it - and only on the SEPARATE ordered "
                         "pass, never as a type discriminator and never in place of source identity.",
     "no_new_op": True, "no_new_verb": True, "no_new_device": True, "no_new_checker": True,
     "move_in_not_called": "this file calls move_in nowhere and imports it nowhere - hence --route owner",
     "creates_no_object": True,
     "remove_bad_wires_scripted": "not imported, not called (BANNED since cycle 58)",
     "no_whole_vi_gobject_census": True,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run - the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py is not called",
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "purges": [], "rows": {}, "phase0": {}, "arms": {}, "route_selection": {}, "build": {}}
K = R["build"]


class Halt(Exception):
    pass


# ============================================================================== reporting primitives
def gate(name, ok, detail=""):
    # `FAIL`, NOT `**FAIL**` (37(i)): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def _f(tmpl, *args):
    """DEFECT FIX (1), the `%`-format TypeError the c76 gate named. A mis-counted format template is a bug
    in THIS SCRIPT, and before this it could raise out of a FACT line - i.e. abort a phase that had already
    mutated the artefact, for a reporting mistake. Now it degrades: the template and the arguments are
    printed verbatim and the mistake is recorded as an OUR-CODE DEFECT (H9), never as a machine refusal
    (Pre-decided 100 SS2)."""
    if not args:
        return tmpl
    try:
        return tmpl % args
    except (TypeError, ValueError) as e:                                           # noqa: BLE001
        rec = {"where": "_f() format", "exception_type": type(e).__name__, "message": str(e)[:200],
               "source_line": "template %r with %d argument(s)" % (tmpl[:160], len(args)),
               "raised_by": "OUR OWN PYTHON CODE, not the machine"}
        defects.append(rec)
        return ("FORMAT DEFECT (%s: %s) template=%r args=%r - an OUR-CODE DEFECT, counted by H9"
                % (type(e).__name__, str(e)[:120], tmpl[:160], [repr(a)[:60] for a in args]))


def fact(line, *args):
    line = _f(line, *args)
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def refusal(where, msg):
    """A MUTATOR CALL **THE MACHINE** REFUSED. Never called for a Python exception of ours - that is
    `defect()` and gate H9 (Pre-decided 100 SS2)."""
    refusals.append({"where": where, "error_verbatim": msg})
    fact("MACHINE REFUSAL at %s: %s" % (where, msg))


def defect(where, exc):
    """A DEFECT IN OUR OWN PYTHON CODE - an exception raised by THIS SCRIPT, not by LabVIEW."""
    import traceback as _tb
    frames = _tb.extract_tb(exc.__traceback__)
    site = ("%s:%d in %s()" % (os.path.basename(frames[-1].filename), frames[-1].lineno, frames[-1].name)
            if frames else "source line unavailable")
    rec = {"where": where, "exception_type": type(exc).__name__, "message": str(exc)[:300],
           "source_line": site, "raised_by": "OUR OWN PYTHON CODE, not the machine"}
    defects.append(rec)
    fact("OUR-CODE DEFECT at %s: %s: %s  RAISED AT %s - a BUG IN THIS SCRIPT; the machine refused "
         "NOTHING here (Pre-decided 100 SS2); counted by H9, never by H8."
         % (where, rec["exception_type"], rec["message"], site))
    return rec


def head(t):
    print("\n---------- %s" % t, flush=True)


def set_target(path):
    """Re-point the module global `TARGET` at THIS arm's own file. Every phase below reads `TARGET` at
    CALL time, so one assignment re-points all of them; no path is captured in a closure, and the two
    scratch arms therefore cannot touch the bed artefact's name."""
    global TARGET
    TARGET = path
    R.setdefault("targets_used", []).append(path)


def safe(label, fn, default=None):
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def open_op(op_path, gate_name):
    """DEFECT FIX (2), the `GetVIReference` `com_error` the c76b gate named (H9).

    `g.op(path)` goes through `Application.GetVIReference`. A `com_error` there is NEVER a machine
    refusal of a mutation - it is OUR code handing LabVIEW a path that is not on disk, or an op VI that
    does not open. Run 1 died exactly there (`com_error 5507 (Hex 0x7) File not found`), AFTER the row's
    wire had been deleted, and the bare `safe()` wrapper turned it into a FACT line that the next phase
    stepped straight past. It is now a NAMED GATE FAILURE carrying the RAW error text, plus an H9 defect
    record, and the caller is expected to HALT on a False return - never to skip silently."""
    if not op_path:
        gate(gate_name, False, "no op VI is bound for this sink kind")
        return None
    on_disk = os.path.isfile(op_path)
    if not on_disk:
        gate(gate_name, False, "the op VI IS NOT ON DISK: %s" % op_path)
        fact("OUR-CODE DEFECT: %s is not on disk - a gscript verb existing is NOT its op VI existing "
             "(run 1's measured cause). Counted by H9, never by H8." % op_path)
        defects.append({"where": gate_name, "exception_type": "FileNotFound",
                        "message": "op VI not on disk: %s" % op_path,
                        "source_line": "open_op() disk check",
                        "raised_by": "OUR OWN PYTHON CODE, not the machine"})
        return None
    try:
        ref = g.op(op_path)
    except Exception as e:                                                         # noqa: BLE001
        raw = "%s: %s" % (type(e).__name__, repr(e)[:400])
        gate(gate_name, False, "GetVIReference RAISED, RAW: %s ; path %s" % (raw, op_path))
        defect("%s g.op(%s) - a com_error in GetVIReference is OUR CODE, not a machine refusal"
               % (gate_name, os.path.basename(op_path)), e)
        return None
    gate(gate_name, ref is not None, op_path)
    return ref


def probe_hash(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["machine_refusals"] = refusals
    R["our_code_defects"] = defects
    R["elapsed_s"] = round(time.time() - T_START, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T_START) - RESERVE_S


def read_es(tag):
    t0 = time.time()
    try:
        es = g.exec_state(TARGET)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    row = {"step": len(R["exec_state_timeline"]) + 1, "tag": tag, "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    # FIVE specs, FIVE arguments (c60c_astcheck gate 10 reads this statically before the launch).
    fact("ExecState [%02d %s] = %r   (+%.1f s, read cost %.2f s) - NEVER a criterion, NEVER a "
         "discriminator (Pre-decided 89/97)"
         % (row["step"], tag, es, row["t_since_start_s"], row["read_cost_s"]))
    return es


def counts(tag, classes=("Node", "Wire", "LoopTunnel", "Tunnel", "LeftShiftRegister",
                         "RightShiftRegister")):
    """NARROW CLASS CENSUSES ONLY - never a whole-VI GObject census (six of those took the handle count
    34,602 -> 91,288)."""
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(TARGET, cc))
    K.setdefault("censuses", {})[tag] = rec
    fact("%s counts: %r" % (tag, rec))
    return rec


# ============================================================ the uid-ECHOED readers (the A7 pattern)
def wire_walk(tag, wire_uid):
    """`OpWireSource_v5(UID 2 = wire_uid)` on THIS run's TARGET, printed and PD85-checked by the
    IMPORTED `build_d1_m3a1.print_walk` (:823) / `pd85_violations` (:811). M3a-1's own `wire_walk`
    (:844) is not called because it binds to THAT module's `WORK` path."""
    if not wire_uid:
        fact("%s wire 0 - the terminal is BARE, there is no wire to walk" % tag)
        return [], ""
    walk, err = safe("%s OpWireSource_v5(UID 2 = %r)" % (tag, wire_uid),
                     lambda: WIRE_TERMS(TARGET, int(wire_uid), n=8), [])
    M.print_walk(tag, wire_uid, walk, err)
    return walk or [], err


def pd85(wire_uid, walk):
    return M.pd85_violations(wire_uid, walk)


def node_table(uid, hints, tag, quiet=False):
    """The node's live (diagram index, Nodes[] index) and its FULL terminal table, uid-echoed. The
    address is ALWAYS resolved live - an index is never carried from a census (T2c2's recorded cause)."""
    loc, rows = M.node_view(TARGET, uid, hints, tag, quiet=quiet)
    f = loc.get("found") or {}
    rec = {"uid": uid, "diagram_index": f.get("diagram_index"), "diagram_uid": f.get("diagram_uid"),
           "nodes_index": f.get("nodes_index"), "label": f.get("label"),
           "uid_echo": loc.get("uid_echo"), "n_terminals": len(rows)}
    fact("%s #%d LIVE: Diagram idx %r (uid #%r), Nodes[%r], label %r, uid echo %r, %d terminal(s)"
         % (tag, uid, rec["diagram_index"], rec["diagram_uid"], rec["nodes_index"], rec["label"],
            rec["uid_echo"], len(rows)))
    return rec, rows


def purge_junk(nodes_before, tag, hints):
    """The measured junk shape of the OpConnect* family: a fresh `Invoke` node with ZERO wired terminals.
    Anything else that is new is REPORTED VERBATIM and LEFT ALONE - deleting a node whose terminal table
    was never read is the one branch that could destroy the artefact."""
    nodes_after, _ = M.node_census(TARGET, "%s AFTER" % tag)
    fresh = M.new_nodes(nodes_before, nodes_after)
    rec = {"tag": tag, "node_count_before": len(nodes_before), "node_count_after": len(nodes_after),
           "new_uids": [(n["uid"], n["class"], n["pos"]) for n in fresh], "deleted": [],
           "reported_not_deleted": []}
    fact("%s CENSUS DIFF: Node %d -> %d ; %d new uid(s): %r"
         % (tag, len(nodes_before), len(nodes_after), len(fresh), rec["new_uids"]))
    for n in fresh:
        loc, rows = M.node_view(TARGET, n["uid"], hints, "%s new #%s" % (tag, n["uid"]))
        wired = [t for t in rows if t.get("has_wire")]
        entry = {"uid": n["uid"], "class": n["class"], "pos": n["pos"],
                 "label": (loc.get("found") or {}).get("label"),
                 "diagram_uid": (loc.get("found") or {}).get("diagram_uid"),
                 "terminals": rows, "n_terminals": len(rows), "n_wired": len(wired)}
        if n["class"] == "Invoke" and rows and not wired:
            fact("%s the junk node's FULL terminal table is printed above; %d terminal(s), %d WIRED - the "
                 "purge precondition (ZERO wired) HOLDS" % (tag, len(rows), len(wired)))
            entry["delete"] = M.delete_by_uid(TARGET, "Node", n["uid"], "%s purge" % tag)
            rec["deleted"].append(entry)
        else:
            rec["reported_not_deleted"].append(entry)
            fact("%s NEW NODE NOT DELETED (not the measured junk shape, or its table could not be read): "
                 "#%s class %r label %r, %d terminal(s), %d wired - REPORTED, left alone"
                 % (tag, n["uid"], n["class"], entry["label"], entry["n_terminals"], entry["n_wired"]))
    final = nodes_after
    if rec["deleted"]:
        final, _ = M.node_census(TARGET, "%s AFTER THE PURGE" % tag)
        fact("%s purge arithmetic: Node %d -> %d -> %d"
             % (tag, len(nodes_before), len(nodes_after), len(final)))
    rec["node_count_after_purge"] = len(final)
    R["purges"].append(rec)
    dump()
    return final, rec


# ======================================================================= [0] files only, zero LabVIEW
def phase_files():
    head("[0] FILES ONLY, ZERO LabVIEW - W1, the md5 pins BEFORE, then the MANDATORY pre-batch restart")
    # ---- W1, THE FIRST GATE IN THE RUN. It answers "can this fleet WRITE this row's sink at all?"
    # BEFORE ensure_loaded, before the copy, before any delete. Run 1's whole cost was this ordering
    # being absent: its delete ran and THEN the writer raised, leaving a dropped consumer on disk.
    K["writer_table"] = {}
    for row in ROWS:
        fn, op_vi, how = WRITERS.get(row["sink_kind"], (None, None, "no entry in WRITERS"))
        K["writer_table"][row["tag"]] = {"sink_kind": row["sink_kind"], "op_vi": op_vi,
                                         "sink_addressing": how, "bound": bool(fn and op_vi)}
        fact("[0] W1 row %s: sink kind %r, sink addressed by %s ; writer op %r ; BOUND %r",
             row["tag"], row["sink_kind"], how, (os.path.basename(op_vi) if op_vi else None),
             bool(fn and op_vi))
    unbound = [r["tag"] for r in ROWS
               if not all(WRITERS.get(r["sink_kind"], (None, None, ""))[:2])]
    gate("W1 EVERY ROW HAS A WRITER BOUND TO ITS SINK KIND - Row D's `tunnel_uid` sink is bound to the "
         "SWAPPED call (Pre-decided 116-A), so a row is NOT ATTEMPTED unless a writer on disk can reach "
         "its sink (no improvised address, no Local, no GUI fallback)",
         not unbound,
         "unbound row(s): %r ; the 6349C03 census stands (tools/bench/c78_rowd_writer.log: 4/4 label "
         "maps take an index-triple SINK, 0 take a uid) and is SIDE-STEPPED, not overturned, by handing "
         "the uid to the op's already-uid-addressed SOURCE half (Pre-decided 115)" % (unbound,))
    if unbound:
        raise Halt("no writer exists for the sink kind of row(s) %r. NOTHING WAS OPENED, NOTHING WAS "
                   "COPIED, NOTHING WAS DELETED - wire %d is untouched and the bed is byte-unchanged. "
                   "Row D's sink is a TERMINAL UID (#%d on FlatSequenceInnerTunnel #%d, Pre-decided "
                   "109/111). Building a writer for it is a NEW OP and a design decision - the "
                   "judgement session's, not this file's (CLAUDE.md section 3)."
                   % (unbound, ROWS[0]["wire"], TUNNEL_D_TERM, TUNNEL_D))
    for row in ROWS:
        op_vi = WRITERS[row["sink_kind"]][1]
        gate("W0 row %s: THE WRITER'S OWN OP VI IS ON DISK before any LabVIEW call (run 1 died on a gscript "
             "verb whose op VI does not exist: com_error 5507 File not found, AFTER the wire had been "
             "deleted)" % row["tag"], os.path.isfile(op_vi), op_vi)
        if not os.path.isfile(op_vi):
            raise Halt("the writer's op VI is not on disk: %s" % op_vi)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; STATUS records ~34,000 at the "
         "previous session's exit and the pre-batch restart below is MANDATORY - 44(e), Pre-decided "
         "100 SS7)" % R["handles"]["before"])
    pr = probe_hash("H INPUT THE BED (M3a-3 run 2's output, ROW C ALREADY IN IT) BEFORE", INPUT)
    gate("H1 the bed's md5 == its pin %s and its size == %d B" % (INPUT_MD5[:8], INPUT_BYTES),
         pr.get("md5") == INPUT_MD5 and str(pr.get("size")) == str(INPUT_BYTES),
         "%r / %r B" % (pr.get("md5"), pr.get("size")))
    R["input_md5_before"] = pr.get("md5")
    R["input_size_before"] = pr.get("size")
    for tag, path, pin in PINS:
        pr = probe_hash("H %s BEFORE" % tag, path)
        gate("H3 %s md5 == its pin %s" % (tag, pin[:8]), pr.get("md5") == pin, "%r" % (pr.get("md5"),))
    K["tool_pins_before"] = {}
    for p in TOOL_PINS:
        pr = probe_hash("H TOOL %s BEFORE" % os.path.basename(p), p)
        K["tool_pins_before"][p] = pr.get("md5")
    K["m3a1_refusals_at_entry"] = len(M.refusals)
    fact("[0] CITED, NOT RE-MEASURED (Pre-decided 108 / prior-art B4): the OLD loop #%d register table "
         "and both consumer nets stand at `tools/bench/diag_c73_m3a2_rows.log:43-44,:67-71,:82-87` and "
         "`tools/bench/diag_c75_m3a3_rows.log` / `diag_c75b_loopterms.log`. #4256 OUTER = 'position "
         "[internal units]' on wire 4859 ; #4334 OUTER = 'Outgoing Handle' on wire 7506. THIS IS THE "
         "TRANSPOSE OF STATUS NEXT's SENTENCE and it is the machine's reading (Pre-decided 104)."
         % OLD_LOOP)
    D.fresh("[0] pre-batch LabVIEW restart (44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])
    # W0b - THE PREFLIGHT THE RUN-1 REVIEW ASKED FOR, STRICTLY STRONGER THAN THE FILE CHECK
    # (`archive/peer/2026-09-22-c75-m3a3-run1-failpred.md`, Prediction 2 (c)): OPEN the writer's op VI with
    # the SAME call the row will make, at step [0], BEFORE the first mutation. It catches a missing file, a
    # broken op VI, a wrong path AND a label-map mismatch, where a disk scan catches only the first.
    # W0b now runs through `open_op()` (DEFECT FIX 2): a com_error inside GetVIReference is OUR code,
    # so it becomes this NAMED gate's failure with the RAW error text and an H9 record - never a FACT
    # line a later phase steps past.
    K["writer_preflight"] = {}
    for row in ROWS:
        op_vi = WRITERS[row["sink_kind"]][1]
        _op = open_op(op_vi, "W0b row %s: THE WRITER'S OP VI OPENS over COM before the first mutation "
                             "(the same call the row makes)" % row["tag"])
        K["writer_preflight"][row["tag"]] = {"op_vi": op_vi, "opened": _op is not None}
        if _op is None:
            raise Halt("the writer's op VI does not open: %s (see the W0b gate line for the raw error)"
                       % op_vi)
    dump()


# ============================================== [1] the arm's own copy and the pre-write FACT census
def arm_prepare(arm):
    """ONE ARM, ONE FILE. The bed is copied to this arm's own path and THE BED IS NEVER OPENED. For the
    two measurement arms that path is a dated SCRATCH deleted at the end of the arm; for the bed arm it
    is the stage artefact's own name."""
    name, dest = arm["name"], arm["target"]
    head("[%s/1] THE ARM TARGET IS A COPY OF THE BED - the bed is never opened, never edited, never run"
         % name)
    set_target(dest)
    for _ in range(4):
        if not os.path.exists(dest):
            break
        try:
            os.remove(dest)
        except OSError:
            time.sleep(1.0)
    shutil.copy2(INPUT, dest)
    time.sleep(0.4)
    pr = probe_hash("[%s/1] the arm target, straight after the copy" % name, dest)
    gate("[%s] X1 the arm target starts byte-identical to THE BED" % name, pr.get("md5") == INPUT_MD5,
         "%r vs %r" % (pr.get("md5"), INPUT_MD5))
    fact("[%s/1] the arm target is %s (%s) - every edit in this arm is made on THIS file"
         % (name, os.path.basename(dest), "SCRATCH" if arm["scratch"] else "THE STAGE ARTEFACT"))
    t0 = time.time()
    _, err = safe("[%s/1] ensure_loaded(arm target)" % name, lambda: g.ensure_loaded(dest))
    fact("[%s/1] ensure_loaded took %.1f s%s (edits are SILENTLY DECLINED on a target that is not fully "
         "loaded - gscript.py:764)" % (name, time.time() - t0, (" ERROR " + err) if err else ""))
    read_es("[%s/1] the arm target, COLD" % name)
    counts("[%s/1] COLD" % name)
    di, derr = safe("[%s/1] diag_index(#%d)" % (name, D686), lambda: diag_index(dest, D686))
    K.setdefault("d686_index", {})[name] = di
    fact("[%s/1] Diagram #%d -> traverse index %r%s (expected 19 - diag_c75b_loopterms.log)"
         % (name, D686, di, (" ; " + derr) if derr else ""))
    dump()
    if di is None:
        return None
    return [di, TOP]


def arm_cleanup(arm):
    """A SCRATCH IS CREATED AND DELETED IN THE SAME RUN. The bed arm's file is deleted ONLY when it was
    not saved - a byte-identical copy of the bed under a stage name is a DECOY bed, not an artefact."""
    name, dest = arm["name"], arm["target"]
    safe("[%s] close_panel" % name, lambda: g.close_panel(dest))
    for _ in range(6):
        try:
            if os.path.exists(dest):
                os.remove(dest)
            break
        except OSError:
            time.sleep(1.0)
    gate("[%s] X9 the arm's working file was deleted (%s)" % (name, os.path.basename(dest)),
         not os.path.exists(dest), dest)


# ================================================= [C0] ROW C's PRECONDITION - asserted, never rebuilt
def phase_precondition_rowc(hints):
    """ROW C IS ALREADY IN THE BED (run 2). It is ASSERTED here, read-only, and NEVER REBUILT.

    The test is Pre-decided 85/106 exactly as Row C was accepted under: the net carried by
    `Global #7202 'Global motor pos.vi'` t0 'Focus position' has EXACTLY ONE source terminal of ANY
    owner class (counted before any class filter - Pre-decided 77) and that terminal is
    `RightShiftRegister #23895`. PD85 violations 0 or the walk is not believed at all.

    If this fails, the bed is not the artefact this stage was told it is, and NOTHING is deleted: a
    stage never repairs its own input (rule 1 in spirit, and the reason run 1's artefact is rejected
    rather than patched)."""
    head("[C0] ROW C's PRECONDITION - Global #%d t0 %r must already read #%d (run 2), ASSERTED NOT REBUILT"
         % (ROWC["sink_uid"], ROWC["sink_name"], ROWC["expect_source_uid"]))
    rec = {"row": ROWC["tag"], "evidence_for_the_claim": ROWC["evidence"], "target": TARGET}
    R.setdefault("precondition_rowc", []).append(rec)
    node, rows = node_table(ROWC["sink_uid"], hints, "[C0] Global #%d" % ROWC["sink_uid"])
    rec["node"] = node
    rec["terminals"] = [(t["i"], t["name"], t["is_source"], t["wire"], M.term_state(t)) for t in rows]
    fact("[C0] Global #%d terminal table: %r", ROWC["sink_uid"], rec["terminals"])
    cands = [t for t in rows if t.get("name") == ROWC["sink_name"] and t.get("is_source") is False]
    if len(cands) != 1:
        rec["verdict"] = ("the precondition sink is not uniquely addressable: %d row(s) named %r"
                          % (len(cands), ROWC["sink_name"]))
        gate("C0 ROW C's PRECONDITION (asserted, never rebuilt): Global #%d t0 %r reads the NEW register "
             "#%d" % (ROWC["sink_uid"], ROWC["sink_name"], ROWC["expect_source_uid"]), False,
             rec["verdict"])
        return rec
    wire_now = cands[0].get("wire") or 0
    rec["sink_wire"] = wire_now
    walk, err = wire_walk("[C0] the Row-C sink net %r" % wire_now, wire_now)
    all_src = [t for t in walk if t.get("is_source") and t.get("owner_uid")]
    the_one = all_src[0] if len(all_src) == 1 else None
    bad = pd85(wire_now, walk)
    rec["walk_error"] = err
    rec["ALL_source_terminals"] = [(t.get("owner_class"), t.get("owner_uid")) for t in all_src]
    rec["observed_one_owner"] = (None if the_one is None else
                                 (the_one.get("owner_class"), the_one.get("owner_uid")))
    rec["pd85_violations"] = len(bad)
    ok = (bool(wire_now) and len(all_src) == 1 and not bad
          and the_one.get("owner_uid") == ROWC["expect_source_uid"]
          and str(the_one.get("owner_class")) == ROWC["expect_source_class"])
    rec["verdict"] = "HOLDS" if ok else "FAILED"
    fact("[C0] the Row-C sink net %r has %d source terminal(s) of ANY class %r ; observed the-one %r "
         "(want %r #%d) ; PD85 violations %d", wire_now, len(all_src), rec["ALL_source_terminals"],
         rec["observed_one_owner"], ROWC["expect_source_class"], ROWC["expect_source_uid"], len(bad))
    gate("C0 ROW C's PRECONDITION (asserted, never rebuilt - Pre-decided 85/106/108): the net at Global "
         "#%d t0 %r has exactly ONE source terminal of ANY class and it is %s #%d"
         % (ROWC["sink_uid"], ROWC["sink_name"], ROWC["expect_source_class"], ROWC["expect_source_uid"]),
         ok, "net %r ; sources %r ; PD85 %d%s"
             % (wire_now, rec["ALL_source_terminals"], len(bad), (" ; walk error " + err) if err else ""))
    dump()
    return rec


# ================================================= [P0] ROW D's SINK - the prediction, then the read
def phase0_resolve_tunnel(hints):
    """PRE-DECIDED 109/111, WHICH AMEND 107's ROUTE AND LEAVE ITS PROHIBITION UNTOUCHED.

    107 prescribed reading the owning `FlatSequence #681` NODE's terminal table on `Diagram #686`.
    THAT TABLE DOES NOT EXIST: `#686` has 27 `Nodes[]` rows and `#681` is in none of them,
    `owner_of(#681)` is `TopLevelDiagram #536`, and `find_node` misses all three FlatSequences
    (#43914 / #12938 / #681) across 173 of 173 diagrams - the miss tracks the CLASS, because a
    `FlatSequence` is a direct child of `GObject` and never a `Node` (`diag_c77_rowd_addr.log`;
    Pre-decided 110). So 107's "absent or duplicated => defer" branch is VOID - its premise was a table
    that was never the right table - and it does not fire here.

    WHAT REPLACES IT: the tunnel's OWN terminal table, read BY UID with ZERO HOPS by the op we already
    have, `OpFsInnerTunnelTerm_v0` (38/38, `build_opfstunnelterm_v2_run1.log:160-161`). Still NO owner
    walk (an owner chain terminates SILENTLY at a `FlatSequenceFrame`, error 1055,
    `docs/toolkit-capabilities.md:61` - exactly `#7468`'s path), NO `Nodes[]` lookup of a FlatSequence,
    NO improvised address, NO GUI fallback.

    THE PREDICTION, STATED BEFORE THE READ: the op returns `LeftTerm` = terminal uid #7488 with its
    error column EMPTY, and that face carries wire 7506. Anything else - an error column, a missing uid,
    a different wire - is a FAILED PREDICTION: the run STOPS, wire 7506 is NOT deleted, and no address
    is improvised."""
    head("[P0] ROW D's SINK - FlatSequenceInnerTunnel #%d's OWN terminal table, read BY UID with zero "
         "hops (Pre-decided 109/111). `#%d` is NEVER looked up in any Nodes[] (Pre-decided 110)."
         % (TUNNEL_D, FLATSEQ))
    rec = {"prediction": "OpFsInnerTunnelTerm_v0 on uid %d returns LeftTerm = terminal uid #%d with an "
                         "EMPTY error column, and that face carries wire 7506 - which IS Row D's sink "
                         "address (Pre-decided 109/111)" % (TUNNEL_D, TUNNEL_D_TERM),
           "no_owner_walk": "an owner chain terminates SILENTLY at a FlatSequenceFrame (error 1055, "
                            "docs/toolkit-capabilities.md:61) - #7468's exact path, so the owner walk "
                            "is NOT used (Pre-decided 107's prohibition, untouched by 109)",
           "no_nodes_lookup": "a FlatSequence is a GObject, never a Node, so #%d is NEVER looked up in "
                              "any Nodes[] (Pre-decided 110; measured diag_c77_rowd_addr.log, 173/173 "
                              "diagrams, 635 nodes, 0 scan errors, found None for #43914/#12938/#681)"
                              % FLATSEQ,
           "wire": ROWS[0]["wire"], "expect_term_uid": TUNNEL_D_TERM}
    R["phase0"] = rec
    fact("[P0] PREDICTION (written before the read): %s", rec["prediction"])
    fact("[P0] %s", rec["no_nodes_lookup"])
    labels_path = os.path.join(BENCH, "opfsinnertunnelterm_labels.json")
    op_in = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelTerm_v0.vi")
    rec["op_vi"], rec["labels"] = op_in, labels_path
    gate("P0a the reader's label map is on disk", os.path.isfile(labels_path), labels_path)
    vi = open_op(op_in, "P0b OpFsInnerTunnelTerm_v0 OPENS over COM (a com_error in GetVIReference is OUR "
                        "code, never a machine refusal - Pre-decided 100 SS2)")
    if vi is None or not os.path.isfile(labels_path):
        rec["verdict"] = "FAILED PREDICTION - the reader could not be opened; see the P0a/P0b gate lines"
        fact("[P0] %s. Wire %d is NOT deleted and no address is improvised.", rec["verdict"], rec["wire"])
        dump()
        return rec
    labs = json.load(open(labels_path, encoding="utf-8"))
    rd, rderr = safe("[P0] read_tunnel(#%d)" % TUNNEL_D, lambda: READ_FSIT(vi, labs, TARGET, TUNNEL_D))
    rec["read"] = rd
    rec["read_error"] = rderr
    if not rd:
        rec["verdict"] = "FAILED PREDICTION - the reader returned nothing (%s)" % (rderr or "no rows")
        fact("[P0] *** %s *** Wire %d is NOT deleted and no address is improvised.",
             rec["verdict"], rec["wire"])
        dump()
        return rec
    fact("[P0] RAW RETURN for #%d: %s", TUNNEL_D, json.dumps(rd, default=str)[:700])
    fact("[P0] #%d self class echo %r uid echo %r ; cast %r", TUNNEL_D, rd.get("cls_back"),
         rd.get("uid_back"), rd.get("cast_class"))
    fact("[P0] #%d %s terminal #%r wire #%r ; %s terminal #%r wire #%r ; owner %r#%r",
         TUNNEL_D, labs.get("face_a"), rd.get("term_a_uid"), rd.get("wire_a"), labs.get("face_b"),
         rd.get("term_b_uid"), rd.get("wire_b"), rd.get("ownercls"), rd.get("owner_uid"))
    fact("[P0] #%d ERROR COLUMNS VERBATIM: err=%r err_a=%r err_b=%r errs=%r", TUNNEL_D, rd.get("err"),
         rd.get("err_a"), rd.get("err_b"), rd.get("errs"))
    # The uid ECHO first (the A7 pattern): a reader that does not echo the uid it was asked about is
    # reporting some OTHER object, and its answer is not evidence about ours (the history-echo defect
    # repaired in `wire_source_owner`, acceptance diag_c68_echo_accept.log 8/0).
    echo_ok = (str(rd.get("uid_back")) == str(TUNNEL_D)
               and str(rd.get("cast_class")) in ("FlatSequenceInnerTunnel",))
    gate("P0c THE READER ECHOES THE UID IT WAS ASKED ABOUT and casts to FlatSequenceInnerTunnel "
         "(an un-echoed answer is about some other object)", echo_ok,
         "uid echo %r ; cast %r" % (rd.get("uid_back"), rd.get("cast_class")))
    faces = [("face_a", labs.get("face_a"), rd.get("term_a_uid"), rd.get("wire_a"), rd.get("err_a")),
             ("face_b", labs.get("face_b"), rd.get("term_b_uid"), rd.get("wire_b"), rd.get("err_b"))]
    rec["faces"] = [{"key": k, "name": n, "term_uid": tu, "wire": w, "error_verbatim": e}
                    for k, n, tu, w, e in faces]
    carrying = [f for f in faces if str(f[3]) == str(rec["wire"])]
    rec["faces_carrying_the_wire"] = [(f[1], f[2]) for f in carrying]
    fact("[P0] which face of #%d carries wire %d: %r  (want EXACTLY ONE, and its terminal uid #%d)",
         TUNNEL_D, rec["wire"], rec["faces_carrying_the_wire"], TUNNEL_D_TERM)
    if len(carrying) != 1 or carrying[0][4] or not carrying[0][2]:
        rec["verdict"] = ("FAILED PREDICTION - %d face(s) of #%d carry wire %d (want exactly 1), "
                          "terminal uid %r, error column %r"
                          % (len(carrying), TUNNEL_D, rec["wire"],
                             carrying[0][2] if carrying else None,
                             carrying[0][4] if carrying else None))
        fact("[P0] *** %s *** Wire %d is NOT deleted, no address is improvised for #%d, and there is no "
             "GUI fallback.", rec["verdict"], rec["wire"], TUNNEL_D)
        dump()
        return rec
    face = carrying[0]
    rec["sink_term_uid"] = int(face[2])
    rec["sink_face"] = face[1]
    rec["matches_pre_decided_111"] = (rec["sink_term_uid"] == TUNNEL_D_TERM)
    gate("P0 ROW D's SINK RESOLVED BY UID - #%d's %s is terminal #%r and it carries wire %d, every error "
         "column empty (Pre-decided 109/111; NO Nodes[], NO owner walk)"
         % (TUNNEL_D, face[1], face[2], rec["wire"]),
         echo_ok and rec["matches_pre_decided_111"],
         "terminal #%r vs Pre-decided 111's #%d ; match %r"
         % (face[2], TUNNEL_D_TERM, rec["matches_pre_decided_111"]))
    rec["verdict"] = "HOLDS" if (echo_ok and rec["matches_pre_decided_111"]) else "FAILED PREDICTION"
    dump()
    return rec


# ================================================================== [2] the live source / sink readers
def resolve_source(row, hints, tag, expect_bare=True):
    """THE SOURCE IS THE NEW RIGHT REGISTER's OUTER TERMINAL, addressed on the loop BORDER node
    `#23032` - resolved LIVE by name among the border's SOURCE rows (there is no `Terminals[]` index for
    a shift register itself: `diag_c75_m3a3_rows.log` reads its OUTER through the `Outside Terminal`
    property, which is not an address a (diagram, node, terminal) verb can take). The index found is
    logged beside the expectation; the expectation is NEVER a criterion (Pre-decided 99 A4)."""
    rec = {"new_reg": row["new_reg"], "name": row["src_name"], "expected_term": row["src_expect_term"]}
    node, rows = node_table(LOOP_A, hints, "%s SOURCE border #%d" % (tag, LOOP_A))
    rec["border"] = node
    rec["border_terminals"] = [(t["i"], t["name"], t["is_source"], t["wire"], M.term_state(t))
                               for t in rows]
    fact("%s SOURCE the loop border #%d terminal table: %r" % (tag, LOOP_A, rec["border_terminals"]))
    named = [t for t in rows if t.get("name") == row["src_name"] and t.get("is_source") is True]
    if expect_bare:
        cands = [t for t in named if M.term_state(t) == "BARE"]
    else:
        cands = named
    rec["candidates"] = [(t["i"], t["name"], t["is_source"], t["wire"], M.term_state(t)) for t in cands]
    if len(cands) != 1:
        rec["stop"] = ("the NEW register #%d's OUTER terminal is not UNIQUELY addressable on the border "
                       "node: %d candidate(s) named %r with is_source True%s among %d terminal(s). No "
                       "index is guessed and nothing is wired (Pre-decided 68)."
                       % (row["new_reg"], len(cands), row["src_name"],
                          " and BARE" if expect_bare else "", len(rows)))
        fact("%s SOURCE UNRESOLVED: %s" % (tag, rec["stop"]))
        return rec
    hit = cands[0]
    rec["src_diag_index"] = node["diagram_index"]
    rec["src_nodes_index"] = node["nodes_index"]
    rec["src_term_index"] = hit["i"]
    rec["matches_expectation"] = (hit["i"] == row["src_expect_term"])
    fact("%s SOURCE RESOLVED LIVE: (Diagram idx %r, Nodes[%r] = loop #%d, Terminals[%r]) name %r "
         "is_source %r state %s ; the EXPECTATION from diag_c75b_loopterms.log is t%r, match %r - an "
         "OUTPUT, never a criterion, and never carried from a census"
         % (tag, rec["src_diag_index"], rec["src_nodes_index"], LOOP_A, rec["src_term_index"],
            hit.get("name"), hit.get("is_source"), M.term_state(hit), row["src_expect_term"],
            rec["matches_expectation"]))
    return rec


def resolve_sink(row, hints, tag, phase0):
    """THE SINK. For a Nodes[] consumer (`Global #7202`) it is resolved live by uid and then by terminal
    NAME; for the tunnel (`#7468`) it is PHASE 0's triple, re-read here to confirm it still stands."""
    rec = {"kind": row["sink_kind"], "uid": row["sink_uid"]}
    if row["sink_kind"] == "tunnel_uid":
        # PRE-DECIDED 109/111: the sink is a TERMINAL UID, re-read from the tunnel's OWN table by uid
        # with zero hops. No `Nodes[]` lookup of the owning FlatSequence (110), no owner walk (107).
        if phase0.get("verdict") != "HOLDS":
            rec["stop"] = "PHASE 0 did not resolve #%d: %s" % (row["sink_uid"], phase0.get("verdict"))
            return rec
        vi = open_op(phase0.get("op_vi"), "%s SINK re-read: OpFsInnerTunnelTerm_v0 opens" % tag)
        if vi is None:
            rec["stop"] = "the sink reader did not open - see the gate line for the raw error"
            return rec
        labs = json.load(open(phase0["labels"], encoding="utf-8"))
        rd, err = safe("%s read_tunnel(#%d)" % (tag, row["sink_uid"]),
                       lambda: READ_FSIT(vi, labs, TARGET, row["sink_uid"]))
        rec["read"] = rd
        if not rd or str(rd.get("uid_back")) != str(row["sink_uid"]):
            rec["stop"] = ("the sink reader did not echo uid #%d (%r)%s"
                           % (row["sink_uid"], (rd or {}).get("uid_back"), (" ; " + err) if err else ""))
            return rec
        pairs = {str(rd.get("term_a_uid")): rd.get("wire_a"), str(rd.get("term_b_uid")): rd.get("wire_b")}
        if str(row["sink_term_uid"]) not in pairs:
            rec["stop"] = ("PHASE 0's terminal uid #%d is no longer a face of #%d: faces %r"
                           % (row["sink_term_uid"], row["sink_uid"], sorted(pairs)))
            return rec
        rec["sink_term_uid"] = row["sink_term_uid"]
        rec["sink_wire_before"] = int(pairs[str(row["sink_term_uid"])] or 0)
        fact("%s SINK (tunnel_uid) RE-CONFIRMED BY UID: terminal #%d of FlatSequenceInnerTunnel #%d "
             "carries wire %r ; the other face %r", tag, row["sink_term_uid"], row["sink_uid"],
             rec["sink_wire_before"], {k: v for k, v in pairs.items()
                                       if k != str(row["sink_term_uid"])})
        return rec
    node, rows = node_table(row["sink_uid"], hints, "%s SINK #%d" % (tag, row["sink_uid"]))
    rec["node"] = node
    rec["terminals"] = [(t["i"], t["name"], t["is_source"], t["wire"], M.term_state(t)) for t in rows]
    fact("%s SINK #%d terminal table: %r" % (tag, row["sink_uid"], rec["terminals"]))
    cands = [t for t in rows if t.get("name") == row["sink_name"] and t.get("is_source") is False]
    rec["candidates"] = [(t["i"], t["name"], t["is_source"], t["wire"], M.term_state(t)) for t in cands]
    if len(cands) != 1:
        rec["stop"] = ("the sink terminal is not UNIQUELY addressable: %d row(s) named %r with "
                       "is_source False among %d terminal(s). Nothing is wired."
                       % (len(cands), row["sink_name"], len(rows)))
        fact("%s SINK UNRESOLVED: %s" % (tag, rec["stop"]))
        return rec
    hit = cands[0]
    rec["sink_diag_index"] = node["diagram_index"]
    rec["sink_nodes_index"] = node["nodes_index"]
    rec["sink_term_index"] = hit["i"]
    rec["sink_wire_before"] = hit.get("wire") or 0
    rec["matches_expectation"] = (node.get("nodes_index") == row["sink_expect_node"]
                                  and hit["i"] == row["sink_expect_term"])
    fact("%s SINK RESOLVED LIVE: (Diagram idx %r, Nodes[%r], Terminals[%r]) name %r is_source %r "
         "carrying wire %r ; expectation Nodes[%r].T[%r], match %r"
         % (tag, rec["sink_diag_index"], rec["sink_nodes_index"], rec["sink_term_index"],
            hit.get("name"), hit.get("is_source"), rec["sink_wire_before"], row["sink_expect_node"],
            row["sink_expect_term"], rec["matches_expectation"]))
    return rec


def sink_wire_now(row, sink, hints, tag, when, phase0):
    """RE-READ the sink terminal on the LIVE target and return the wire it carries NOW. An index is never
    carried across a mutation: the terminal is found again by NAME (Nodes[] consumer) or by PHASE 0's
    index (tunnel), and what is found is reported either way."""
    rec = {"when": when, "stored_index": sink.get("sink_term_index")}
    if row["sink_kind"] == "tunnel_uid":
        # BY UID, zero hops - never by an index carried across a mutation, and never through Nodes[].
        rec["how"] = "BY THE TERMINAL UID #%d on FlatSequenceInnerTunnel #%d (Pre-decided 109/111)" % (
            row["sink_term_uid"], row["sink_uid"])
        vi = open_op(sink.get("op_vi") or R["phase0"].get("op_vi"),
                     "%s sink re-read %s: OpFsInnerTunnelTerm_v0 opens" % (tag, when))
        rd = None
        if vi is not None:
            labs = json.load(open(R["phase0"]["labels"], encoding="utf-8"))
            rd, _e = safe("%s read_tunnel(#%d) %s" % (tag, row["sink_uid"], when),
                          lambda: READ_FSIT(vi, labs, TARGET, row["sink_uid"]))
        pairs = ({} if not rd else
                 {str(rd.get("term_a_uid")): rd.get("wire_a"), str(rd.get("term_b_uid")): rd.get("wire_b")})
        rec["term_index"] = row["sink_term_uid"]
        rec["name"] = R["phase0"].get("sink_face")
        rec["wire"] = int(pairs.get(str(row["sink_term_uid"])) or 0)
        rec["state"] = "BARE" if not rec["wire"] else "WIRED"
        rec["index_moved"] = False
        rec["uid_echo"] = (rd or {}).get("uid_back")
        fact("%s the sink terminal %s (%s): terminal #%r carries wire %r, state %r, uid echo %r",
             tag, when, rec["how"], rec["term_index"], rec["wire"], rec["state"], rec["uid_echo"])
        return rec
    uid = row["sink_uid"]
    node, rows = node_table(uid, hints, "%s sink %s" % (tag, when), quiet=True)
    rec["nodes_index"] = node.get("nodes_index")
    rec["diagram_index"] = node.get("diagram_index")
    named = [t for t in rows if t.get("name") == row["sink_name"] and t.get("is_source") is False]
    if len(named) == 1:
        hit, rec["how"] = named[0], "BY NAME (unique among the node's sink rows)"
    else:
        hit = next((t for t in rows if t.get("i") == rec["stored_index"]), None)
        rec["how"] = ("BY THE STORED INDEX - the by-name reading was not unique (%d row(s) named %r)"
                      % (len(named), row["sink_name"]))
    rec["term_index"] = (hit or {}).get("i")
    rec["name"] = (hit or {}).get("name")
    rec["wire"] = (hit or {}).get("wire") or 0
    rec["state"] = M.term_state(hit) if hit else None
    rec["index_moved"] = (rec["term_index"] != rec["stored_index"])
    fact("%s the sink terminal %s (%s): Nodes[%r].Terminals[%r] (stored %r ; moved %r), name %r, carries "
         "wire %r, state %r" % (tag, when, rec["how"], rec["nodes_index"], rec["term_index"],
                                rec["stored_index"], rec["index_moved"], rec["name"], rec["wire"],
                                rec["state"]))
    return rec


# ==================================================== THE SWAPPED CALL (Pre-decided 116-A) - two halves
def wire_term_index(tag, wire_uid, want_owner, when):
    """THE SOURCE HALF OF THE SWAPPED CALL, step 1 of the c79 review's own test.

    `OpWireSource_v5` walks `Wire.Terms[]` BY INDEX (`docs/toolkit-capabilities.md:60` - it increments
    `term index` until error 1055 and keeps the rows), and `OpConnectFromWire_v0` reads the SAME property
    6371003 with the SAME index (`opconnectfromwire_v0_labels.json`: `wire_terms_prop` 6371003,
    `wire_term_index` = 'index 7'). So the index the reader reports for the NON-source row IS the index
    the writer needs. READ-ONLY; nothing is guessed - if the non-source row is not unique the caller
    STOPS."""
    walk, err = wire_walk("%s the SOURCE HALF %s - Wire.Terms[] of w%r" % (tag, when, wire_uid), wire_uid)
    rec = {"when": when, "wire": wire_uid, "want_owner": want_owner, "walk_error": err,
           "rows": [(t.get("i"), t.get("is_source"), t.get("owner_class"), t.get("owner_uid"),
                     t.get("recip")) for t in walk],
           "pd85_violations": len(pd85(wire_uid, walk))}
    sinks = [t for t in walk if t.get("owner_uid") and t.get("is_source") is False]
    owned = [t for t in sinks if t.get("owner_uid") == want_owner]
    rec["non_source_rows"] = [(t.get("i"), t.get("owner_class"), t.get("owner_uid")) for t in sinks]
    rec["rows_owned_by_the_target"] = [(t.get("i"), t.get("owner_class"), t.get("owner_uid"))
                                       for t in owned]
    if len(owned) == 1:
        hit, rec["chosen_by"] = owned[0], "the ONE non-source row whose owner IS #%d" % want_owner
    elif len(sinks) == 1:
        hit, rec["chosen_by"] = sinks[0], ("the ONE non-source row on the wire (its owner is NOT #%d - "
                                           "REPORTED, not corrected)" % want_owner)
    else:
        hit, rec["chosen_by"] = None, ("UNRESOLVED: %d non-source row(s), %d owned by #%d - no index is "
                                       "guessed" % (len(sinks), len(owned), want_owner))
    rec["index"] = None if hit is None else hit.get("i")
    rec["chosen_owner"] = (None if hit is None
                           else (hit.get("owner_class"), hit.get("owner_uid")))
    fact("%s the SOURCE HALF %s: Wire.Terms[] index %r chosen %s ; owner %r ; all non-source rows %r ; "
         "PD85 violations %d", tag, when, rec["index"], rec["chosen_by"], rec["chosen_owner"],
         rec["non_source_rows"], rec["pd85_violations"])
    return rec


def swapped_connect(tag, when, wire_uid, term_index, inv):
    """THE SWAPPED CALL ITSELF (Pre-decided 116-A). `connect_from_wire`'s uid-addressed half is handed the
    FSIT TERMINAL - the true SINK - and its (diagram, `Nodes[]`, `Terminals[]`) triple is handed the NEW
    loop's BARE border terminal - the true SOURCE - so the Invoke sits on the BARE terminal and receives
    the FSIT terminal as `Wire Source`. EVERY return is recorded VERBATIM, including a refusal: a dead
    wire uid failing is a legitimate outcome of the measurement, never something to work around."""
    rec = {"when": when, "wire_uid": wire_uid, "wire_term_index": term_index,
           "invoke_triple_diag_node_term": (inv.get("src_diag_index"), inv.get("src_nodes_index"),
                                            inv.get("src_term_index")),
           "roles": "wire_uid+term_index -> `Wire Source` (the FSIT terminal, the TRUE SINK) ; the index "
                    "triple -> the Invoke's own terminal (the NEW loop border, the TRUE SOURCE)"}
    t0 = time.time()
    try:
        dw, es, err, sub = CONNECT_FROM_WIRE(TARGET, int(wire_uid), int(term_index),
                                             inv["src_diag_index"], inv["src_nodes_index"],
                                             inv["src_term_index"], CFW_LABELS)
        rec["wire_delta"] = dw
        rec["exec_state"] = es
        rec["op_error_verbatim"] = str(err or "")[:300]
        rec["sub_returns_verbatim"] = dict((k, repr(v)[:200]) for k, v in (sub or {}).items())
        rec["err_uidvi_verbatim"] = str((sub or {}).get("err_uidvi") or "")[:300]
        rec["err_wirepn_verbatim"] = str((sub or {}).get("err_wirepn") or "")[:300]
        rec["is_broken_readback"] = (sub or {}).get("Is Broken?")
        rec["uid2_readback"] = (sub or {}).get("UID 2")
        if rec["op_error_verbatim"]:
            refusal("%s swapped connect_from_wire %s" % (tag, when), rec["op_error_verbatim"])
    except Exception as e:                                                         # noqa: BLE001
        rec["call_error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        defect("%s swapped connect_from_wire %s (wire_uid=%r, term_index=%r, invoke triple %r)"
               % (tag, when, wire_uid, term_index, rec["invoke_triple_diag_node_term"]), e)
    rec["cost_s"] = round(time.time() - t0, 2)
    rec["reported_success"] = bool(not rec.get("call_error") and not rec.get("op_error_verbatim")
                                   and not rec.get("err_uidvi_verbatim")
                                   and not rec.get("err_wirepn_verbatim"))
    fact("%s THE SWAPPED CALL %s -> VERBATIM %s", tag, when, json.dumps(rec, default=str)[:1200])
    return rec


# NOTE, RECORDED SO IT IS NOT RE-TRIED: the c79 review's "step 4" probe - hand the op the TERMINAL uid
# #7488 with the index triple out of range and read `err_uidvi` alone - WAS RUN ONCE
# (`tools/bench/c80_rowd_routeA.log:289-290`) and is UNSOUND. `err_uidvi` came back EMPTY for a DELETED
# wire uid as well (arm A1, `:119`), so empty does not mean "resolved"; and the c80-r2 review showed the
# probe is uninformative BY CONSTRUCTION, since the deliberately out-of-range triple guarantees the only
# downstream indicator fails whatever the uid resolved to. The sound reader is `OpOwnerChain_v1` with
# `uid_in = 7488`, read on its SELF echo (`Class Name 3` / the self uid) - which needs a labels map that
# is not on disk and a `read_owner()` whose target is hard-coded to the MAIN VI. Not done here.


# ========================================================================= [3] the acceptance test
def acceptance(row, tag, when, sink_wire, mandatory):
    """PRE-DECIDED 85 + 106, THE WHOLE TEST, READ OFF THE MACHINE AND NOTHING ELSE.
      (1) the wire carried by the SINK terminal has EXACTLY ONE source terminal OF ANY OWNER CLASS
          (Pre-decided 77 - counted BEFORE any class filter; the recorded pathology is broken wire w1231,
          whose two is_source terminals are of DIFFERENT classes);
      (2) that one terminal's owner is the NEW RIGHT register (#23895 / #23868) - `LANDED` IS SOURCE
          IDENTITY, never "the sink is still wired" and never a wired-count delta (Pre-decided 106);
      (3) the walk has ZERO Pre-decided 85 violations, or it is not believed at all.
    FACT-ONLY, never part of the verdict: whether the OLD register (#4256 / #4334) is still on the net,
    and the hop count (Pre-decided 90)."""
    walk, err = wire_walk("%s ACCEPTANCE %s - the SINK net %r" % (tag, when, sink_wire), sink_wire)
    all_src = [t for t in walk if t.get("is_source") and t.get("owner_uid")]
    classes = [(t.get("owner_class"), t.get("owner_uid")) for t in all_src]
    the_one = all_src[0] if len(all_src) == 1 else None
    owners = [int(t["owner_uid"]) for t in walk if t.get("owner_uid")]
    bad = pd85(sink_wire, walk)
    rec = {"tag": tag, "when": when, "sink_wire": sink_wire, "walk_error": err,
           "ALL_source_terminals": classes, "ALL_source_terminal_count": len(all_src),
           "the_one_is_the_NEW_register": bool(the_one is not None
                                               and the_one.get("owner_uid") == row["new_reg"]),
           "observed_one_owner": (None if the_one is None else
                                  (the_one.get("owner_class"), the_one.get("owner_uid"))),
           "OLD_register_still_on_the_net": row["old_source"] in owners,
           "OLD_loop_still_on_the_net": OLD_LOOP in owners,
           "new_loop_border_on_the_net_FACT_ONLY": LOOP_A in owners,
           "every_owner_on_the_net": sorted(set(owners)), "pd85_violations": len(bad),
           "counted_before_filtering": "Pre-decided 77 - every owner class is counted before any filter"}
    # PRE-DECIDED 111 adds the OLD side to the ASSERTION, not to the commentary: "the OLD #637 t10 must
    # be OFF the net". With exactly one source terminal it cannot still DRIVE the net, but it could still
    # sit on it as a sink (a branch), which would be just as wrong - so neither the old register #4334
    # nor the old loop #637 may appear among the net's owners at all.
    ok = (bool(sink_wire) and len(all_src) == 1 and rec["the_one_is_the_NEW_register"] and not bad
          and not rec["OLD_register_still_on_the_net"] and not rec["OLD_loop_still_on_the_net"])
    rec["pass"] = ok
    fact("%s ACCEPTANCE %s: sink net %r has %d source terminal(s) of ANY class %r (want exactly 1, owned "
         "by the NEW register #%d) ; observed the-one %r ; OLD register #%d still on the net %r ; OLD "
         "loop #%d still on the net %r ; the new loop border #%d on the net (FACT ONLY) %r ; every owner "
         "%r ; PD85 violations %d",
         tag, when, sink_wire, len(all_src), classes, row["new_reg"], rec["observed_one_owner"],
         row["old_source"], rec["OLD_register_still_on_the_net"], OLD_LOOP,
         rec["OLD_loop_still_on_the_net"], LOOP_A,
         rec["new_loop_border_on_the_net_FACT_ONLY"], rec["every_owner_on_the_net"], len(bad))
    if mandatory:
        gate("%s ROW ACCEPTANCE %s (Pre-decided 85/106/111): ONE source of ANY class, owned by the NEW "
             "register #%d, and the OLD #%d/#%d OFF the net" % (tag, when, row["new_reg"],
                                                                row["old_source"], OLD_LOOP), ok,
             "sink wire %r ; sources %r ; PD85 %d ; old-on-net %r/%r"
             % (sink_wire, classes, len(bad), rec["OLD_register_still_on_the_net"],
                rec["OLD_loop_still_on_the_net"]))
    K.setdefault("acceptance", []).append(rec)
    return rec


# ================================================================================ [4] ONE ROW
def one_row(row, hints, phase0, arm):
    ordering = arm["ordering"]
    tag = "[%s ROW %s]" % (arm["name"], row["tag"])
    head("%s %s: wire %d , NEW register #%d OUTER -> FlatSequenceInnerTunnel #%d terminal #%d"
         % (tag, ordering, row["wire"], row["new_reg"], row["sink_uid"], row["sink_term_uid"]))
    fact("%s WHY: %s" % (tag, row["why"]))
    rec = {"row": row, "arm": arm["name"], "ordering": ordering,
           "writer": "build_opconnectfromwire_v0.connect_from_wire (OpConnectFromWire_v0.vi, VERIFIED "
                     "ON DISK by gate W0 and OPENED by W0b before the first mutation) WITH THE ROLES "
                     "SWAPPED - Pre-decided 116-A",
           "shape": "THE SWAPPED CALL: the uid-addressed half takes the FSIT TERMINAL (the true SINK) "
                    "and the index triple takes the NEW loop's BARE border terminal (the true SOURCE), "
                    "so the Invoke sits on the BARE terminal (gscript.py:2522-2523 is why the ordering "
                    "of delete vs connect is the thing being measured)",
           "never_a_local": "a Local is NEVER substituted for this row (rule 1a)"}
    R["rows"]["%s/%s" % (arm["name"], row["tag"])] = rec

    # ---- (i) the state BEFORE anything is touched: the net that is about to be cut.
    before_walk, _ = wire_walk("%s BEFORE - the net about to be CUT (wire %d)" % (tag, row["wire"]),
                               row["wire"])
    rec["net_before"] = [(t.get("i"), t.get("is_source"), t.get("owner_class"), t.get("owner_uid"))
                         for t in before_walk]
    sink = resolve_sink(row, hints, tag, phase0)
    rec["sink"] = sink
    src = resolve_source(row, hints, tag, expect_bare=True)
    rec["source"] = src
    stop = sink.get("stop") or src.get("stop")
    if stop:
        rec["result"] = "ROW STOPPED BEFORE THE DELETE: %s" % stop
        fact("%s *** %s Nothing was deleted, nothing was wired, nothing was substituted "
             "(Pre-decided 68). ***" % (tag, rec["result"]))
        gate("%s ROW WRITTEN AT ALL" % tag, False, stop)
        dump()
        return rec

    # ---- (ii) THE SOURCE HALF, read BEFORE any mutation (read-only; in ARM A1 the delete destroys the
    #      wire this index is read from, so it can only be read here).
    wt = wire_term_index(tag, row["wire"], TUNNEL_D, "BEFORE ANY MUTATION")
    rec["wire_terms_before"] = wt
    if wt.get("index") is None:
        rec["result"] = ("ROW STOPPED BEFORE ANY MUTATION: the FSIT terminal is not a uniquely "
                         "resolvable row of Wire.Terms[] - %s" % wt.get("chosen_by"))
        fact("%s *** %s Nothing was deleted, nothing was wired, no index was guessed. ***"
             % (tag, rec["result"]))
        gate("%s ROW WRITTEN AT ALL" % tag, False, str(rec["result"])[:200])
        dump()
        return rec
    nodes_before, _ = M.node_census(TARGET, "%s before the mutation" % tag)
    counts_b = {}
    for c in ("Wire", "LoopTunnel", "Tunnel"):
        counts_b[c], _ = safe("%s count(%r) before" % (tag, c), lambda cc=c: g.count(TARGET, cc))
    rec["counts_before"] = counts_b
    fact("%s baselines before the mutation: %r" % (tag, counts_b))

    # ---- (iii) THE TWO ORDERINGS. WHICH ONE WORKS IS THE MEASUREMENT (Pre-decided 116-A).
    def do_delete(when):
        d = M.delete_by_uid(TARGET, "Wire", row["wire"], "%s cut %s" % (tag, when))
        rec["delete"] = d
        rec["delete_when"] = when
        gate("%s THE DELETE of wire %d was made by the machine (%s)" % (tag, row["wire"], when),
             not d.get("error_verbatim") and d.get("index") is not None,
             "%r" % ({k: d.get(k) for k in ("index", "gone", "error_verbatim", "result")},))
        st = sink_wire_now(row, sink, hints, tag, "AFTER THE DELETE (%s)" % when, phase0)
        rec["sink_after_delete"] = st
        fact("%s the OLD source #%d's OUTER terminal is now a BARE SOURCE - legal LabVIEW (Pre-decided "
             "69); the sink terminal reads wire %r, state %r"
             % (tag, row["old_source"], st.get("wire"), st.get("state")))
        return st

    if ordering == DELETE_FIRST:
        do_delete("FIRST - Pre-decided 106's ordering")
        inv = resolve_source(row, hints, "%s the INVOKE SITE, post-delete" % tag, expect_bare=True)
        rec["invoke_site_for_the_write"] = {k: inv.get(k) for k in
                                           ("src_diag_index", "src_nodes_index", "src_term_index",
                                            "matches_expectation", "stop")}
        if inv.get("stop"):
            rec["result"] = "ROW STOPPED AFTER THE DELETE, BEFORE THE WRITE: %s" % inv["stop"]
            fact("%s *** %s *** The wire was cut and NOT rebuilt - reported, not hidden."
                 % (tag, rec["result"]))
            gate("%s ROW WRITTEN AT ALL" % tag, False, str(inv["stop"])[:200])
            dump()
            return rec
        rec["connect"] = swapped_connect(tag, "AFTER THE DELETE (the dead-uid question)", row["wire"],
                                         wt["index"], inv)
    else:
        inv = src
        rec["invoke_site_for_the_write"] = {k: inv.get(k) for k in
                                           ("src_diag_index", "src_nodes_index", "src_term_index",
                                            "matches_expectation", "stop")}
        rec["connect"] = swapped_connect(tag, "WHILE WIRE %d IS STILL ALIVE (the branch question)"
                                         % row["wire"], row["wire"], wt["index"], inv)
        if rec["connect"].get("reported_success"):
            # THE READ THE FIRST RUN OF THIS ARM MISSED (`tools/bench/c80_rowd_routeA.log:237`): the op's
            # OWN ordered readback came back `UID 2` = 7506 (the OLD wire, not a new one), `Name` =
            # 'Outgoing Handle', `Is Broken?` = True - which is exactly the c79 review's SILENT-BRANCH
            # signature. The op's readback does not name OWNERS, though, so Pre-decided 117's gate (ii)
            # is UNANSWERABLE unless the net is walked while it still exists. This walk is read-only and
            # changes no ordering of mutations: the delete still follows the connect.
            s0 = sink_wire_now(row, sink, hints, tag, "AFTER THE CONNECT, BEFORE THE DELETE", phase0)
            rec["sink_after_connect_before_delete"] = s0
            inv0 = resolve_source(row, hints, "%s the INVOKE SITE after the connect" % tag,
                                  expect_bare=False)
            rec["invoke_site_after_connect"] = dict(
                (k, inv0.get(k)) for k in ("src_diag_index", "src_nodes_index", "src_term_index",
                                           "candidates", "stop"))
            rec["acceptance_after_connect_before_delete"] = acceptance(
                row, tag, "(a0) AFTER THE CONNECT, BEFORE THE DELETE - MEASURED, NOT ASSERTED "
                          "(Pre-decided 94). THIS is the only reading that names the OWNERS on the net "
                          "the swapped call produced, so it is the only one that can answer Pre-decided "
                          "117's branch question for this ordering", s0["wire"], False)
            a0 = rec["acceptance_after_connect_before_delete"]
            n_src = a0.get("ALL_source_terminal_count")
            rec["discriminator_source_rows_after_the_connect"] = n_src
            fact("%s THE c80-r2 REVIEW'S ONE INDICATOR (its step 2): immediately after the connect and "
                 "BEFORE any delete, net %r has %r source terminal(s) of ANY class, %r. >=2 => the "
                 "swapped call DID join the NEW loop's border terminal to that net, Route A's verb works, "
                 "and Row D reduces to REMOVING THE OLD SOURCE #%d (a NEW step, judgement's). ==1 => "
                 "nothing happened and the op's `UID 2` readback was an echo of the wire half, i.e. arm "
                 "A2 is VOID. The border table printed just above is the same fact read from the terminal "
                 "side (step 3).", tag, a0.get("sink_wire"), n_src, a0.get("ALL_source_terminals"),
                 row["old_source"])
            gate("%s THE DISCRIMINATOR (c80-r2 review step 2): net %r has >=2 source terminals "
                 "immediately after the connect, i.e. THE SWAPPED CALL CONNECTED. Gated only so it is "
                 "unmissable - BOTH values are legitimate outcomes of a measurement"
                 % (tag, a0.get("sink_wire")), (n_src or 0) >= 2,
                 "%r source terminal(s) %r" % (n_src, a0.get("ALL_source_terminals")))
            do_delete("AFTER THE CONNECT - the connect reported success")
        else:
            rec["delete"] = {"skipped": "the connect did NOT report success, so wire %d is NOT deleted - "
                                        "nothing is improvised and the arm target keeps the OLD wiring"
                                        % row["wire"]}
            rec["delete_when"] = "NOT DONE"
            fact("%s wire %d was NOT deleted: %s", tag, row["wire"], rec["delete"]["skipped"])
    rec["call_cost_s"] = (rec.get("connect") or {}).get("cost_s")
    counts_a = {}
    for c in ("Wire", "LoopTunnel", "Tunnel"):
        counts_a[c], _ = safe("%s count(%r) after" % (tag, c), lambda cc=c: g.count(TARGET, cc))
    rec["counts_after"] = counts_a
    fact("%s counts %r -> %r (wire_delta %r) - FACT lines, NEVER the acceptance test (Pre-decided 106: "
         "LANDED is SOURCE IDENTITY, never a wired-count delta)"
         % (tag, counts_b, counts_a, (rec["connect"] or {}).get("wire_delta")))

    # ---- (iv) the state the write left, measured but NOT yet asserted (Pre-decided 94).
    s_a = sink_wire_now(row, sink, hints, tag, "IMMEDIATELY AFTER THE WRITE", phase0)
    rec["sink_after_write"] = s_a
    rec["measurement_after_write"] = acceptance(row, tag, "(a) IMMEDIATELY AFTER THE WRITE - MEASURED, "
                                                          "NOT ASSERTED (Pre-decided 94)", s_a["wire"],
                                                False)

    # ---- (v) the junk purge, then the state the artefact actually keeps.
    _nodes, purge = purge_junk(nodes_before, "%s after the write" % tag, hints)
    rec["purge"] = {"new_uids": purge["new_uids"], "deleted": [d["uid"] for d in purge["deleted"]],
                    "reported_not_deleted": [d["uid"] for d in purge["reported_not_deleted"]]}
    s_b = sink_wire_now(row, sink, hints, tag, "AFTER THE JUNK PURGE", phase0)
    rec["sink_after_purge"] = s_b
    rec["measurement_after_purge"] = acceptance(row, tag, "(b) AFTER THE JUNK PURGE - MEASURED, NOT "
                                                          "ASSERTED (Pre-decided 94)", s_b["wire"], False)
    rec["result"] = "WRITTEN"
    dump()
    return rec


# ==================================== [5] THE ORDERED SECOND PASS - where the row is ASSERTED
def phase_second_pass(row, hints, phase0, arm):
    """PRE-DECIDED 94 + 106. The row is RE-CONNECTED idempotently in a SEPARATE ORDERED PASS - `wire_delta`
    is expected to be 0 because the connection already exists - and THE ACCEPTANCE IS ASSERTED HERE, never
    in the pass that made the connection.

    THE SWAPPED CALL's source half is addressed BY WIRE, so the second pass CANNOT reuse the first pass's
    `wire_uid`: after a successful write the FSIT terminal carries a DIFFERENT wire. The current wire is
    therefore re-read from the tunnel's own table by uid, and the FSIT terminal's index in THAT wire's
    `Wire.Terms[]` is re-read too. Nothing is carried across the mutation (the T2c2 lesson)."""
    tag = "[%s 94 %s]" % (arm["name"], row["tag"])
    head("%s THE ORDERED SECOND PASS - idempotent re-connect, and THE ACCEPTANCE IS ASSERTED HERE" % tag)
    st = R["rows"].get("%s/%s" % (arm["name"], row["tag"])) or {}
    rec = {"row": row["tag"], "arm": arm["name"]}
    K.setdefault("second_pass", []).append(rec)
    if st.get("result") != "WRITTEN":
        rec["skipped"] = "the row was not written, so there is nothing to re-connect"
        fact("%s SKIPPED - %s" % (tag, rec["skipped"]))
        gate("%s the row was WRITTEN at all" % tag, False, str(st.get("result"))[:200])
        return rec
    sink = resolve_sink(row, hints, "%s re-resolve" % tag, phase0)
    inv = resolve_source(row, hints, "%s re-resolve the INVOKE SITE" % tag, expect_bare=False)
    rec["sink"] = {k: sink.get(k) for k in ("sink_term_uid", "sink_wire_before", "stop")}
    rec["invoke_site"] = {k: inv.get(k) for k in ("src_diag_index", "src_nodes_index", "src_term_index",
                                                  "stop")}
    if sink.get("stop") or inv.get("stop"):
        rec["skipped"] = "an endpoint no longer resolves: %s" % (sink.get("stop") or inv.get("stop"))
        fact("%s SKIPPED - %s" % (tag, rec["skipped"]))
        gate("%s the endpoints still resolve" % tag, False, rec["skipped"][:200])
        return rec
    wire_now = sink.get("sink_wire_before") or 0
    rec["wire_the_sink_carries_now"] = wire_now
    if not wire_now:
        rec["skipped"] = ("the sink terminal #%d is BARE, so there is no wire to re-connect FROM - the "
                          "swapped call's source half has no uid" % row["sink_term_uid"])
        fact("%s SKIPPED - %s" % (tag, rec["skipped"]))
        gate("%s the sink terminal carries a wire after the write" % tag, False, rec["skipped"][:200])
        return rec
    wt = wire_term_index(tag, wire_now, TUNNEL_D, "AT THE ORDERED SECOND PASS")
    rec["wire_terms"] = wt
    if wt.get("index") is None:
        rec["skipped"] = "the FSIT terminal is not a unique row of w%r's Wire.Terms[]" % wire_now
        fact("%s SKIPPED - %s" % (tag, rec["skipped"]))
        gate("%s the source half re-resolves on the ordered second pass" % tag, False,
             rec["skipped"][:200])
        return rec
    wires_before, _ = safe("%s count('Wire') before" % tag, lambda: g.count(TARGET, "Wire"))
    rec["reconnect"] = swapped_connect(tag, "THE ORDERED SECOND PASS (idempotent)", wire_now,
                                       wt["index"], inv)
    wires_after, _ = safe("%s count('Wire') after" % tag, lambda: g.count(TARGET, "Wire"))
    rec["wire_census"] = [wires_before, wires_after]
    rec["wire_delta"] = rec["reconnect"].get("wire_delta")
    rec["idempotent"] = (rec["wire_delta"] == 0)
    rec["is_broken_readback"] = rec["reconnect"].get("is_broken_readback")
    fact("%s IDEMPOTENT RE-CONNECT: wire_delta %r (expected 0 - the connection already exists) ; Wire "
         "census %r -> %r ; op error %r ; `Wire.Is Broken?` readback %r"
         % (tag, rec["wire_delta"], wires_before, wires_after,
            rec["reconnect"].get("op_error_verbatim"), rec["is_broken_readback"]))
    if not rec["idempotent"]:
        fact("%s *** wire_delta is NOT 0, so this pass CHANGED the diagram instead of re-reading it. "
             "That is REPORTED; the junk census runs and the acceptance below is still measured on the "
             "state the artefact now holds. ***" % tag)
        nodes_now, _ = M.node_census(TARGET, "%s after a non-idempotent re-connect" % tag)
        purge_junk(nodes_now, "%s re-connect" % tag, hints)
    now = sink_wire_now(row, sink, hints, tag, "AT THE ORDERED SECOND PASS", phase0)
    rec["sink_now"] = now
    rec["acceptance"] = acceptance(row, tag, "(c) THE ORDERED SECOND PASS - THIS IS THE ASSERTION",
                                   now["wire"], False)
    dump()
    return rec


# ================================ [6] THE FIVE GATES OF PRE-DECIDED 116, ASSERTED ON THE SECOND PASS
def arm_gates(row, arm, sp, pd85_before, rowc_owner):
    """THE FIVE ACCEPTANCE GATES, one printed line each, asserted on the ORDERED SECOND PASS only.

    Gate (ii) is Pre-decided 117's BRANCH gate. Its SUBSTANCE is "the source is on the NEW side, never
    the OLD one"; its LITERAL wording names `WhileLoop #23032`, but this reader has already been measured
    naming the SHIFT REGISTER for exactly this kind of terminal (`build_d1_m3a3_run2.log:182`, the
    delivered Row C: `[('RightShiftRegister', 23895)]`, and `:72` for the OLD side:
    `('RightShiftRegister', 4256)`). BOTH readings are evaluated and printed, and this arm's own live
    Row-C calibration (`rowc_owner`, from C0) is printed beside them, so the discrepancy is visible
    rather than resolved silently here."""
    name = arm["name"]
    acc = (sp.get("acceptance") or {})
    src_all = acc.get("ALL_source_terminals") or []
    the_one = acc.get("observed_one_owner")
    owners = acc.get("every_owner_on_the_net") or []
    pd_rows = (M.K.get("pd85_checks") or [])[pd85_before:]
    pd_bad = sum(int(r.get("violations") or 0) for r in pd_rows)
    g_i = (bool(acc.get("sink_wire")) and len(src_all) == 1)
    g_ib = bool(the_one and the_one[1] == row["new_reg"])
    g_ii_literal = bool(the_one and the_one[1] == LOOP_A)
    g_ii_substance = bool(the_one and the_one[1] in (row["new_reg"], LOOP_A))
    g_iii = not (row["old_source"] in owners or OLD_LOOP in owners)
    g_iv = (pd_bad == 0)
    g_v = (sp.get("is_broken_readback") is False)
    g_vi = (sp.get("wire_delta") == 0)
    rec = {"arm": name, "sink_wire": acc.get("sink_wire"),
           "ALL_source_terminals": src_all, "the_one_owner": the_one,
           "every_owner_on_the_net": owners, "pd85_walks": len(pd_rows), "pd85_violations": pd_bad,
           "is_broken_readback": sp.get("is_broken_readback"), "wire_delta": sp.get("wire_delta"),
           "rowc_calibration_owner_live": rowc_owner,
           "gate_i": g_i, "gate_ib_new_register_23868": g_ib,
           "gate_ii_substance": g_ii_substance, "gate_ii_literal_117": g_ii_literal,
           "gate_iii": g_iii, "gate_iv": g_iv, "gate_v": g_v, "gate_vi": g_vi}
    fact("[%s] PRE-DECIDED 117 READER CALIBRATION: this arm's OWN Row-C source owner (from C0) is %r ; "
         "Row D's measured source owner is %r ; 117's literal target is WhileLoop #%d and the NEW "
         "register is #%d. BOTH literal forms are evaluated as their own lines below and NOTHING is "
         "substituted silently.", name, rowc_owner, the_one, LOOP_A, row["new_reg"])
    gate("[%s] GATE (i) the wire the SINK terminal #%d carries has EXACTLY ONE source terminal of ANY "
         "owner class, counted BEFORE any class filter (Pre-decided 77)" % (name, row["sink_term_uid"]),
         g_i, "sink wire %r ; sources %r" % (acc.get("sink_wire"), src_all))
    gate("[%s] GATE (i-b) that ONE source terminal's owner is the NEW register #%d - Pre-decided "
         "106/111's literal form, and the form the DELIVERED Row C passed under "
         "(build_d1_m3a3_run2.log:182)" % (name, row["new_reg"]), g_ib,
         "MEASURED OWNER %r ; live Row-C calibration %r" % (the_one, rowc_owner))
    gate("[%s] GATE (ii) PRE-DECIDED 117 BRANCH GATE, SUBSTANCE - the source terminal's OWNER is on the "
         "NEW side (#%d the register, or #%d the loop), never the OLD one"
         % (name, row["new_reg"], LOOP_A), g_ii_substance,
         "MEASURED OWNER %r ; live Row-C calibration %r" % (the_one, rowc_owner))
    gate("[%s] GATE (ii-literal) PRE-DECIDED 117 AS WRITTEN - the source terminal's OWNER == WhileLoop "
         "#%d (REPORTED and COUNTED; the reader was measured naming the SHIFT REGISTER for this kind of "
         "terminal in the delivered Row C, build_d1_m3a3_run2.log:182)" % (name, LOOP_A), g_ii_literal,
         "MEASURED OWNER %r ; live Row-C calibration %r" % (the_one, rowc_owner))
    gate("[%s] GATE (iii) the OLD register #%d and the OLD loop #%d are OFF the net entirely (a silent "
         "branch of wire %d would leave one of them on it)"
         % (name, row["old_source"], OLD_LOOP, row["wire"]), g_iii, "every owner %r" % (owners,))
    gate("[%s] GATE (iv) PD85 violations 0 on EVERY walk of this arm (%d walk(s))" % (name, len(pd_rows)),
         g_iv, "%d violation(s)" % pd_bad)
    gate("[%s] GATE (v) `Wire.Is Broken?` 6371004 reads FALSE on the SEPARATE ORDERED pass" % name, g_v,
         "readback %r" % (sp.get("is_broken_readback"),))
    gate("[%s] GATE (vi) wire_delta 0 on the ordered idempotent second pass (Pre-decided 94)" % name,
         g_vi, "wire_delta %r" % (sp.get("wire_delta"),))
    rec["verdict"] = "PASS" if (g_i and g_ii_substance and g_iii and g_iv and g_v and g_vi) else "FAIL"
    rec["failing"] = [k for k in ("gate_i", "gate_ii_substance", "gate_iii", "gate_iv", "gate_v",
                                  "gate_vi") if not rec[k]]
    rec["verdict_composition"] = ("gate_i (one source of ANY class) AND gate_ii_substance (the owner is "
                                  "on the NEW side) AND gate_iii (the OLD side is off the net) AND "
                                  "gate_iv (PD85 0) AND gate_v (`Is Broken?` False) AND gate_vi "
                                  "(wire_delta 0). gate_ib (owner == #%d) and gate_ii_literal_117 "
                                  "(owner == #%d) are the TWO LITERAL FORMS of the same requirement and "
                                  "cannot both hold - they are printed and counted, and which of them "
                                  "the reader uses for this class of terminal is a MEASURED fact of this "
                                  "run, carried to the judgement session."
                                  % (row["new_reg"], LOOP_A))
    fact("[%s] ARM VERDICT %s ; failing %r ; gate_ib (#%d) %r ; 117-literal (#%d) %r - the two literal "
         "forms are reported, the SUBSTANCE is what the verdict uses (see the calibration line above)",
         name, rec["verdict"], rec["failing"], row["new_reg"], g_ib, LOOP_A, g_ii_literal)
    return rec


# ======================================================================== ONE WHOLE ARM, END TO END
def run_arm(arm):
    """ONE ARM = one file, one ordering, one verdict. The two measurement arms run on dated SCRATCH
    copies and are deleted; the bed arm runs on the stage artefact's own name."""
    name = arm["name"]
    row = ROWS[0]
    rec = {"arm": name, "ordering": arm["ordering"], "target": arm["target"],
           "scratch": arm["scratch"], "why": arm["why"], "verdict": "NOT REACHED"}
    R["arms"][name] = rec
    head("[ARM %s] %s on %s" % (name, arm["ordering"], os.path.basename(arm["target"])))
    fact("[%s] WHY THIS ORDERING: %s" % (name, arm["why"]))
    pd85_before = len(M.K.get("pd85_checks") or [])
    hints = arm_prepare(arm)
    if hints is None:
        rec["verdict"] = "STOPPED - Diagram #%d does not resolve on the arm target" % D686
        gate("[%s] ARM RAN AT ALL" % name, False, rec["verdict"])
        return rec
    rec["hints"] = hints
    pre = phase_precondition_rowc(hints)
    rec["precondition_rowc"] = pre.get("verdict")
    rec["rowc_owner_live"] = pre.get("observed_one_owner")
    if pre.get("verdict") != "HOLDS":
        rec["verdict"] = "STOPPED at C0 - %s" % pre.get("verdict")
        gate("[%s] ARM RAN AT ALL" % name, False, str(rec["verdict"])[:200])
        return rec
    phase0 = phase0_resolve_tunnel(hints)
    rec["phase0_verdict"] = phase0.get("verdict")
    rec["phase0_sink_term_uid"] = phase0.get("sink_term_uid")
    if phase0.get("verdict") != "HOLDS":
        rec["verdict"] = "STOPPED at P0 - %s" % phase0.get("verdict")
        fact("[%s] *** ROW D NOT ATTEMPTED - a FAILED PREDICTION at PHASE 0. Wire %d is NOT deleted, no "
             "address is improvised for #%d, and there is no GUI fallback. ***", name, row["wire"],
             row["sink_uid"])
        gate("[%s] ARM RAN AT ALL" % name, False, str(rec["verdict"])[:200])
        return rec
    if left_s() < ROW_MIN_S:
        rec["verdict"] = "STOPPED - only %.0f s left before the reserve; an arm needs %.0f s" % (
            left_s(), ROW_MIN_S)
        gate("[%s] ARM RAN AT ALL" % name, False, str(rec["verdict"])[:200])
        return rec
    r = one_row(row, hints, phase0, arm)
    rec["row_result"] = r.get("result")
    rec["connect_verbatim"] = r.get("connect")
    rec["delete"] = {k: (r.get("delete") or {}).get(k)
                     for k in ("index", "gone", "error_verbatim", "result", "skipped")}
    rec["delete_when"] = r.get("delete_when")
    sp = phase_second_pass(row, hints, phase0, arm)
    rec["second_pass"] = {k: sp.get(k) for k in ("wire_delta", "idempotent", "is_broken_readback",
                                                 "wire_the_sink_carries_now", "skipped")}
    if r.get("result") != "WRITTEN" or sp.get("skipped"):
        rec["verdict"] = "FAIL"
        rec["gates"] = {"verdict": "FAIL", "reason": r.get("result") or sp.get("skipped")}
        gate("[%s] ARM VERDICT PASS - every Row-D gate held on this ordering" % name, False,
             str(rec["gates"]["reason"])[:220])
        return rec
    rec["gates"] = arm_gates(row, arm, sp, pd85_before, rec.get("rowc_owner_live"))
    rec["verdict"] = rec["gates"]["verdict"]
    gate("[%s] ARM VERDICT PASS - every Row-D gate held on this ordering" % name,
         rec["verdict"] == "PASS", "failing %r" % (rec["gates"].get("failing"),))
    dump()
    return rec


# ==================================================================================== [S] THE SAVE
def phase_save():
    """PRE-DECIDED 96/101 - THE STAGE ALWAYS LEAVES A FILE. `ExecState` 1 => an ordinary SaveInstrument;
    otherwise `save(allow_broken=True)` diverts to the `gui_save` route with USER RULE 17:5x in full. For
    a SAVE the after-confirmation is THE FILE ITSELF - size and md5 read back off disk and required to
    differ from the input - with the saved path verified to be the claudeDev target and all four md5 pins
    re-read at [H]. The capture paths are passed RAW: `gscript.q()` quotes exactly once, and pre-quoting
    is the measured cause of M3a-1's captures never landing (build_d1_m3a1.log:3402)."""
    head("[S] THE SAVE - the stage always leaves a file (Pre-decided 88/96/101)")
    rec = {"dest": TARGET, "save_error_verbatim": "",
           "NOT_COMPUTATION_EQUIVALENT": "THE M3a-3 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE "
                                         "ORIGINAL (Pre-decided 97). It is BROKEN BY DESIGN and is "
                                         "NEVER RUN (34(f))."}
    rec["exec_state_at_save"] = read_es("[S] immediately before the save")
    rec["route"] = ("ordinary SaveInstrument" if rec["exec_state_at_save"] == 1
                    else "the Pre-decided 88/101 broken-intermediate route -> gui_save")
    fact("[S] ExecState at the save is %r, so the route is: %s (ExecState is a ROUTE SELECTOR here and "
         "nothing else - it is never a criterion, Pre-decided 89/97)"
         % (rec["exec_state_at_save"], rec["route"]))
    shot_b = os.path.join(BENCH, "m3a3_save_before_%s.png" % STAMP)
    shot_a = os.path.join(BENCH, "m3a3_save_after_%s.png" % STAMP)
    out_b, err_b = safe("[S] capture BEFORE the save",
                        lambda: g._lv_gui("-Action", "shot", "-Out", shot_b))
    rec["capture_before_stdout"] = (out_b or "")[-400:]
    gate("S3 the BEFORE capture LANDED ON DISK (USER RULE 17:5x - locate in a capture taken just before)",
         os.path.exists(shot_b),
         "%s%s ; lv_gui said %r" % (shot_b, (" ; " + err_b) if err_b else "", (out_b or "")[-160:]))
    try:
        rec["save_returned_size"] = g.save(TARGET, allow_broken=True)
    except Exception as e:                                                         # noqa: BLE001
        rec["save_returned_size"] = None
        rec["save_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    out_a, err_a = safe("[S] capture AFTER the save",
                        lambda: g._lv_gui("-Action", "shot", "-Out", shot_a))
    rec["capture_after_stdout"] = (out_a or "")[-400:]
    gate("S4 the AFTER capture LANDED ON DISK (USER RULE 17:5x - capture after and confirm)",
         os.path.exists(shot_a),
         "%s%s ; lv_gui said %r" % (shot_a, (" ; " + err_a) if err_a else "", (out_a or "")[-160:]))
    rec["captures"] = {
        "before": shot_b, "before_exists": os.path.exists(shot_b),
        "before_size": (os.path.getsize(shot_b) if os.path.exists(shot_b) else None),
        "after": shot_a, "after_exists": os.path.exists(shot_a),
        "after_size": (os.path.getsize(shot_a) if os.path.exists(shot_a) else None),
        "quoting": "the path is passed RAW - gscript.q() quotes it exactly once"}
    fact("[S] capture -> act -> capture: before %r (exists %r, %r B), after %r (exists %r, %r B)"
         % (os.path.basename(shot_b), rec["captures"]["before_exists"], rec["captures"]["before_size"],
            os.path.basename(shot_a), rec["captures"]["after_exists"], rec["captures"]["after_size"]))
    if rec["save_error_verbatim"]:
        fact("[S] THE SAVE WAS REFUSED, VERBATIM: %s" % rec["save_error_verbatim"])
        refusal("[S] g.save(TARGET, allow_broken=True)", rec["save_error_verbatim"])
    ff = D.file_facts("[S] the M3a-3b artefact", TARGET)
    rec.update({"exists": bool(ff.get("exists")), "md5": ff.get("md5"), "size": ff.get("size"),
                "version_candidates": ff.get("version_candidates")})
    rec["bytes_equal_to_the_input"] = (ff.get("md5") == INPUT_MD5)
    gate("S1 the saved artefact's bytes DIFFER from THE BED - the in-memory edits reached the disk",
         rec["exists"] and not rec["bytes_equal_to_the_input"],
         "md5 %r vs bed %r ; size %r vs bed %r" % (rec.get("md5"), INPUT_MD5, rec.get("size"),
                                                   R.get("input_size_before")))
    gate("S2 the saved path IS the claudeDev target this run created",
         os.path.normcase(os.path.dirname(TARGET)) == os.path.normcase(g.CLAUDEDEV)
         and os.path.basename(TARGET).startswith(TARGET_PREFIX) and rec["exists"], TARGET)
    fact("[S] FILE ON DISK: %s  md5 %r  size %r  (input md5 %s size %r ; bytes equal %r)"
         % (TARGET, rec["md5"], rec["size"], INPUT_MD5, R.get("input_size_before"),
            rec["bytes_equal_to_the_input"]))
    fact("[S] *** %s IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL (Pre-decided 97) AND IS NEVER RUN "
         "(34(f)). It is never cold-loaded headless either (the skill's recompile-spin rule). ***"
         % os.path.basename(TARGET))
    R["artefacts_on_disk"].append(rec)
    fact("[S] NO COLD REOPEN IS ATTEMPTED at ExecState %r" % rec["exec_state_at_save"])
    dump()
    return rec


# ============================================================================================== main
def main():
    print("=" * 100, flush=True)
    print("=== build_d1_m3a3  %s  - STAGE **M3a-3b: ROW D ALONE, ROUTE A** (Pre-decided 104-118). ROW C "
          "IS ALREADY IN THE BED AND IS NOT REDONE - it is asserted read-only at [C0] in every arm."
          % STAMP, flush=True)
    print("=== THREE ARMS: A1 delete-then-connect and A2 connect-then-delete on DATED SCRATCH copies "
          "(deleted in this run), then - ONLY IF ONE PASSED EVERY GATE - the same ordering on THE BED.",
          flush=True)
    print("=== NOTHING IS BUILT. If both arms fail, Route B (`OpConnectByUid`) is EXPENSIVE CONSTRUCTION "
          "and gets a FRESH CYCLE (Pre-decided 116-B) - it is not improvised here.", flush=True)
    print("=== THE ARTEFACT THIS RUN MAY SAVE IS **NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL**, IS "
          "BROKEN BY DESIGN AND IS NEVER RUN (34(f), Pre-decided 97).", flush=True)
    print("=" * 100, flush=True)
    bed_arm = None
    try:
        phase_files()
        # ---- THE TWO MEASUREMENT ARMS, on dated scratch copies, deleted in this same run.
        # THE c79 REVIEW'S "STEP 4" PROBE IS NOT RUN, and the reason is measured, not stylistic: run 1
        # (`tools/bench/c80_rowd_routeA.log:289-290`) showed it returns `err_uidvi ''` for BOTH a DELETED
        # wire uid (arm A1) and the terminal uid 7488, so an empty `err_uidvi` establishes nothing; and
        # the c80-r2 review showed the probe is uninformative BY CONSTRUCTION, because its index triple
        # is deliberately out of range so the only downstream indicator was guaranteed to fail whatever
        # the uid resolved to. Its sound replacement - `OpOwnerChain_v1` with `uid_in = 7488`, reading the
        # SELF echo - needs a labels map that is NOT on disk and a `read_owner()` that hard-codes the MAIN
        # VI as its target, i.e. tool work; and Route B is a FRESH CYCLE's decision anyway (116-B).
        for arm in ARMS:
            run_arm(arm)
            arm_cleanup(arm)
        # ---- THE ROUTE SELECTION. Mechanical: Pre-decided 116-A, A1 preferred because it is
        #      Pre-decided 106's ordering.
        winner = next((a for a in ARMS if (R["arms"].get(a["name"]) or {}).get("verdict") == "PASS"),
                      None)
        R["route_selection"].update({
            "rule": "Pre-decided 116-A / 116-B",
            "arm_verdicts": dict((a["name"], (R["arms"].get(a["name"]) or {}).get("verdict"))
                                 for a in ARMS),
            "winner": None if winner is None else winner["name"],
            "winning_ordering": None if winner is None else winner["ordering"]})
        fact("[R] ROUTE SELECTION: arm verdicts %r -> winner %r (%r)",
             R["route_selection"]["arm_verdicts"], R["route_selection"]["winner"],
             R["route_selection"]["winning_ordering"])
        gate("R1 ROUTE A WORKS - at least one ordering of the SWAPPED call passed EVERY Row-D gate on a "
             "dated scratch copy of the bed (Pre-decided 116-A)", winner is not None,
             "arm verdicts %r" % (R["route_selection"]["arm_verdicts"],))
        if winner is None:
            raise Halt("NEITHER ordering of the swapped call passed Row D's gates. THE BED IS UNTOUCHED "
                       "(it was never opened), both scratch copies are deleted, and NO OP WAS BUILT. "
                       "Route B (`OpConnectByUid`: uid -> `UID to GObject Reference.vi` -> TMSC on a "
                       "Terminal seed -> the Invoke's `reference`, donor `OpConnectNested_v2`) is "
                       "EXPENSIVE CONSTRUCTION and gets a FRESH CYCLE (Pre-decided 116-B); it is never "
                       "improvised at the end of a dispatch. The step-4 probe above says whether its "
                       "first gate - does a TERMINAL uid resolve - is clear.")
        # ---- ARM 3: THE BED, on the winning ordering. NOTHING NEW IS BUILT (Pre-decided 116-A).
        bed_arm = {"name": "ARM3-BED", "ordering": winner["ordering"], "target": BED_TARGET,
                   "scratch": False,
                   "why": "Pre-decided 116-A: 'If A works, Row D proceeds on it in the same dispatch and "
                          "NOTHING NEW IS BUILT.' The winning ordering is %s, from arm %s."
                          % (winner["ordering"], winner["name"])}
        K["refusals_before_the_bed_arm"] = len(refusals)
        K["defects_before_the_bed_arm"] = len(defects)
        K["m3a1_refusals_before_the_bed_arm"] = len(M.refusals)
        run_arm(bed_arm)
        K["counts_final"] = counts("[F] final, in memory")
        # THE STAGE ALWAYS LEAVES A FILE (Pre-decided 96) - but only when there is something IN it that
        # PASSED. A byte-identical copy of the bed under a new stage name is not an artefact, it is a
        # decoy; and an artefact whose Row D was cut but not rebuilt is run 1's REJECTED artefact.
        if (R["arms"].get("ARM3-BED") or {}).get("verdict") == "PASS":
            phase_save()
        else:
            gate("S0 THE BED ARM PASSED EVERY GATE, so there is something worth saving",
                 False, "ARM3-BED verdict %r ; gates %r"
                        % ((R["arms"].get("ARM3-BED") or {}).get("verdict"),
                           (R["arms"].get("ARM3-BED") or {}).get("gates")))
            fact("[S] NO ARTEFACT IS SAVED: the bed arm did not pass, so the in-memory copy is NOT a "
                 "stage output. Saving it would produce either a DECOY bed (byte-identical) or run 1's "
                 "REJECTED shape (a cut-but-not-rebuilt consumer). The bed %s (md5 %s) remains the "
                 "current bed and its file is deleted below.",
                 os.path.basename(INPUT), INPUT_MD5[:8])
            arm_cleanup(bed_arm)
            bed_arm = None
    except Halt as e:
        fact("HALTED: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        # Pre-decided 100 SS2: OUR bug, NOT a machine refusal. `refusal()` is not called here.
        import traceback
        R["unexpected_exception"] = traceback.format_exc()[-2500:]
        defect("main", e)
    finally:
        head("[H] HYGIENE - panels closed, the md5 pins AFTER, the tool pins, the refs and the handles")
        for _p in (SCRATCH_A1, SCRATCH_A2, BED_TARGET):
            safe("close_panel(%s)" % os.path.basename(_p), lambda pp=_p: g.close_panel(pp))
        # A SCRATCH IS NEVER LEFT ON DISK, whatever the run did (CLAUDE.md: created and deleted in the
        # same run). `arm_cleanup` already removed each one; this is the belt-and-braces pass for the
        # case where an arm raised before reaching it.
        for _p in (SCRATCH_A1, SCRATCH_A2):
            for _ in range(4):
                try:
                    if os.path.exists(_p):
                        os.remove(_p)
                    break
                except OSError:
                    time.sleep(1.0)
            gate("H0 no scratch copy is left on disk: %s" % os.path.basename(_p),
                 not os.path.exists(_p), _p)
        pr = probe_hash("H INPUT THE BED AFTER", INPUT)
        gate("H2 the bed's md5 is UNCHANGED after the run", pr.get("md5") == INPUT_MD5,
             "before %r / after %r" % (R.get("input_md5_before"), pr.get("md5")))
        for tag, path, pin in PINS:
            pr = probe_hash("H %s AFTER" % tag, path)
            gate("H3 %s md5 is STILL its pin %s" % (tag, pin[:8]), pr.get("md5") == pin,
                 "%r" % (pr.get("md5"),))
        for p in TOOL_PINS:
            pr = probe_hash("H TOOL %s AFTER" % os.path.basename(p), p)
            gate("H5 TOOL %s is byte-identical before and after" % os.path.basename(p),
                 pr.get("md5") == (K.get("tool_pins_before") or {}).get(p),
                 "%r vs %r" % (pr.get("md5"), (K.get("tool_pins_before") or {}).get(p)))
        rc = g.ref_counts()
        R["ref_counts"] = rc
        fact("refs: %r" % (rc,))
        gate("H6 refs opened == closed and 0 live", rc.get("live") == 0, "%r" % (rc,))
        R["handles"]["after"] = labview_handles()
        fact("LabVIEW handles AFTER: %r (before %r, after the restart %r) - a FACT beside the ~31,500 "
             "baseline, NOT a gate (Pre-decided 100 SS7)"
             % (R["handles"].get("after"), R["handles"].get("before"),
                R["handles"].get("after_restart")))
        gate("H7 the LabVIEW handle count was read at entry and at exit",
             isinstance(R["handles"].get("before"), int) and isinstance(R["handles"].get("after"), int),
             "%r -> %r" % (R["handles"].get("before"), R["handles"].get("after")))
        imported = M.refusals[K.get("m3a1_refusals_at_entry", 0):]
        R["imported_helper_refusals"] = imported
        # H8 / H9 ARE SCOPED TO THE BED ARM, and this is not a softening - it is what the run IS. The two
        # scratch arms are a DISCRIMINATING TEST whose negative outcome is the measurement: a dead wire
        # uid being refused, or an already-wired terminal being branched, is exactly what they were run
        # to find out. Counting those refusals against the deliverable would make every honest
        # measurement look like a broken build. Everything is REPORTED either way, verbatim.
        bed_refusals = refusals[K.get("refusals_before_the_bed_arm", 0):]
        bed_defects = defects[K.get("defects_before_the_bed_arm", 0):]
        bed_imported = M.refusals[K.get("m3a1_refusals_before_the_bed_arm",
                                        K.get("m3a1_refusals_at_entry", 0)):]
        arm_refusals = refusals[:K.get("refusals_before_the_bed_arm", len(refusals))]
        arm_defects = defects[:K.get("defects_before_the_bed_arm", len(defects))]
        R["measurement_arm_refusals_REPORTED_NOT_GATED"] = arm_refusals
        R["measurement_arm_defects_REPORTED_NOT_GATED"] = arm_defects
        fact("H8b THE MEASUREMENT ARMS (REPORTED, NEVER GATED - their negative outcome IS the "
             "measurement): %d machine refusal(s) %r ; %d our-code defect(s) %r"
             % (len(arm_refusals), [r["where"] for r in arm_refusals], len(arm_defects),
                [("%s at %s: %s" % (d["exception_type"], d["source_line"], d["where"]))
                 for d in arm_defects]))
        gate("H8 no mutator call was REFUSED BY THE MACHINE IN THE BED ARM (this file's refusals and the "
             "imported helpers'; a Python exception of OURS is NOT one - it is H9)",
             not bed_refusals and not bed_imported,
             "%d machine refusal(s) here %r ; %d in the imported helpers %r"
             % (len(bed_refusals), [r["where"] for r in bed_refusals], len(bed_imported),
                [r.get("where") for r in bed_imported]))
        gate("H9 NO DEFECT IN OUR OWN PYTHON CODE IN THE BED ARM - no exception was raised by this script "
             "itself there (a bug of ours is NEVER a machine refusal)", not bed_defects,
             "%d our-code defect(s): %r"
             % (len(bed_defects), [("%s at %s: %s" % (d["exception_type"], d["source_line"], d["where"]))
                                   for d in bed_defects]))
        left = [(os.path.basename(a["dest"]), a.get("md5"), a.get("size"))
                for a in R["artefacts_on_disk"] if a.get("exists")]
        R["files_left_on_disk"] = left
        fact("THE FILES THIS RUN LEFT ON DISK: %r" % (left,))
        if left:
            fact("*** EVERY FILE NAMED ABOVE IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL AND IS NEVER "
                 "RUN (34(f), Pre-decided 97). ***")
        dump()
        print("\n" + "=" * 100, flush=True)
        print("=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                  ("; failing: " + ", ".join(fails)) if fails else ""),
              flush=True)
        print("=== JSON: %s   elapsed %.1f s" % (OUT, time.time() - T_START), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
