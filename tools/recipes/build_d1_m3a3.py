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

THE PREDICTION CONTRACT, WRITTEN BEFORE THE RUN.
 W1 (FILES ONLY, BEFORE LabVIEW IS TOUCHED AT ALL - the first gate in the run). `Terminal.Connect Wire`
    **6349C03 is invoked ON THE SINK TERMINAL** (`docs/NAMES.md:245`, `:847`), so Row D needs a WRITER
    that can hold a reference to a sink reached WITHOUT `Nodes[]`. PREDICTION: such a writer is on disk.
      HOLDS -> the row runs.
      FAILS -> the run HALTS IMMEDIATELY, before `ensure_loaded`, before the copy, before any delete.
               Wire 7506 is NOT deleted, no address is improvised, there is no GUI fallback and no
               substitute source (rule 1a). Run 1's lesson is exactly this ordering: its delete ran and
               THEN the writer raised `com_error 5507 File not found` in `GetVIReference`, leaving
               `Global #7202` t0 BARE - a dropped consumer and a rejected artefact.
    ⚠️ MEASURED 2026-09-22 09:2x, `tools/bench/c78_rowd_writer.log`: of the FOUR label maps declaring
    method 6349C03 (`opconnectfromwire_v0`, `opconnectnested`, `opconnectnested_v1`, `opconnectnested_v2`)
    **every one addresses its SINK as (`index`, `index 2`, `index 3`) = (diagram, `Nodes[]`,
    `Terminals[]`)**, and the count of writers whose sink is addressed by a UID is **0**.
    `opfsinnertunnelterm_labels.json` declares NO `method` key (`kind: IN`) - it is a READER. So W1 is
    expected to FAIL on today's fleet, and that is a question for judgement, not a thing this file
    decides or works around.
 C0 (PRECONDITION, read-only, asserted not rebuilt). The net carried by `Global #7202` t0 'Focus
    position' still has EXACTLY ONE source terminal of ANY owner class and it is
    `RightShiftRegister #23895` (Row C, delivered in the bed). PD85 violations 0 on the walk. If C0
    fails the bed is not what this stage was told it is: STOP, delete nothing.
 P0 (ROW D's SINK). `OpFsInnerTunnelTerm_v0` on uid 7468 returns `LeftTerm` = a terminal uid with its
    error column empty, and that terminal carries wire 7506. Anything else - an error column, a missing
    uid, or a face carrying a different wire - is a FAILED PREDICTION: STOP, delete nothing, improvise
    nothing (Pre-decided 107's prohibition, which 109 leaves untouched).
 P1 The loop border `#23032` resolves live at Diagram idx 19, Nodes[21], t1 'Outgoing Handle',
    is_source True and BARE (`diag_c75b_loopterms.log:76`, bare list `:82`).
 P3 THE ACCEPTANCE (Pre-decided 85 + 106 + 111, not relaxed): the wire the SINK terminal carries
    afterwards has EXACTLY ONE source terminal of ANY owner class (counted before any class filter -
    Pre-decided 77) and that terminal is `#23868`'s OUTER. Asserted on an ORDERED SECOND, IDEMPOTENT
    re-connect (`wire_delta` 0), NEVER in the pass that makes the connection (Pre-decided 94). The OLD
    `#637` t10 must be OFF the net. Hop count is an OUTPUT, never a criterion (Pre-decided 90). Every
    `OpWireSource_v5` row must satisfy `recip == queried_uid`; violations reported per walk (PD 85).
 P4 `LANDED` IS SOURCE IDENTITY (Pre-decided 106). Never "the sink is still wired", never a wired-count
    delta: `connect_from_wire` into an already-wired sink is a MEASURED SILENT NO-OP that passed a gate
    five runs running (`tools/bench/build_d1_m3a1.log:1174,:1875,:2593,:3311`; cause
    `tools/gscript.py:2522-2523`). That is why THE DELETE PRECEDES THE CONNECT.

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
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_NESTED           # noqa: E402
from build_opconnectnested_v1 import OP as OP_CONNECT_NESTED                       # noqa: E402
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
TARGET = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3b_%s.vi" % STAMP)
TARGET_PREFIX = "D1_s3b_m3a3b_"
OUT = os.path.join(BENCH, "build_d1_m3a3b.json")
# THE WRITER'S OWN OP VI, CHECKED ON DISK BEFORE ANY LabVIEW CALL (gate W0 in phase_files).
# RUN 1 (2026-09-22 07:56) DIED HERE: `gscript.connect_nested_v2` EXISTS as a def - `c60c_astcheck` gate 4
# verifies exactly that and PASSED it - but `OpConnectNested_v2.vi` IS NOT ON DISK in claudeDev, so the call
# raised `com_error 5507 (Hex 0x7) File not found` inside `GetVIReference`, AFTER the row's wire had already
# been deleted. A gscript verb existing is NOT its op VI existing; this file checks the file itself.
CONNECT_NESTED_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"),
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
# A writer is bound to a SINK KIND, not to a row. `Terminal.Connect Wire` 6349C03 is invoked ON THE SINK
# TERMINAL (docs/NAMES.md:245, :847), so a sink this fleet cannot hold a reference to has NO writer, and
# a row with no writer is NOT ATTEMPTED - it is never approximated, never routed through a Local, never
# clicked (rule 1a; Pre-decided 107's prohibition, left untouched by 109).
#
# MEASURED 2026-09-22 09:2x, tools/bench/c78_rowd_writer.log: the FOUR label maps declaring method
# 6349C03 all address their sink as (index, index 2, index 3) = (diagram, Nodes[], Terminals[]); the
# count of writers with a UID-addressed sink is 0; opfsinnertunnelterm_labels.json declares no method
# at all (kind 'IN' - a reader). So `tunnel_uid` has no writer TODAY and W1 halts the run.
WRITERS = {
    # sink kind -> (callable, the op VI that must be on disk, how the sink is addressed)
    "node": (CONNECT_NESTED, OP_CONNECT_NESTED, "(diagram idx, Nodes[] idx, Terminals[] idx)"),
    "tunnel_uid": (None, None, "a TERMINAL UID (#%d) - no Nodes[] membership exists for a "
                               "FlatSequenceInnerTunnel" % TUNNEL_D_TERM),
}

RUN_DEADLINE_S = 45 * 60.0       # the `bgrun --max-min` this file is launched under
RESERVE_S = 420.0                # held back for the save and the hygiene tail
ROW_MIN_S = 300.0

T_START = time.time()
passes, fails, facts, refusals = [], [], [], []
# OUR-CODE DEFECTS - Python exceptions raised by THIS SCRIPT, kept SEPARATE from machine refusals
# (Pre-decided 100 SS2): a bug of ours must never be reported as "a mutator call the machine refused".
defects = []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "target": TARGET, "input": INPUT,
     "task": "STAGE M3a-3: re-source the TWO downstream consumers onto the NEW loop's RIGHT registers - "
             "delete-and-rebuild rows, the CORRECTED (transposed) pairing of Pre-decided 104, acceptance "
             "= the one-source identity of Pre-decided 85/106 on an ordered idempotent second pass.",
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
     "is_broken_policy": "`Wire.Is Broken?` is never a criterion and never a type discriminator here "
                         "(Pre-decided 89/94). RUN 2 CHANGE: the writer is `connect_nested_v1` "
                         "(OpConnectNested_v1.vi), because `OpConnectNested_v2.vi` - the byte-copy with "
                         "the 6371004 readback deleted - IS NOT ON DISK, which is what killed run 1. v1 "
                         "PRINTS its own `UID`/`Name`/`UID 2`/`Is Broken?` readback; that line is "
                         "REPORTED and never gated, and its dataflow order relative to the Connect Wire "
                         "invoke is not fixed (build_opconnectnested_v1.py:444-446).",
     "no_new_op": True, "no_new_verb": True, "no_new_device": True, "no_new_checker": True,
     "move_in_not_called": "this file calls move_in nowhere and imports it nowhere - hence --route owner",
     "creates_no_object": True,
     "remove_bad_wires_scripted": "not imported, not called (BANNED since cycle 58)",
     "no_whole_vi_gobject_census": True,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run - the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py is not called",
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "purges": [], "rows": {}, "phase0": {}, "build": {}}
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
    gate("W1 EVERY ROW HAS A WRITER BOUND TO ITS SINK KIND - `Terminal.Connect Wire` 6349C03 is invoked ON "
         "THE SINK TERMINAL (docs/NAMES.md:245), so a sink this fleet cannot hold a reference to has no "
         "writer and the row is NOT ATTEMPTED (no improvised address, no Local, no GUI fallback)",
         not unbound,
         "unbound row(s): %r ; measured inventory: tools/bench/c78_rowd_writer.log - all four 6349C03 "
         "label maps address their sink as (diagram, Nodes[], Terminals[]), 0 writers take a UID-"
         "addressed sink, and opfsinnertunnelterm_labels.json declares no method at all (a READER)"
         % (unbound,))
    if unbound:
        raise Halt("no writer exists for the sink kind of row(s) %r. NOTHING WAS OPENED, NOTHING WAS "
                   "COPIED, NOTHING WAS DELETED - wire %d is untouched and the bed is byte-unchanged. "
                   "Row D's sink is a TERMINAL UID (#%d on FlatSequenceInnerTunnel #%d, Pre-decided "
                   "109/111) and every Connect-Wire writer on disk addresses its sink by (diagram, "
                   "Nodes[], Terminals[]); a FlatSequence is a GObject, never a Node, so no Nodes[] "
                   "address for it exists or can exist. Building such a writer is a NEW OP and a design "
                   "decision - the judgement session's, not this file's (CLAUDE.md section 3)."
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


# ============================================== [1] the target copy and the pre-write FACT census
def phase_copy():
    head("[1] THE TARGET IS A COPY OF THE INPUT - the input is never opened, never edited, never run")
    shutil.copy2(INPUT, TARGET)
    time.sleep(0.4)
    pr = probe_hash("[1] the target, straight after the copy", TARGET)
    gate("H4 the target starts byte-identical to the input artefact", pr.get("md5") == INPUT_MD5,
         "%r vs %r" % (pr.get("md5"), INPUT_MD5))
    fact("[1] the target is %s - the STAGE'S OWN OUTPUT NAME; every edit below is made on THIS file"
         % os.path.basename(TARGET))
    t0 = time.time()
    _, err = safe("[1] ensure_loaded(target)", lambda: g.ensure_loaded(TARGET))
    fact("[1] ensure_loaded(target) took %.1f s%s (edits are SILENTLY DECLINED on a target that is not "
         "fully loaded - gscript.py:764)" % (time.time() - t0, (" ERROR " + err) if err else ""))
    read_es("[1] the target, COLD")
    K["counts_before"] = counts("[1] COLD")
    di, derr = safe("[1] diag_index(#%d)" % D686, lambda: diag_index(TARGET, D686))
    K["d686_index"] = di
    fact("[1] Diagram #%d -> traverse index %r%s (expected 19 - diag_c75b_loopterms.log)"
         % (D686, di, (" ; " + derr) if derr else ""))
    if di is None:
        raise Halt("Diagram #%d does not resolve on the target" % D686)
    dump()
    return [di, TOP]


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
    rec = {"row": ROWC["tag"], "evidence_for_the_claim": ROWC["evidence"]}
    R["precondition_rowc"] = rec
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
def one_row(row, hints, phase0):
    tag = "[ROW %s]" % row["tag"]
    head("%s delete wire %d, then NEW register #%d OUTER -> %s"
         % (tag, row["wire"], row["new_reg"],
            ("FlatSequenceInnerTunnel #%d" % row["sink_uid"]) if row["sink_kind"] == "tunnel"
            else ("#%d t%r %r" % (row["sink_uid"], row["sink_expect_term"], row["sink_name"]))))
    fact("%s WHY: %s" % (tag, row["why"]))
    rec = {"row": row, "writer": "build_opconnectnested_v1.connect_nested_v1 (OpConnectNested_v1.vi, "
                                 "VERIFIED ON DISK by gate W0 - run 1 called gscript.connect_nested_v2, "
                                 "whose op VI does not exist, and died with com_error 5507 File not "
                                 "found AFTER the delete)",
           "shape": "DELETE-AND-REBUILD (cycle 62's re-cut): the sink is ALREADY WIRED, and "
                    "connect_from_wire into an already-wired sink is a MEASURED SILENT NO-OP "
                    "(build_d1_m3a1.log:1174,:1875,:2593,:3311 ; gscript.py:2522-2523)",
           "never_a_local": "a Local is NEVER substituted for this row (rule 1a)"}
    R["rows"][row["tag"]] = rec

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

    # ---- (ii) THE DELETE. Mandatory and first (Pre-decided 106).
    nodes_before, _ = M.node_census(TARGET, "%s before the delete" % tag)
    counts_b = {}
    for c in ("Wire", "LoopTunnel", "Tunnel"):
        counts_b[c], _ = safe("%s count(%r) before" % (tag, c), lambda cc=c: g.count(TARGET, cc))
    rec["counts_before"] = counts_b
    fact("%s baselines before the delete: %r" % (tag, counts_b))
    rec["delete"] = M.delete_by_uid(TARGET, "Wire", row["wire"], "%s cut" % tag)
    gate("%s THE DELETE of wire %d was made by the machine" % (tag, row["wire"]),
         not rec["delete"].get("error_verbatim") and rec["delete"].get("index") is not None,
         "%r" % ({k: rec["delete"].get(k) for k in ("index", "gone", "error_verbatim", "result")},))
    after_cut = sink_wire_now(row, sink, hints, tag, "AFTER THE DELETE, BEFORE THE REBUILD", phase0)
    rec["sink_after_delete"] = after_cut
    fact("%s the OLD source #%d's OUTER terminal is now a BARE SOURCE - legal LabVIEW (Pre-decided 69); "
         "the sink terminal reads wire %r, state %r"
         % (tag, row["old_source"], after_cut.get("wire"), after_cut.get("state")))

    # ---- (iii) THE REBUILD. Indices RE-RESOLVED after the delete, never carried across the mutation.
    sink2 = resolve_sink(row, hints, "%s post-delete" % tag, phase0)
    src2 = resolve_source(row, hints, "%s post-delete" % tag, expect_bare=True)
    rec["sink_resolved_for_write"] = sink2
    rec["source_resolved_for_write"] = src2
    stop2 = sink2.get("stop") or src2.get("stop")
    if stop2:
        rec["result"] = "ROW STOPPED AFTER THE DELETE, BEFORE THE WRITE: %s" % stop2
        fact("%s *** %s *** The wire was cut and NOT rebuilt - reported, not hidden." % (tag, rec["result"]))
        gate("%s ROW WRITTEN AT ALL" % tag, False, stop2)
        dump()
        return rec
    t0 = time.time()
    writer = WRITERS[row["sink_kind"]][0]
    if writer is None:
        # UNREACHABLE after gate W1 - kept so that a future edit which deletes W1 fails LOUDLY and
        # BEFORE a second mutation, instead of improvising an address (rule 1a, Pre-decided 107).
        raise Halt("no writer is bound to sink kind %r, and the wire has ALREADY BEEN CUT. This row is "
                   "reported as CUT-NOT-REBUILT; nothing is improvised." % row["sink_kind"])
    try:
        dw, es, err = writer(TARGET, sink2["sink_diag_index"], sink2["sink_nodes_index"],
                             sink2["sink_term_index"], src2["src_diag_index"],
                             src2["src_nodes_index"], src2["src_term_index"],
                             CONNECT_NESTED_LABELS)
        rec["connect"] = {"wire_delta": dw, "exec_state": es, "op_error": str(err)[:250]}
        if err:
            refusal("%s connect_nested_v1" % tag, str(err)[:250])
    except Exception as e:                                                         # noqa: BLE001
        rec["connect"] = {"call_error": "%s: %s" % (type(e).__name__, str(e)[:250])}
        defect("%s connect_nested_v1(sink D[%r].N[%r].T[%r] <- src D[%r].N[%r].T[%r])"
               % (tag, sink2["sink_diag_index"], sink2["sink_nodes_index"], sink2["sink_term_index"],
                  src2["src_diag_index"], src2["src_nodes_index"], src2["src_term_index"]), e)
    rec["call_cost_s"] = round(time.time() - t0, 2)
    fact("%s connect_nested_v1(sink_diag=%r, sink_node=%r, sink_term=%r, src_diag=%r, src_node=%r, "
         "src_term=%r) -> %r (%.2f s)"
         % (tag, sink2["sink_diag_index"], sink2["sink_nodes_index"], sink2["sink_term_index"],
            src2["src_diag_index"], src2["src_nodes_index"], src2["src_term_index"], rec["connect"],
            rec["call_cost_s"]))
    counts_a = {}
    for c in ("Wire", "LoopTunnel", "Tunnel"):
        counts_a[c], _ = safe("%s count(%r) after" % (tag, c), lambda cc=c: g.count(TARGET, cc))
    rec["counts_after"] = counts_a
    fact("%s counts %r -> %r (wire_delta %r) - FACT lines, NEVER the acceptance test (Pre-decided 106: "
         "LANDED is SOURCE IDENTITY, never a wired-count delta)"
         % (tag, counts_b, counts_a, (rec["connect"] or {}).get("wire_delta")))

    # ---- (iv) the state the write left, measured but NOT yet asserted (Pre-decided 94).
    s_a = sink_wire_now(row, sink2, hints, tag, "IMMEDIATELY AFTER THE WRITE", phase0)
    rec["sink_after_write"] = s_a
    rec["measurement_after_write"] = acceptance(row, tag, "(a) IMMEDIATELY AFTER THE WRITE - MEASURED, "
                                                          "NOT ASSERTED (Pre-decided 94)", s_a["wire"],
                                                False)

    # ---- (v) the junk purge, then the state the artefact actually keeps.
    _nodes, purge = purge_junk(nodes_before, "%s after the write" % tag, hints)
    rec["purge"] = {"new_uids": purge["new_uids"], "deleted": [d["uid"] for d in purge["deleted"]],
                    "reported_not_deleted": [d["uid"] for d in purge["reported_not_deleted"]]}
    s_b = sink_wire_now(row, sink2, hints, tag, "AFTER THE JUNK PURGE", phase0)
    rec["sink_after_purge"] = s_b
    rec["measurement_after_purge"] = acceptance(row, tag, "(b) AFTER THE JUNK PURGE - MEASURED, NOT "
                                                          "ASSERTED (Pre-decided 94)", s_b["wire"], False)
    rec["result"] = "WRITTEN"
    dump()
    return rec


# ==================================== [5] THE ORDERED SECOND PASS - where the row is ASSERTED
def phase_second_pass(hints, phase0):
    """PRE-DECIDED 94 + 106. Each written row is RE-CONNECTED idempotently in a SEPARATE ORDERED PASS -
    `wire_delta` is expected to be 0 because the connection already exists - and THE ACCEPTANCE IS
    ASSERTED HERE, never in the pass that made the connection. The writer's own `Is Broken?` readback is
    PRINTED by the op wrapper and is REPORTED, never gated (see R['is_broken_policy'])."""
    head("[94] THE ORDERED SECOND PASS - idempotent re-connect, and the ROW ACCEPTANCE IS ASSERTED HERE")
    K["second_pass"] = []
    for row in ROWS:
        tag = "[94 %s]" % row["tag"]
        st = R["rows"].get(row["tag"]) or {}
        rec = {"row": row["tag"]}
        if st.get("result") != "WRITTEN":
            rec["skipped"] = "the row was not written, so there is nothing to re-connect"
            fact("%s SKIPPED - %s" % (tag, rec["skipped"]))
            gate("%s ROW ACCEPTANCE (Pre-decided 85/106) - the row was WRITTEN at all" % tag, False,
                 str(st.get("result"))[:200])
            K["second_pass"].append(rec)
            continue
        sink = resolve_sink(row, hints, "%s re-resolve" % tag, phase0)
        src = resolve_source(row, hints, "%s re-resolve" % tag, expect_bare=False)
        rec["sink"] = {k: sink.get(k) for k in ("sink_diag_index", "sink_nodes_index", "sink_term_index",
                                                "sink_wire_before", "stop")}
        rec["source"] = {k: src.get(k) for k in ("src_diag_index", "src_nodes_index", "src_term_index",
                                                 "stop")}
        if sink.get("stop") or src.get("stop"):
            rec["skipped"] = "an endpoint no longer resolves: %s" % (sink.get("stop") or src.get("stop"))
            fact("%s SKIPPED - %s" % (tag, rec["skipped"]))
            gate("%s ROW ACCEPTANCE (Pre-decided 85/106) - the endpoints still resolve" % tag, False,
                 rec["skipped"][:200])
            K["second_pass"].append(rec)
            continue
        wires_before, _ = safe("%s count('Wire') before" % tag, lambda: g.count(TARGET, "Wire"))
        writer = WRITERS[row["sink_kind"]][0]
        try:
            dw, es, err = writer(TARGET, sink["sink_diag_index"], sink["sink_nodes_index"],
                                 sink["sink_term_index"], src["src_diag_index"],
                                 src["src_nodes_index"], src["src_term_index"],
                                 CONNECT_NESTED_LABELS)
            rec.update({"wire_delta": dw, "exec_state": es, "op_error": str(err)[:250]})
        except Exception as e:                                                     # noqa: BLE001
            rec["call_error"] = "%s: %s" % (type(e).__name__, str(e)[:250])
            defect("%s idempotent re-connect" % tag, e)
            K["second_pass"].append(rec)
            continue
        wires_after, _ = safe("%s count('Wire') after" % tag, lambda: g.count(TARGET, "Wire"))
        rec["wire_census"] = [wires_before, wires_after]
        rec["idempotent"] = (rec.get("wire_delta") == 0)
        fact("%s IDEMPOTENT RE-CONNECT: wire_delta %r (expected 0 - the connection already exists) ; "
             "Wire census %r -> %r ; op error %r"
             % (tag, rec.get("wire_delta"), wires_before, wires_after, rec.get("op_error")))
        if not rec["idempotent"]:
            fact("%s *** wire_delta is NOT 0, so this pass CHANGED the diagram instead of re-reading it. "
                 "That is REPORTED; the junk census runs and the acceptance below is still measured on "
                 "the state the artefact now holds. ***" % tag)
            nodes_now, _ = M.node_census(TARGET, "%s after a non-idempotent re-connect" % tag)
            purge_junk(nodes_now, "%s re-connect" % tag, hints)
        now = sink_wire_now(row, sink, hints, tag, "AT THE ORDERED SECOND PASS", phase0)
        rec["sink_now"] = now
        acc = acceptance(row, tag, "(c) THE ORDERED SECOND PASS - THIS IS THE ASSERTION", now["wire"],
                         True)
        rec["acceptance"] = acc
        gate("%s IDEMPOTENT (wire_delta 0 on the ordered second pass, Pre-decided 94)"
             % tag, rec["idempotent"], "wire_delta %r" % rec.get("wire_delta"))
        K["second_pass"].append(rec)
        dump()
    return K["second_pass"]


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
    print("=== build_d1_m3a3  %s  - STAGE **M3a-3b: ROW D ALONE** (Pre-decided 104-111). ROW C IS ALREADY "
          "IN THE BED AND IS NOT REDONE - it is asserted read-only at [C0]." % STAMP, flush=True)
    print("=== THE ARTEFACT THIS RUN SAVES IS **NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL**, IS BROKEN "
          "BY DESIGN AND IS NEVER RUN (34(f), Pre-decided 97).", flush=True)
    print("=" * 100, flush=True)
    hints = [TOP]
    phase0 = {"verdict": "NOT REACHED"}
    try:
        phase_files()
        hints = phase_copy()
        pre = phase_precondition_rowc(hints)
        if pre.get("verdict") != "HOLDS":
            raise Halt("ROW C's PRECONDITION FAILED (%s). The bed is not the artefact this stage was "
                       "told it is, so NOTHING is deleted and Row D is not attempted. A stage never "
                       "repairs its own input." % pre.get("verdict"))
        phase0 = phase0_resolve_tunnel(hints)
        for row in ROWS:
            if row["sink_kind"] == "tunnel_uid" and phase0.get("verdict") != "HOLDS":
                R["rows"][row["tag"]] = {"result": "ROW D NOT ATTEMPTED - PHASE 0 did not resolve",
                                         "reason": phase0.get("verdict"),
                                         "wire_not_deleted": row["wire"]}
                fact("*** ROW D NOT ATTEMPTED - a FAILED PREDICTION at PHASE 0. Wire %d is NOT deleted, "
                     "no address is improvised for #%d, and there is no GUI fallback. ***",
                     row["wire"], row["sink_uid"])
                continue
            if left_s() < ROW_MIN_S:
                fact("HALTED before row %s: only %.0f s left before the reserve; a row needs %.0f s"
                     % (row["tag"], left_s(), ROW_MIN_S))
                R["rows"][row["tag"]] = {"result": "NOT RUN - no wall-clock left"}
                gate("[ROW %s] ROW WRITTEN AT ALL" % row["tag"], False, "no wall-clock left")
                break
            one_row(row, hints, phase0)
        phase_second_pass(hints, phase0)
        K["counts_final"] = counts("[F] final, in memory")
        # THE STAGE ALWAYS LEAVES A FILE (Pre-decided 96) - but only when there is something IN it.
        # A byte-identical copy of the bed under a new stage name is not an artefact, it is a decoy:
        # it would pass "a file exists" and fail S1, and a later session could mistake it for a bed.
        if any((R["rows"].get(r["tag"]) or {}).get("result") == "WRITTEN" for r in ROWS):
            phase_save()
        else:
            fact("[S] NO ARTEFACT IS SAVED: no row was WRITTEN, so the in-memory copy is byte-identical "
                 "to the bed. A copy under a new stage name would be a DECOY bed, not a stage output. "
                 "The bed %s (md5 %s) remains the current bed.",
                 os.path.basename(INPUT), INPUT_MD5[:8])
            gate("S0 A ROW WAS WRITTEN, so there is something to save", False,
                 "rows: %r" % ({t: (v or {}).get("result") for t, v in R["rows"].items()},))
    except Halt as e:
        fact("HALTED: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        # Pre-decided 100 SS2: OUR bug, NOT a machine refusal. `refusal()` is not called here.
        import traceback
        R["unexpected_exception"] = traceback.format_exc()[-2500:]
        defect("main", e)
    finally:
        head("[H] HYGIENE - panels closed, the md5 pins AFTER, the tool pins, the refs and the handles")
        safe("close_panel(TARGET)", lambda: g.close_panel(TARGET))
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
        gate("H8 no mutator call was REFUSED BY THE MACHINE (this file's refusals and the imported "
             "helpers'; a Python exception of OURS is NOT one - it is H9)", not refusals and not imported,
             "%d machine refusal(s) here %r ; %d in the imported helpers %r"
             % (len(refusals), [r["where"] for r in refusals], len(imported),
                [r.get("where") for r in imported]))
        gate("H9 NO DEFECT IN OUR OWN PYTHON CODE - no exception was raised by this script itself "
             "(a bug of ours is NEVER a machine refusal)", not defects,
             "%d our-code defect(s): %r"
             % (len(defects), [("%s at %s: %s" % (d["exception_type"], d["source_line"], d["where"]))
                               for d in defects]))
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
