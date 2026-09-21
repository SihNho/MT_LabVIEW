"""diag_c66b_s3b_m3 - cycle 66 material #3, PART B: STAGE S3b-M3 **AMENDED** on the S3b row-2 bed.

WHAT IS AMENDED vs `tools/bench/diag_c66_s3b_m3.py` (dispatch #2, `BGRUN END rc=1`, 32 pass / 5 fail):
  1. THE MOVE SET IS **SEVEN** OBJECTS, not five: the five loop-1.5 nodes PLUS the two Local variables
     `#23499` and `#23523`, all into `#23032`'s body `Diagram #23058`, ONE `move_in` per object. `#10407`
     moves while both Locals sit on `Diagram #639`, so leaving them behind makes rows 1 and 2 CROSS-DIAGRAM
     and `connect_nested_v1` addresses one nested diagram only. A Local binds to its front-panel control BY
     LABEL, not by wire, so relocating one changes no data path: a pure SCHEDULING change (rule 1a).
  2. GATE `E5` IS REPAIRED. Dispatch #2 read the brief's "(59, 48)" for `#637` as a POSITION and failed on it;
     it is **59 TERMINALS / 48 WIRED**. The machine's position, (2633, 927), is now a FACT, never a gate.
  3. ABORT CLAUSE `A2` IS RE-SCOPED. It fired on wires 23540 / 23502 whose sinks are `#10407`'s OWN case
     tunnels - the very connection rows 1 and 2 were built to make. It now fires only if a watched wire has
     **more than one sink**, or a sink other than the terminal its row was built to feed.
  4. ABORT CLAUSE `A1` AND STAGE `P3` ARE RETIRED. The data-type read was MEASURED unreachable in dispatch #2
     with eight named wrapped properties (`diag_c66_s3b_m3.log:133`, `TYPE READ UNREACHABLE`). It is NOT
     re-attempted here; the factual question is being pursued in the Part A peer dispatch. A scheduling move
     changes no data types, so this stage does not depend on it. `P2` (four `owner_of` calls) is likewise not
     repeated - it was answered in dispatch #2 and was never a gate (53(d^8)).
  5. TWO MORE ROWS ARE NOW ADDRESSABLE and are re-wired: `#10407` t0 from Local `#23499` and `#10407` t2 from
     Local `#23523`. Dispatch #2 listed them as NOT ATTEMPTED with the reason "CROSS-DIAGRAM after the move" -
     moving the Locals is exactly what removes that reason.

THE PEER REVIEW THAT CLEARED THE BUILD GATE, AND WHAT IT CHANGED HERE. `archive/peer/2026-09-21-c66-m3-
movelocals.md` (claude / hypothesis, opus / effort max, ANSWERED 628 s) **REFUTED Claim 1** - it argues the
seven-object move set is a COMPUTATION change, not a scheduling one (sampling rate, race semantics, first-
iteration value) - and reported that the data-type read IS reachable via `Terminal.Coercion Dot?` 634A006 and
`Terminal.Data Type` 634A008. Both are ROUTE CHANGES and both are a rule-1a / design call, so they are QUOTED
VERBATIM AND NOT ACTED ON in that file's `## What was done with it`, and carried to judgement. What WAS taken
mechanically, because none of it changes the route: the A2 whitelist now covers the **SOURCE** side as well as
the sink (the peer's one concrete objection to the re-scoping); the `Tunnel` subclass arithmetic it disputed is
now PRINTED rather than assumed; `#10407`'s full terminal table is dumped so "is t0 or t2 the case selector" is
answerable from this run's record; and the limit of `wire_source_owner`'s branch detection is written into the
log as a FACT instead of being glossed.

WHAT ALREADY EXISTS, CHECKED BEFORE A LINE OF THIS FILE WAS WRITTEN (CLAUDE.md: most of this project's cost has
been rebuilding what it already owned):
  - `grep "^def " tools/gscript.py` - every verb this file needs is ALREADY THERE: `exec_state`, `count`,
    `report_all`, `node_labels`, `node_terms_uid`, `panel_wiring`, `delete_object`, `save`, `close_panel`,
    `ref_counts`. NO new verb, NO new op, NO edit to tools/gscript.py, NO edit to any *_astcheck.py gate file,
    NO recipe written.
  - `tools/recipes/build_d1_v0.py:318` `move_in` / `:338` `owner_of` / `:357` `diag_index` - THE BUILT MOVER and
    the two uid-addressed readers. `move_in` is not in gscript at all.
  - `tools/recipes/build_opconnectnested_v1.py:418` `connect_nested_v1` - the BUILT node->node writer for two
    nodes on ONE nested diagram, and the fleet's only ordered `Broken?` reader.
  - `tools/recipes/build_opconnectfromwire_v0.py:423` `wire_source_owner` - `OpWireSource_v5`, the ONLY BY-UID
    walk of a WIRE's own `Terms[]`, giving each terminal's OWNER class and uid. This is what A2 reads.
  - `tools/bench/diag_c66_s3b_m3.py` / `tools/bench/diag_c65_s3b_row2c.py` / `tools/bench/diag_s3_focus_trial.py`
    (cycle 54, the only prior end-to-end run of the moves and the re-wiring) - every helper below is reused IN
    SHAPE from them, and cycle 54's `SET` drop positions and `INTERNAL_JOBS` are reused verbatim in value with
    every address RE-RESOLVED off this bed.
  - `tools/bench/c60c_astcheck.py` - the static gate, run with `--route movein` on THIS file before launch.
    NOT edited.

PREDICTION CONTRACT (machine-checkable; a failed prediction is reported, never explained away)
  E   THE BED re-measured COLD: ExecState 1 / Wire 1907 / Node 632 / ControlTerminal 116 / Local 10 /
      LoopTunnel 135 / Tunnel 471 / `Diagram #639` = traverse index 46 with 75 nodes / `#637` = 59 terminals,
      48 WIRED. Each is a GATE against the value MEASURED here, never against the recorded constant.
  P1  (a) the tunnel-family class census, REPORTED (Tunnel 471 = LoopTunnel 135 + ConditionalTunnel 146 +
      SelectorTunnel 146 + 36/36 shift registers, per dispatch #2). (b) EVERY node of `Diagram #639` gets
      `node_terms_uid`; every terminal carrying 23556 / 23540 / 23502 is recorded with its node's class.
      (c) the same three wires walked BY UID with `wire_source_owner`.
  A2  RE-SCOPED, and the ONLY abort. For each watched wire: the SINK endpoints are the `Terms[]` rows with
      `is_source` False and a non-zero owner uid. A2 fires iff any watched wire has MORE THAN ONE sink, or its
      sink is not the terminal its row was built to feed:
        23556 -> the row-2 indicator's control terminal, whose owner uid is `Diagram #639`
        23540 -> a terminal of `#10407` at t2   (cross-checked against the P1b scan)
        23502 -> a terminal of `#10407` at t0   (cross-checked against the P1b scan)
      A sink on `#10407`'s OWN case tunnel is the INTENDED wiring and is NOT an abort. On A2: stop before the
      first `move_in`, save no `.vi`, remove the working copy, report.
  M1  SEVEN `move_in` CALLS, ONE OBJECT PER CALL, destination index RE-RESOLVED by uid immediately before each
      (38(e)); after EVERY call the whole-VI `Node` census is diffed and any new ZERO-WIRED `Invoke` is deleted
      BY UID with `gone` confirmed (55(c)). NEVER after `wire_indicators` (56(e)) - which this file does not
      call at all. PREDICTION: all seven appear in `Diagram #23058`'s `Nodes[]`; `move_in` SEVERS every wire on
      the moved object (37(d)), so wired-terminal counts fall to 0 and `ExecState` goes to 0.
  M2  SEVEN ROWS, each addressed off the machine (by terminal NAME where the name is non-empty and unique, by
      the RE-MEASURED index otherwise) and written with `connect_nested_v1`; census + purge after every call.
      Rows are matched by WIRED-TERMINAL counts, never by a Wire-class count (37(e)/49(e)).
      REPORTED, NOT ATTEMPTED, with their reason: the three shift-register rows and the from-tunnel row.
  SAVE  MECHANICAL INTERMEDIATE SAVES (the user's 2026-09-19 split rule, a standing instruction not a branch):
      an object WITH ITS OWN SEVERED ROWS RE-WIRED is one unit; at every unit boundary `ExecState` is read and,
      WHENEVER IT READS 1, the file is saved as `claudeDev\\D1_s3b_m3_u<k>_<stamp>.vi` and its md5 recorded.
      `dump()` writes the JSON after every step, so a run that dies still leaves a file.
  Z   THE PASS CRITERION for the final save: all seven moved uids appear in `Diagram #23058`'s `Nodes[]` census
      (THE authoritative gate; `owner_of` on the seven is reported ALONGSIDE, never as it - 53(d^8)) AND
      `ExecState` 1 => save `claudeDev\\D1_s3b_m3_moved_<stamp>.vi`, then LabVIEW RESTART + COLD reopen and read
      `ExecState` again. Both values reported.
  Y   md5 pins hold BEFORE and AFTER: ORIGINAL 2a78e17c / D1_s1_copy 3e3d23ce / D1_s2_loops 6ff19497 /
      D1_s3a_focus_ind eef91c1d / row 1 c7094f98 and 72f0d47d / THE BED 26c54ff7 (476,759 B).
      Every scratch `exists=False` at the end; refs opened == closed == 0 live; handles either side.

38(g) stays banned. No `allow_broken`, no `gui_save`, no `g.open_panel`, no GUI, no new op, no new verb, no cast,
no splice (51(h)), no recipe, no `CYCLE_GUARD_OFF`. `retrospective.py` / `audit_cycle.py` / `violations.py` /
`doc_ingest.py` / `prior_art_review.py` are NOT run (54(a)). No route is chosen and none is recommended;
`docs/cycle27-plan.md` and STATUS's `## NEXT` are untouched.
VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)). Rig ASSEMBLED: no motor, no ASI, no camera, no VI run.
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
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index, move_in, owner_of                              # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS             # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
ROW1A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_row1a_20260921_135932.vi")
ROW1A_MD5 = "c7094f98324af3bb53755fef718f8e28"
ROW1_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_20260921_135932.vi")
ROW1_MD5 = "72f0d47d0b1cbd0834d50f1483e558c1"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
BED_SIZE = 476759

TOP = 0
D639 = 639                       # the nested diagram the 1.5 set lives on today
D639_RECORDED = 46
D639_NODES_RECORDED = 75
LOOP_A_UID = 23032               # 37(h) / docs/cycle27-plan.md:1127-1129 - CITED, never re-derived.
BODY_A_UID = 23058               # the destination diagram. NOTE :1037's `Obtain Queue #23032` is a DIFFERENT
                                 # object reusing the uid - it is not this loop.
LOOP11_UID = 637
LOOP637_TERMS_RECORDED = 59      # 59 TERMINALS / 48 WIRED. NOT a position - dispatch #2's E5 read it as one.
LOOP637_WIRED_RECORDED = 48

SRC_UID = 10757                  # row 2's SOURCE node, an `Index Array`
CASE_UID = 10407                 # the CaseStructure both Local rows feed
IND_CONTROL_UID = 23525          # row 2's indicator, panel control uid
LOCAL_ROW1_UID = 23499           # row 1's Local carrier
LOCAL_ROW2_UID = 23523           # row 2's Local carrier
ROW2_WIRE = 23556                # row 2's NEW net: #10757 t1 -> the indicator's control terminal
ROW2_LOCAL_WIRE = 23540          # Local #23523 -> #10407 t2
ROW1_WIRE = 23502                # Local #23499 -> #10407 t0
WATCH_WIRES = (ROW2_WIRE, ROW2_LOCAL_WIRE, ROW1_WIRE)

# A2 RE-SCOPED, AND WRITTEN BEFORE THE RUN AS A WHITELIST ON **BOTH** SIDES. The peer review
# `archive/peer/2026-09-21-c66-m3-movelocals.md` conceded the original clause was unsatisfiable for the rows it
# guards, then objected that a sink-only replacement "drops the SOURCE side entirely - at the stage that creates
# source-side branches". So both ends are whitelisted here, as constants, before a single object moves.
# ("diagram", uid) means that endpoint's owner uid is that diagram (a front-panel control terminal reports its
# diagram as its owner); ("node_term", uid, t) means the endpoint must be a terminal of that node at that index,
# cross-checked against the P1b scan of #639; ("node", uid) means the endpoint's owner IS that object.
EXPECTED_SINK = {
    ROW2_WIRE:       ("diagram", D639),
    ROW2_LOCAL_WIRE: ("node_term", CASE_UID, 2),
    ROW1_WIRE:       ("node_term", CASE_UID, 0),
}
EXPECTED_SOURCE = {
    ROW2_WIRE:       ("node", SRC_UID),
    ROW2_LOCAL_WIRE: ("node", LOCAL_ROW2_UID),
    ROW1_WIRE:       ("node", LOCAL_ROW1_UID),
}

# The baseline this brief RECORDED. Every gate below is computed from the value MEASURED at step [E], never
# from these; they exist so a drift is VISIBLE.
BASE = {"Node": 632, "Wire": 1907, "ControlTerminal": 116, "Local": 10, "LoopTunnel": 135}
BASE_TUNNEL = 471

# THE MOVE SET - SEVEN objects. The five loop-1.5 nodes carry cycle 54's drop positions
# (diag_s3_focus_trial.py:133-139); the two Locals are dropped clear of them inside the same body.
SET = [
    (3529, "- Inc (PgDn)", (40, 60), "ControlReferenceConstant; docs/d1-build-plan.md:330"),
    (3560, "+ Inc (PgUp)", (40, 170), "ControlReferenceConstant; docs/d1-build-plan.md:331"),
    (3447, "Focus Step (F1)", (40, 280), "ControlReferenceConstant; docs/d1-build-plan.md:332"),
    (48, "ASI_adjust focus-subvi.vi", (300, 170), "SubVI; docs/d1-build-plan.md:306"),
    (10407, "Case Structure", (620, 60), "CaseStructure (autofocus); docs/d1-build-plan.md:305"),
    (LOCAL_ROW1_UID, "Local (row 1 carrier)", (40, 430),
     "Local; binds to its control BY LABEL, so the move is scheduling only (rule 1a)"),
    (LOCAL_ROW2_UID, "Local (row 2 carrier)", (40, 520),
     "Local; binds to its control BY LABEL, so the move is scheduling only (rule 1a)"),
]
SET_UIDS = [u for u, _n, _p, _e in SET]

# THE ROWS. The five INTERNAL rows are cycle 54's (diag_s3_focus_trial.py:143-149, actions same-loop /
# source-side in c53_row_class.json). The two LOCAL rows are the ones dispatch #2 listed as NOT ATTEMPTED
# because they were cross-diagram; moving the Locals is what makes them addressable.
# (sink_uid, sink_name, sink_t, src_uid, src_name, src_t, evidence)
INTERNAL_JOBS = [
    (48, "-Inc reference", 0, 3529, "- Inc (PgDn)", 0, "w4833; c53_row_class.json :1919 / :2096"),
    (48, "+Inc reference", 1, 3560, "+ Inc (PgUp)", 0, "w2819; d1_rewire_sources.json:1946 / :2126"),
    (48, "Focus inc reference", 2, 3447, "Focus Step (F1)", 0, "w1893; d1_rewire_sources.json:1973 / :2156"),
    (10407, "Outgoing Handle", 3, 48, "Outgoing Handle", 6, "w11232; d1_rewire_sources.json:1820 / :2066"),
    (10407, "Out position", 5, 48, "Out position", 5, "w7388; d1_rewire_sources.json:1865 / :2036"),
    (10407, "", 0, LOCAL_ROW1_UID, "", 0,
     "row 1; wire 23502 measured this run at #10407 t0 and at Local #23499 t0"),
    (10407, "index", 2, LOCAL_ROW2_UID, "index", 0,
     "row 2; wire 23540 measured this run at #10407 t2 and at Local #23523 t0"),
]

# REPORTED, NOT ATTEMPTED. Named here so the omission is explicit and machine-readable, never silent.
NOT_ATTEMPTED = [
    {"row": "SR VISA RightIn  #10407 'VISA out' t4", "verb": "gscript.add_shift_reg + wire_sr",
     "why": "creating a shift-register pair is a CREATION, not an 'internal row'; the brief named only the "
            "internal rows and 49(e)'s M3 text names no register"},
    {"row": "SR VISA LeftIn   #48 'VISA resource name' t3", "verb": "gscript.add_shift_reg + wire_sr",
     "why": "same - the left side cannot be written before the pair exists"},
    {"row": "SR POSITION LeftIn #48 'In position' t4", "verb": "gscript.add_shift_reg + wire_sr",
     "why": "same"},
    {"row": "from-tunnel      #10407 '# slices in stack' t1", "verb": "OpConnectFromWire_v0",
     "why": "a TUNNEL write, not an internal node->node row; the brief names the internal rows only"},
]

SCAN_LIMIT = 140
RUN_DEADLINE_S = 40 * 60.0       # the bgrun --max-min this file is launched under
RESERVE_S = 420.0                # held back for the final save, the restart and the cold reopen
M3_MIN_S = 540.0                 # M3 is not started with less than this left before the reserve
ROW_MIN_S = 150.0                # a row is not started with less than this left before the reserve

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c66b_s3b_m3.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

WORK = os.path.join(g.CLAUDEDEV, "WORK_C66BM3_%s.vi" % STAMP)
FINAL_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_m3_moved_%s.vi" % STAMP)

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 66 material #3 PART B: STAGE S3b-M3 AMENDED - SEVEN move_in calls into Diagram #23058 "
             "(five loop-1.5 nodes + Locals #23499/#23523) plus the seven internal rows, on the S3b row-2 bed, "
             "gated by the RE-SCOPED abort clause A2 only",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "bed": {"path": BED, "md5_pin": BED_MD5, "size_pin": BED_SIZE,
             "never_overwritten": "the bed is only ever READ; all work is on WORK, a fresh stamped name"},
     "a1_retired": "the data-type read was MEASURED unreachable in dispatch #2 with eight named wrapped "
                   "properties (diag_c66_s3b_m3.log:133). It is NOT re-attempted; a scheduling move changes no "
                   "data types. The factual question is in the Part A peer dispatch.",
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "no_open_panel_call_in_this_file": True, "no_property_id_guessed": True,
     "gscript_not_edited": True, "no_astcheck_gate_file_edited": True, "no_gui_action": True,
     "wire_indicators_not_called": True,
     "allow_broken": "NEVER True", "gui_save": "NEVER called",
     "remove_bad_wires_scripted": "not imported, not called",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "purges": [], "stage_p": {}, "build": {}, "not_attempted": NOT_ATTEMPTED}
K = R["build"]
P = R["stage_p"]


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    # `FAIL`, NOT `**FAIL**` (37(i)): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        dump()
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


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["elapsed_s"] = round(time.time() - T_START, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T_START) - RESERVE_S


def safe(label, fn, default=None):
    """Run one read, record its error VERBATIM, never let it kill the run."""
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def read_es(tag, target):
    t0 = time.time()
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    row = {"step": len(R["exec_state_timeline"]) + 1, "tag": tag,
           "target": os.path.basename(target), "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    fact("ExecState [%02d %s] = %r   (+%.1f s, read cost %.2f s)"
         % (row["step"], tag, es, row["t_since_start_s"], row["read_cost_s"]))
    return es


def counts(path, tag, classes=("Node", "Wire", "ControlTerminal", "Local", "LoopTunnel", "Tunnel")):
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    K.setdefault("censuses", {})[tag] = rec
    fact("%s counts: %r" % (tag, rec))
    return rec


def node_census(path, tag):
    rows, err = safe("%s report_all('Node')" % tag, lambda: g.report_all(path, "Node"), [])
    out = [{"i": r["i"], "uid": r["uid"], "class": r["class"], "pos": r["pos"], "owner_class": r["owner"]}
           for r in (rows or [])]
    fact("%s node census: %d rows%s" % (tag, len(out), ("  [%s]" % err) if err else ""))
    return out, err


def new_nodes(before, after):
    seen = {n["uid"] for n in before}
    return [n for n in after if n["uid"] not in seen]


def terms_at(path, diagram_index, nodes_index, expect_uid, tag, quiet=False):
    """The FULL terminal table of one node, with the node's own uid echoed back before it is believed."""
    rec = {"diagram_index": diagram_index, "nodes_index": nodes_index, "expected_uid": expect_uid}
    try:
        echo, rows = g.node_terms_uid(path, int(diagram_index), int(nodes_index))
        rec["uid_echo"] = echo
        rec["ok"] = (expect_uid is None) or (echo == expect_uid)
        rec["terminals"] = [{"i": t["i"], "name": t["name"], "is_source": t["is_source"], "wire": t["wire"],
                             "has_wire": bool(t["wire"]),
                             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]}
                            for t in rows]
    except Exception as e:                                                         # noqa: BLE001
        rec["ok"] = False
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        rec["terminals"] = []
    if not quiet:
        fact("%s terminal table of #%s (Diagram idx %r, Nodes[%r], echo %r): %d terminal(s)"
             % (tag, expect_uid, diagram_index, nodes_index, rec.get("uid_echo"), len(rec["terminals"])))
        for t in rec["terminals"]:
            fact("    %s t%-2d %-34r is_source=%-5r wire=%-7r errs=%r"
                 % (tag, t["i"], t["name"], t["is_source"], t["wire"], t["errs"]))
    return rec


def term_state(t):
    """WIRED / BARE / UNREAD for ONE terminal row (Pre-decided 14; gscript.py:874 gives the one legitimate
    bare-terminal error pattern: wire 0 with conn_err/wire_err 1055 and name_err/src_err 0)."""
    ne, se, ce, we = [int(x or 0) for x in t.get("errs", [0, 0, 0, 0])]
    if t.get("wire"):
        return "UNREAD" if (ne or se or ce or we) else "WIRED"
    if ne or se:
        return "UNREAD"
    if (ce and ce != 1055) or (we and we != 1055):
        return "UNREAD"
    return "BARE"


def wired_count(rows):
    return sum(1 for t in rows if term_state(t) == "WIRED")


def find_node(path, uid, hints, tag, budget_s=240.0, quiet=False):
    """Which DIAGRAM lists `uid` in its Nodes[] - answered by the census that finds it, NEVER by owner_of
    (owner_of is measured to answer with the PREVIOUS query's object, silently; Pre-decided 53(d^8))."""
    t0 = time.time()
    rec = {"uid": uid, "hints": list(hints), "scanned": [], "found": None}
    diags, derr = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(path, "Diagram"), [])
    rec["diagram_rows"] = len(diags or [])
    rec["diagram_census_error"] = derr
    by_index = {d["i"]: d for d in (diags or [])}
    order = [i for i in hints if isinstance(i, int) and i in by_index]
    order += [i for i in sorted(by_index) if i not in order]
    for i in order:
        if time.time() - t0 > budget_s:
            rec["scan_stopped"] = "budget %.0f s reached after %d diagrams" % (budget_s, len(rec["scanned"]))
            break
        rows, err = safe("%s node_labels(%d)" % (tag, i), lambda k=i: g.node_labels(path, k), [])
        rec["scanned"].append({"diagram_index": i, "diagram_uid": by_index[i]["uid"],
                               "nodes": len(rows or []), "error": err})
        hit = next((k for k, r in enumerate(rows or []) if r["uid"] == uid), None)
        if hit is not None:
            rec["found"] = {"diagram_index": i, "diagram_uid": by_index[i]["uid"],
                            "diagram_class": by_index[i]["class"], "nodes_index": hit,
                            "nodes_on_diagram": len(rows), "label": rows[hit]["label"]}
            break
    rec["scan_cost_s"] = round(time.time() - t0, 1)
    if not quiet:
        fact("%s #%s lives at: %r  (%d diagram(s) scanned of %d, %.1f s)"
             % (tag, uid, rec["found"], len(rec["scanned"]), rec["diagram_rows"], rec["scan_cost_s"]))
    return rec


def node_view(path, uid, hints, tag, quiet=False):
    loc = find_node(path, uid, hints, tag, quiet=quiet)
    f = loc.get("found") or {}
    if f.get("nodes_index") is None:
        return loc, []
    tt = terms_at(path, f["diagram_index"], f["nodes_index"], uid, tag, quiet=quiet)
    loc["uid_echo"] = tt.get("uid_echo")
    loc["terminal_table"] = tt
    return loc, tt.get("terminals", [])


def delete_by_uid(path, cls, uid, tag):
    """report_all(cls) -> .index(uid) -> delete_object(cls, idx). The shape cycle 58 used; no new verb."""
    rec = {"class": cls, "uid": uid}
    rows, err = safe("%s report_all(%r) before delete" % (tag, cls), lambda: g.report_all(path, cls), [])
    rec["census_before"] = len(rows or [])
    rec["census_error"] = err
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    rec["index"] = idx
    if idx is None:
        rec["result"] = "NOT IN THE %s CENSUS (%d rows) - nothing deleted" % (cls, len(rows or []))
        fact("%s delete %s #%s: %s" % (tag, cls, uid, rec["result"]))
        return rec
    t0 = time.time()
    try:
        gone = g.delete_object(path, cls, idx, verify=True)
        rec["gone"] = sorted(int(x) for x in (gone or []))
        rec["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["gone"] = None
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    rec["call_cost_s"] = round(time.time() - t0, 2)
    after, _ = safe("%s report_all(%r) after delete" % (tag, cls), lambda: g.report_all(path, cls), [])
    rec["census_after"] = len(after or [])
    rec["still_present"] = any(r["uid"] == uid for r in (after or []))
    fact("%s delete %s #%s at index %r: gone %r, error %r, census %r -> %r, still present %r (%.2f s)"
         % (tag, cls, uid, idx, rec.get("gone"), rec.get("error_verbatim"), rec["census_before"],
            rec["census_after"], rec["still_present"], rec.get("call_cost_s", 0.0)))
    return rec


def census_and_purge(path, nodes_before, tag, hints, keep_uids=()):
    """55(c): after EVERY move_in and EVERY connect_nested_v1, diff the whole-VI Node census and purge the junk
    BY UID. A new node is DELETED only when it is an `Invoke` with ZERO wired terminals (the measured junk
    shape). Anything else is REPORTED VERBATIM and left alone; an `Invoke` whose terminal table could NOT be
    read is never deleted and stops the build instead. NEVER called after `wire_indicators` (56(e)) - which
    this file does not call at all."""
    nodes_after, _ = node_census(path, "%s AFTER" % tag)
    fresh = new_nodes(nodes_before, nodes_after)
    rec = {"tag": tag, "node_count_before": len(nodes_before), "node_count_after": len(nodes_after),
           "new_uids": [(n["uid"], n["class"], n["pos"]) for n in fresh],
           "kept": list(keep_uids), "deleted": [], "reported_not_deleted": []}
    fact("%s CENSUS DIFF: Node %d -> %d ; %d new uid(s): %r"
         % (tag, len(nodes_before), len(nodes_after), len(fresh), rec["new_uids"]))
    for n in fresh:
        if n["uid"] in keep_uids:
            fact("%s new node #%s (%s) is INTENDED by this build - kept" % (tag, n["uid"], n["class"]))
            continue
        loc, rows = node_view(path, n["uid"], hints, "%s new #%s" % (tag, n["uid"]))
        wired = [t for t in rows if t.get("has_wire")]
        entry = {"uid": n["uid"], "class": n["class"], "pos": n["pos"],
                 "label": (loc.get("found") or {}).get("label"),
                 "diagram_index": (loc.get("found") or {}).get("diagram_index"),
                 "diagram_uid": (loc.get("found") or {}).get("diagram_uid"),
                 "terminals": rows, "n_terminals": len(rows), "n_wired": len(wired)}
        if n["class"] == "Invoke" and rows and not wired:
            fact("%s THE JUNK NODE'S FULL TERMINAL TABLE IS PRINTED ABOVE; %d terminal(s), %d WIRED - the "
                 "purge precondition (ZERO wired) HOLDS" % (tag, len(rows), len(wired)))
            entry["delete"] = delete_by_uid(path, "Node", n["uid"], "%s purge" % tag)
            rec["deleted"].append(entry)
        elif n["class"] == "Invoke" and not rows:
            rec["reported_not_deleted"].append(entry)
            fact("%s AN `Invoke` NEW NODE #%s COULD NOT BE LOCATED OR READ - IT IS NOT DELETED. Deleting a "
                 "node whose table was never read is the one branch that could destroy the artefact."
                 % (tag, n["uid"]))
        else:
            rec["reported_not_deleted"].append(entry)
            fact("%s NEW NODE NOT DELETED (not the measured junk shape): #%s class %r label %r, %d "
                 "terminal(s), %d wired - REPORTED, left alone"
                 % (tag, n["uid"], n["class"], entry["label"], entry["n_terminals"], entry["n_wired"]))
    if rec["deleted"]:
        final, _ = node_census(path, "%s AFTER THE PURGE (the next step's baseline)" % tag)
        gate("%s purge: the Node census returns to its pre-call value %d" % (tag, len(nodes_before)),
             len(final) == len(nodes_before), "%d -> %d -> %d"
             % (len(nodes_before), len(nodes_after), len(final)))
    else:
        final = nodes_after
    rec["node_count_after_purge"] = len(final)
    R["purges"].append(rec)
    dump()
    return final, rec


def panel_all(path, tag):
    rows, err = safe("%s panel_wiring" % tag, lambda: g.panel_wiring(path), [])
    fact("%s panel_wiring: %d rows%s" % (tag, len(rows or []), (" ; ERROR " + err) if err else ""))
    return rows or [], err


def save_artefact(tag, dest, not_equal_to, not_equal_label):
    """g.save writes the WORKING copy in place; the artefact is a fresh path LabVIEW has never seen.
    A file byte-identical to its predecessor means THE IN-MEMORY EDITS DID NOT LAND - reported as a FAILURE."""
    rec = {"tag": tag, "dest": dest, "save_error_verbatim": ""}
    rec["exec_state_at_save"] = read_es("%s immediately before the save" % tag, WORK)
    try:
        rec["save_returned_size"] = g.save(WORK)
    except Exception as e:                                                         # noqa: BLE001
        rec["save_returned_size"] = None
        rec["save_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    try:
        shutil.copy2(WORK, dest)
        rec["copy_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["copy_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    ff = D.file_facts("%s the artefact" % tag, dest)
    rec.update({"exists": bool(ff.get("exists")), "md5": ff.get("md5"), "size": ff.get("size"),
                "version_candidates": ff.get("version_candidates")})
    rec["compared_against"] = not_equal_label
    rec["bytes_equal_to_the_predecessor"] = (ff.get("md5") == not_equal_to)
    R["artefacts_on_disk"].append(rec)
    fact("%s FILE ON DISK: %s  md5 %r  size %r  (ExecState at the save %r ; COM save error %r ; bytes equal "
         "to %s %r)" % (tag, dest, rec["md5"], rec["size"], rec["exec_state_at_save"],
                        rec["save_error_verbatim"], not_equal_label,
                        rec["bytes_equal_to_the_predecessor"]))
    gate("%s *** A FILE IS ON DISK at %s ***" % (tag, os.path.basename(dest)), bool(rec["exists"]),
         "md5 %r size %r" % (rec["md5"], rec["size"]))
    gate("%s that file is NOT byte-identical to %s (the in-memory edits LANDED)" % (tag, not_equal_label),
         bool(rec["exists"]) and not rec["bytes_equal_to_the_predecessor"] and not rec["save_error_verbatim"],
         "md5 %r vs %s %r ; save error %r"
         % (rec["md5"], not_equal_label, not_equal_to, rec["save_error_verbatim"]))
    dump()
    return rec


def unit_boundary(tag):
    """The user's 2026-09-19 split rule, applied MECHANICALLY and not as a branch: read ExecState at every unit
    boundary and, WHENEVER it reads 1, leave a file on disk before the next unit starts."""
    es = read_es("[UNIT] %s" % tag, WORK)
    K.setdefault("unit_boundaries", []).append({"tag": tag, "exec_state": es})
    if es == 1:
        k = sum(1 for a in R["artefacts_on_disk"] if "_u" in os.path.basename(a["dest"])) + 1
        save_artefact("[UNIT %d] %s - ExecState 1 at a unit boundary" % (k, tag),
                      os.path.join(g.CLAUDEDEV, "D1_s3b_m3_u%d_%s.vi" % (k, STAMP)), BED_MD5, "the bed")
    else:
        fact("[UNIT] %s: ExecState %r - NOT 1, so no intermediate file is written at this boundary "
             "(`allow_broken` is never set and `gui_save` is never called)" % (tag, es))
    dump()
    return es


# ======================================================================= PHASE 0 - files only, zero LabVIEW
def phase_0():
    print("\n---------- [0] FILES ONLY, ZERO LabVIEW - the md5 pins BEFORE", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; cycle 66 dispatch #2 ended at 63,539, "
         "so the pre-batch restart below is MANDATORY - 44(e))" % R["handles"]["before"])
    for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy", S1_ARTEFACT, S1_MD5),
                           ("D1_s2_loops", S2_ARTEFACT, S2_MD5), ("D1_s3a_focus_ind", S3A_ARTEFACT, S3A_MD5),
                           ("D1_s3b_row1a", ROW1A_ARTEFACT, ROW1A_MD5),
                           ("D1_s3b_row1", ROW1_ARTEFACT, ROW1_MD5), ("THE BED", BED, BED_MD5)):
        pr = probe("Y %s BEFORE" % tag, path)
        gate("Y %s md5 == its pin %s" % (tag, pin[:8]), pr.get("md5") == pin, "%r" % (pr.get("md5"),))
    pr = probe("Y THE BED size", BED)
    gate("Y the bed is %d B" % BED_SIZE, str(pr.get("size")) == str(BED_SIZE), "%r" % (pr.get("size"),))

    D.fresh("[0] pre-batch LabVIEW restart (44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])
    shutil.copy2(BED, WORK)
    pr = probe("[0] the working copy", WORK)
    gate("[0] the working copy is byte-identical to the bed", pr.get("md5") == BED_MD5, "%r" % (pr.get("md5"),))
    dump()


# ======================================================================= STEP E - the bed's cold baseline
def step_E():
    print("\n---------- [E] THE BED RE-MEASURED COLD - the brief's baseline, echoed before anything else",
          flush=True)
    es = read_es("[E] the bed, COLD", WORK)
    gate("E1 the bed reopens COLD at ExecState 1", es == 1, "%r" % (es,), fatal=True)
    c = counts(WORK, "[E] the bed COLD")
    K["counts_before"] = c
    for k, v in BASE.items():
        gate("E2 %s == %d (the brief's recorded baseline)" % (k, v), c.get(k) == v, "%r" % (c.get(k),))
    gate("E2t Tunnel == %d (the class the previous review called blind; now counted)" % BASE_TUNNEL,
         c.get("Tunnel") == BASE_TUNNEL, "%r" % (c.get("Tunnel"),))

    di, err = safe("[E] diag_index(#%d)" % D639, lambda: diag_index(WORK, D639))
    K["d639_index"] = di
    gate("E3 Diagram #%d resolves to traverse index %d" % (D639, D639_RECORDED), di == D639_RECORDED,
         "%r%s" % (di, (" ; ERROR " + err) if err else ""), fatal=True)
    rows, lerr = safe("[E] node_labels(%r)" % di, lambda: g.node_labels(WORK, di), [])
    K["d639_nodes"] = len(rows or [])
    K["d639_node_uids"] = [r["uid"] for r in (rows or [])]
    gate("E4 Diagram #%d carries %d nodes" % (D639, D639_NODES_RECORDED),
         len(rows or []) == D639_NODES_RECORDED, "%d%s" % (len(rows or []), (" ; " + lerr) if lerr else ""))

    ncen, _ = node_census(WORK, "[E] whole-VI")
    K["node_class_by_uid"] = {str(n["uid"]): n["class"] for n in ncen}
    K["node_census_before"] = ncen
    l637 = next((n for n in ncen if n["uid"] == LOOP11_UID), None)
    K["loop637_census_row"] = l637
    fact("[E] #%d in the whole-VI Node census: %r   <- its POSITION is REPORTED, never gated; dispatch #2's "
         "E5 mistook the brief's terminal/wired pair for a position and failed on it" % (LOOP11_UID, l637))
    hints = [di, TOP]
    _loc, lrows = node_view(WORK, LOOP11_UID, hints, "[E] #%d the WhileLoop" % LOOP11_UID, quiet=True)
    K["loop637_before"] = {"n_terms": len(lrows), "n_wired": wired_count(lrows)}
    fact("[E] #%d (WhileLoop): %d terminals, %d WIRED  <- 37(e)/50(e)'s no-new-tunnel baseline"
         % (LOOP11_UID, len(lrows), wired_count(lrows)))
    gate("E5 #%d has %d TERMINALS and %d WIRED (a count pair, NOT a position)"
         % (LOOP11_UID, LOOP637_TERMS_RECORDED, LOOP637_WIRED_RECORDED),
         len(lrows) == LOOP637_TERMS_RECORDED and wired_count(lrows) == LOOP637_WIRED_RECORDED,
         "%r" % (K["loop637_before"],))
    for uid in (LOCAL_ROW1_UID, LOCAL_ROW2_UID):
        loc, lr = node_view(WORK, uid, hints, "[E] the Local #%d" % uid)
        K.setdefault("locals_before", {})[str(uid)] = {"found": loc.get("found"), "terminals": lr}
        gate("E6 the Local #%d is listed in Diagram #%d's Nodes[] before the move" % (uid, D639),
             (loc.get("found") or {}).get("diagram_uid") == D639, "%r" % ((loc.get("found") or {}),))
    # The peer review asks which of #10407's terminals LabVIEW calls the case SELECTOR - "the run does not
    # settle this and did not ask". The FULL table is dumped here, with existing verbs only, so the question is
    # answerable from this run's own record. REPORTED, never a gate, and no route is chosen from it.
    cloc, crows = node_view(WORK, CASE_UID, hints, "[E] #%d the CaseStructure, FULL terminal table" % CASE_UID)
    K["case_terminals_before"] = {"found": cloc.get("found"), "terminals": crows}
    fact("[E] #%d carries %d terminal(s), %d WIRED; t0 = %r ; t2 = %r  <- REPORTED for the open question "
         "'is t0 or t2 the case SELECTOR' (archive/peer/2026-09-21-c66-m3-movelocals.md); no route is chosen "
         "from it here" % (CASE_UID, len(crows), wired_count(crows),
                           next((t for t in crows if t.get("i") == 0), None),
                           next((t for t in crows if t.get("i") == 2), None)))
    dump()
    return hints


# ======================================================================= P1 - the watched wires, measured
def step_P1(hints):
    print("\n---------- [P1] THE THREE WATCHED WIRES - the evidence the RE-SCOPED A2 reads", flush=True)
    rec = {"watch_wires": list(WATCH_WIRES), "expected_sink": {str(k): list(v)
                                                               for k, v in EXPECTED_SINK.items()}}

    for cls in ("Tunnel", "LoopTunnel", "ConditionalTunnel", "SelectorTunnel",
                "LeftShiftRegister", "RightShiftRegister"):
        rows, err = safe("[P1a] report_all(%r)" % cls, lambda c=cls: g.report_all(WORK, cls), None)
        rec.setdefault("class_census", {})[cls] = {"rows": (len(rows) if rows is not None else None),
                                                   "error_verbatim": err}
        fact("[P1a] report_all(%-20r) -> %s row(s)%s"
             % (cls, ("%d" % len(rows)) if rows is not None else "NONE", (" ; ERROR " + err) if err else ""))
    # The peer review disputed the arithmetic behind "the tunnel class is now counted": 135+146+146+36+36 = 499
    # against a parent `Tunnel` count of 471, so either the subclasses OVERLAP by >= 28 or `Tunnel` is not their
    # parent at all. The run now STATES which instead of leaving it to inference. REPORTED, never a gate.
    parent = (rec["class_census"].get("Tunnel") or {}).get("rows")
    kids = [(c, (rec["class_census"].get(c) or {}).get("rows"))
            for c in ("LoopTunnel", "ConditionalTunnel", "SelectorTunnel",
                      "LeftShiftRegister", "RightShiftRegister")]
    ksum = sum(v for _c, v in kids if isinstance(v, int))
    rec["tunnel_arithmetic"] = {"parent_Tunnel": parent, "subclass_rows": dict(kids), "subclass_sum": ksum,
                                "sum_minus_parent": (ksum - parent) if isinstance(parent, int) else None}
    fact("[P1a] TUNNEL ARITHMETIC: parent `Tunnel` = %r ; subclasses %r sum to %d ; sum - parent = %r. If that "
         "difference is positive the subclasses OVERLAP by that many and a substring test on the owner class "
         "does not partition them; if it is negative the parent does not cover them. REPORTED because the peer "
         "review named this as an unestablished premise, never a gate and no route is chosen from it."
         % (parent, dict(kids), ksum, rec["tunnel_arithmetic"]["sum_minus_parent"]))

    # (b) every node on #639, its class, and every terminal carrying one of the three watched wires
    di = K.get("d639_index")
    cls_by_uid = K.get("node_class_by_uid", {})
    hits, struct_rows, scanned = [], [], 0
    t0 = time.time()
    for i in range(SCAN_LIMIT):
        if left_s() < M3_MIN_S + 120:
            rec["scan_stopped"] = "wall-clock guard after %d node(s)" % scanned
            break
        try:
            u, tr = g.node_terms_uid(WORK, di, i)
        except Exception as e:                                                     # noqa: BLE001
            rec["scan_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
            break
        if not u:
            break
        scanned += 1
        cls = cls_by_uid.get(str(u), "?")
        is_struct = cls in ("CaseStructure", "WhileLoop", "ForLoop", "Sequence", "FlatSequence",
                            "FlatSequenceFrame", "EventStructure", "Stacked Sequence", "TimedLoop",
                            "DisableStructure", "ConditionalDisableStructure", "InPlaceElementStructure")
        if is_struct:
            struct_rows.append({"nodes_index": i, "uid": u, "class": cls, "n_terminals": len(tr)})
        for t in tr:
            if t["wire"] in WATCH_WIRES:
                hits.append({"nodes_index": i, "node_uid": u, "node_class": cls, "terminal": t["i"],
                             "name": t["name"], "is_source": t["is_source"], "wire": t["wire"],
                             "node_is_structure": is_struct})
    rec.update({"nodes_scanned_on_639": scanned, "scan_cost_s": round(time.time() - t0, 1),
                "structure_nodes": struct_rows, "watch_wire_hits": hits})
    fact("[P1b] scanned %d node(s) of Diagram #%d in %.1f s ; %d STRUCTURE node(s) ; %d terminal(s) carrying "
         "one of %r" % (scanned, D639, rec["scan_cost_s"], len(struct_rows), len(hits), list(WATCH_WIRES)))
    for h in hits:
        fact("    [P1b] wire %r on #%s (%s, structure=%r) t%d %r is_source=%r"
             % (h["wire"], h["node_uid"], h["node_class"], h["node_is_structure"], h["terminal"],
                h["name"], h["is_source"]))
    struct_with_terms = [s for s in struct_rows if s["n_terminals"]]
    gate("P1b node_terms ON A STRUCTURE RETURNS TERMINALS - if it does not, THAT IS THE FINDING (the census "
         "has a blind class), reported, never worked around",
         bool(struct_with_terms) or not struct_rows,
         "%d structure node(s) on #%d, %d of them returned terminals"
         % (len(struct_rows), D639, len(struct_with_terms)))

    # (c) the same three wires walked BY UID through `Wire.Terms[]` - the tunnel-visible route
    net = {}
    for w in WATCH_WIRES:
        rows, err = safe("[P1c] wire_source_owner(%d)" % w, lambda ww=w: WIRE_TERMS(WORK, ww, n=12), [])
        entry = {"rows": rows, "error_verbatim": err}
        fact("[P1c] WIRE %d Terms[] BY UID: %r%s" % (w, rows, (" ; ERROR " + err) if err else ""))
        live = [r for r in (rows or []) if isinstance(r, dict) and r.get("owner_uid")]
        entry["sources"] = [r for r in live if r.get("is_source")]
        entry["sinks"] = [r for r in live if not r.get("is_source")]
        entry["owner_classes"] = [r.get("owner_class") for r in (rows or []) if isinstance(r, dict)]
        entry["tunnel_family_owners"] = [r.get("owner_class") for r in live
                                         if "Tunnel" in str(r.get("owner_class"))]
        fact("[P1c] wire %d: %d source(s), %d sink(s) ; tunnel-family owners %r - REPORTED, and per the "
             "RE-SCOPED A2 a sink on the case structure's OWN tunnel is the INTENDED wiring, not an abort"
             % (w, len(entry["sources"]), len(entry["sinks"]), entry["tunnel_family_owners"]))
        net[str(w)] = entry
    rec["wire_terms_by_uid"] = net
    P["P1"] = rec
    dump()
    return rec


# ======================================================================= A2, RE-SCOPED
def step_A2(p1):
    print("\n---------- [A2] THE RE-SCOPED ABORT CLAUSE - >1 sink, or a sink other than the intended terminal",
          flush=True)
    net = p1["wire_terms_by_uid"]
    hits = p1["watch_wire_hits"]
    verdict = {}
    for w in WATCH_WIRES:
        entry = net.get(str(w), {})
        sinks = entry.get("sinks") or []
        want = EXPECTED_SINK[w]
        rec = {"wire": w, "n_sinks": len(sinks), "sinks": sinks, "expected": list(want),
               "more_than_one_sink": len(sinks) > 1, "sink_is_the_intended_terminal": None,
               "p1b_rows": [h for h in hits if h["wire"] == w]}
        if want[0] == "diagram":
            rec["sink_is_the_intended_terminal"] = (len(sinks) == 1
                                                    and sinks[0].get("owner_uid") == want[1])
            rec["how"] = ("the single sink's OWNER UID is Diagram #%d, which is where the row-2 indicator's "
                          "control terminal lives" % want[1])
        else:
            _kind, node_uid, term_i = want
            sink_rows = [h for h in rec["p1b_rows"]
                         if h["node_uid"] == node_uid and h["terminal"] == term_i
                         and h["is_source"] is False]
            other = [h for h in rec["p1b_rows"]
                     if h["is_source"] is False and not (h["node_uid"] == node_uid
                                                         and h["terminal"] == term_i)]
            rec["p1b_intended_rows"] = sink_rows
            rec["p1b_other_sink_rows"] = other
            rec["sink_is_the_intended_terminal"] = (len(sinks) == 1 and bool(sink_rows) and not other)
            rec["how"] = ("the single sink is a terminal of #%d at t%d, cross-checked against the P1b scan "
                          "of Diagram #%d" % (node_uid, term_i, D639))
        # THE SOURCE SIDE, which the peer review said a sink-only clause drops "at the stage that creates
        # source-side branches". Whitelisted before the run in EXPECTED_SOURCE, gated here.
        sources = entry.get("sources") or []
        want_src = EXPECTED_SOURCE[w]
        rec["n_sources"] = len(sources)
        rec["sources"] = sources
        rec["expected_source"] = list(want_src)
        rec["more_than_one_source"] = len(sources) > 1
        rec["source_is_the_intended_object"] = (len(sources) == 1
                                                and sources[0].get("owner_uid") == want_src[1])
        rec["fires"] = (bool(rec["more_than_one_sink"]) or not rec["sink_is_the_intended_terminal"]
                        or bool(rec["more_than_one_source"])
                        or not rec["source_is_the_intended_object"])
        fact("[A2] wire %d: %d source(s) %r ; %d sink(s) %r ; intended source %r / sink %r -> source %r, "
             "sink %r ; %s"
             % (w, rec["n_sources"], [(s.get("owner_class"), s.get("owner_uid")) for s in sources],
                rec["n_sinks"], [(s.get("owner_class"), s.get("owner_uid")) for s in sinks],
                rec["expected_source"], rec["expected"], rec["source_is_the_intended_object"],
                rec["sink_is_the_intended_terminal"], rec["how"]))
        gate("A2 wire %d has EXACTLY ONE source" % w, not rec["more_than_one_source"],
             "%d source(s)" % rec["n_sources"])
        gate("A2 wire %d's source IS the object its row was built to read (#%d)" % (w, want_src[1]),
             bool(rec["source_is_the_intended_object"]),
             "%r" % ([(s.get("owner_class"), s.get("owner_uid")) for s in sources],))
        gate("A2 wire %d has EXACTLY ONE sink" % w, not rec["more_than_one_sink"],
             "%d sink(s)" % rec["n_sinks"])
        gate("A2 wire %d's sink IS the terminal its row was built to feed" % w,
             bool(rec["sink_is_the_intended_terminal"]), rec["how"])
        verdict[str(w)] = rec
    P["A2"] = verdict
    a2 = any(v["fires"] for v in verdict.values())
    gate("A2 *** ABORT CLAUSE A2 (RE-SCOPED) DID NOT FIRE ***", not a2, "a2=%r" % (a2,))
    fact("[A2] THE LIMIT OF THIS READING, recorded rather than glossed (peer review "
         "archive/peer/2026-09-21-c66-m3-movelocals.md): the endpoint counts above come from "
         "`wire_source_owner`, whose BRANCH detection has never been exercised on a wire known to have two "
         "sinks, and whose array terminator is error 1055 - a code this project has seen mean three different "
         "things (past the end, a BARE terminal, and a genuine invalid reference, the last of them in dispatch "
         "#2's own `owner_of(26117)`). So A2 cannot distinguish 'no third endpoint' from 'a third endpoint "
         "whose reference failed to resolve'. The positive control that would settle it is NOT built here - it "
         "is a new scratch VI the brief does not name - and is carried to judgement.")
    fact("[A2] A1 IS RETIRED AND IS NOT RE-ATTEMPTED: the data-type read was MEASURED unreachable in dispatch "
         "#2 with eight named wrapped properties (diag_c66_s3b_m3.log:133 `TYPE READ UNREACHABLE`). A "
         "SCHEDULING move changes no data types, so this stage does not depend on it; the factual question "
         "is being pursued in the Part A peer dispatch.")
    dump()
    return a2


# ======================================================================= M3
def resolve_dest(tag):
    """38(e): RE-RESOLVE the destination index BY UID from a freshly-read traverse list immediately before
    every `move_in`, and gate that the resolved index still owns that diagram."""
    lst, err = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(WORK, "Diagram"), [])
    uids = [o["uid"] for o in (lst or [])]
    idx = uids.index(BODY_A_UID) if BODY_A_UID in uids else None
    rec = {"tag": tag, "want_diagram_uid": BODY_A_UID, "resolved_index": idx, "traverse_len": len(uids),
           "index_still_owns_it": idx is not None and uids[idx] == BODY_A_UID, "error_verbatim": err}
    K.setdefault("dest_index_resolutions", []).append(rec)
    fact("%s DESTINDEX: Diagram #%d -> traverse index %r (array length %d)" % (tag, BODY_A_UID, idx, len(uids)))
    gate("%s the freshly resolved index %r still owns Diagram #%d (38(e))" % (tag, idx, BODY_A_UID),
         rec["index_still_owns_it"], "traverse_len %d" % len(uids))
    return idx


def body_a_node_uids(tag):
    """THE AUTHORITATIVE GATE for M3: Diagram #23058's own Nodes[] census, by uid."""
    idx, err = safe("%s diag_index(#%d)" % (tag, BODY_A_UID), lambda: diag_index(WORK, BODY_A_UID))
    if idx is None:
        fact("%s Diagram #%d could not be resolved: %s" % (tag, BODY_A_UID, err))
        return [], idx
    rows, lerr = safe("%s node_labels(%r)" % (tag, idx), lambda: g.node_labels(WORK, idx), [])
    uids = [r["uid"] for r in (rows or [])]
    fact("%s Diagram #%d [traverse %r] Nodes[] census: %d node(s) -> %r%s"
         % (tag, BODY_A_UID, idx, len(uids), uids, (" ; " + lerr) if lerr else ""))
    return uids, idx


def step_M1(hints):
    print("\n---------- [M1] SEVEN `move_in` CALLS, ONE OBJECT PER CALL (37(d) severs every wire)", flush=True)
    before_uids, bidx = body_a_node_uids("[M1] BEFORE")
    K["body_a_before"] = before_uids
    nodes = K["node_census_before"]
    after_hints = [bidx, hints[0], TOP]
    for uid, name, pos, why in SET:
        _loc, rows = node_view(WORK, uid, hints, "[M1] #%d BEFORE" % uid, quiet=True)
        fact("[M1] #%d %r BEFORE the move: %d terminal(s), %d WIRED  (%s)"
             % (uid, name, len(rows), wired_count(rows), why))
        bi = resolve_dest("[M1] before move #%d" % uid)
        rec = {"uid": uid, "name": name, "dest_diagram_uid": BODY_A_UID, "dest_index_used": bi,
               "position": list(pos), "wired_before": wired_count(rows), "n_terms_before": len(rows)}
        try:
            rec["echoed_uid"] = move_in(WORK, uid, bi, pos)
            rec["error_verbatim"] = ""
            fact("[M1] MOVE #%d %r -> Diagram #%d [traverse %r] at %r; the op echoed uid %r (37(d): the echo "
                 "is NOT the moved object)" % (uid, name, BODY_A_UID, bi, pos, rec["echoed_uid"]))
        except Exception as e:                                                     # noqa: BLE001
            rec["echoed_uid"] = None
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            fact("[M1] MOVE #%d RAISED %s" % (uid, rec["error_verbatim"]))
        nodes, _p = census_and_purge(WORK, nodes, "[M1] after move #%d" % uid, after_hints)
        after_uids, _ = body_a_node_uids("[M1] after move #%d" % uid)
        rec["in_body_a_nodes"] = uid in after_uids
        gate("M1 #%d appears in Diagram #%d's Nodes[] census (THE authoritative gate)" % (uid, BODY_A_UID),
             rec["in_body_a_nodes"], "body has %d node(s)" % len(after_uids))
        own, oerr = safe("[M1] owner_of(%d) after the move" % uid, lambda u=uid: owner_of(WORK, u))
        rec["owner_of_after"] = list(own) if own else None
        rec["owner_of_error"] = oerr
        fact("[M1] owner_of(%d) AFTER the move = %r (REPORTED ALONGSIDE, never the gate - 53(d^8))"
             % (uid, own))
        _l2, rows2 = node_view(WORK, uid, after_hints, "[M1] #%d AFTER" % uid, quiet=True)
        rec["wired_after"] = wired_count(rows2)
        rec["n_terms_after"] = len(rows2)
        fact("[M1] #%d AFTER the move: %d terminal(s), %d WIRED (was %d)"
             % (uid, len(rows2), wired_count(rows2), rec["wired_before"]))
        rec["exec_state_after"] = unit_boundary("after move #%d %s" % (uid, name))
        K.setdefault("moves", []).append(rec)
        dump()

    final_uids, _ = body_a_node_uids("[M1] AFTER all seven")
    K["body_a_after_moves"] = final_uids
    missing = [u for u in SET_UIDS if u not in final_uids]
    gate("M1 *** ALL SEVEN MOVED UIDS ARE IN Diagram #%d's Nodes[] CENSUS ***" % BODY_A_UID, not missing,
         "missing %r ; body now holds %d node(s)" % (missing, len(final_uids)))
    K["node_census_after_moves"] = nodes
    K["counts_after_moves"] = counts(WORK, "[M1] after the seven moves")
    dump()
    return nodes, not missing, after_hints


def resolve_term(rows, want_name, want_i, want_source, tag):
    """Address a terminal OFF THE MACHINE: by NAME when the name is non-empty and unique among terminals of
    the right direction, otherwise by the RE-MEASURED index. Never by a remembered coordinate."""
    cands = [t for t in rows if t.get("is_source") is want_source]
    if want_name:
        named = [t for t in cands if t.get("name") == want_name]
        if len(named) == 1:
            return named[0]["i"], "by NAME %r (unique among %d %s terminals)" % (
                want_name, len(cands), "source" if want_source else "sink")
    hit = next((t for t in cands if t["i"] == want_i), None)
    if hit is not None:
        return hit["i"], ("by RE-MEASURED INDEX t%d (name %r is empty or not unique); that terminal reads "
                          "name %r is_source %r" % (want_i, want_name, hit.get("name"), hit.get("is_source")))
    fact("%s UNRESOLVED: no %s terminal named %r and none at index %d among %d row(s)"
         % (tag, "source" if want_source else "sink", want_name, want_i, len(rows)))
    return None, "UNRESOLVED"


def step_M2(nodes, hints):
    print("\n---------- [M2] THE SEVEN ROWS, each addressed OFF THE MACHINE", flush=True)
    results = []
    for sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why in INTERNAL_JOBS:
        job = {"sink_uid": sink_uid, "sink_name": sink_name, "sink_t_recorded": sink_t,
               "src_uid": src_uid, "src_name": src_name, "src_t_recorded": src_t, "evidence": why}
        if left_s() < ROW_MIN_S:
            job["result"] = "NOT STARTED - only %.0f s left before the reserve" % left_s()
            gate("M2 row #%d t%d <- #%d: there is enough wall-clock left to start it"
                 % (sink_uid, sink_t, src_uid), False, job["result"])
            results.append(job)
            K.setdefault("rows", []).append(job)
            dump()
            continue
        sloc, srows = node_view(WORK, sink_uid, hints, "[M2] sink #%d" % sink_uid, quiet=True)
        rloc, rrows = node_view(WORK, src_uid, hints, "[M2] src  #%d" % src_uid, quiet=True)
        job["sink_wired_before"] = wired_count(srows)
        job["src_wired_before"] = wired_count(rrows)
        # The FULL tables both ends were addressed from, so terminal-index drift after the moves is visible in
        # the record rather than inferred (the peer review: case-structure tunnel indices renumber).
        job["sink_terminals_before"] = srows
        job["src_terminals_before"] = rrows
        si, show = resolve_term(srows, sink_name, sink_t, False, "[M2] sink #%d" % sink_uid)
        ri, rhow = resolve_term(rrows, src_name, src_t, True, "[M2] src #%d" % src_uid)
        job["sink_term_resolution"] = show
        job["src_term_resolution"] = rhow
        sd = (sloc.get("found") or {}).get("diagram_index")
        sn = (sloc.get("found") or {}).get("nodes_index")
        rd = (rloc.get("found") or {}).get("diagram_index")
        rn = (rloc.get("found") or {}).get("nodes_index")
        job["addr"] = {"sink_diag": sd, "sink_node": sn, "sink_term": si,
                       "src_diag": rd, "src_node": rn, "src_term": ri}
        fact("[M2] row #%d t%r <- #%d t%r : %r ; sink %s ; src %s"
             % (sink_uid, si, src_uid, ri, job["addr"], show, rhow))
        same_diag = (sd is not None and sd == rd)
        job["same_nested_diagram"] = same_diag
        if None in (si, ri, sn, rn) or not same_diag:
            job["result"] = "NOT ADDRESSABLE" if None in (si, ri, sn, rn) else "NOT ON ONE NESTED DIAGRAM"
            gate("M2 row #%d t%r <- #%d t%r is addressable on ONE nested diagram"
                 % (sink_uid, sink_t, src_uid, src_t), False, "%r ; %s" % (job["addr"], job["result"]))
            results.append(job)
            K.setdefault("rows", []).append(job)
            dump()
            continue
        try:
            dw, es, err = CONNECT_V1(WORK, sd, sn, si, rd, rn, ri, V1_LABELS)
            job["connect"] = {"wire_delta": dw, "exec_state": es, "machine_error": str(err)[:200]}
        except Exception as e:                                                     # noqa: BLE001
            job["connect"] = {"exception": "%s: %s" % (type(e).__name__, str(e)[:250])}
        fact("[M2] connect_nested_v1 -> %r" % (job["connect"],))
        nodes, _p = census_and_purge(WORK, nodes, "[M2] after row #%d t%r" % (sink_uid, si), hints)
        _l3, srows2 = node_view(WORK, sink_uid, hints, "[M2] sink #%d AFTER" % sink_uid, quiet=True)
        _l4, rrows2 = node_view(WORK, src_uid, hints, "[M2] src  #%d AFTER" % src_uid, quiet=True)
        job["sink_wired_after"] = wired_count(srows2)
        job["src_wired_after"] = wired_count(rrows2)
        srow = next((t for t in srows2 if t["i"] == si), None)
        rrow = next((t for t in rrows2 if t["i"] == ri), None)
        job["same_wire_uid"] = bool(srow and rrow and srow["wire"] and srow["wire"] == rrow["wire"])
        job["wire_uid"] = (srow or {}).get("wire")
        fact("[M2] row #%d t%r <- #%d t%r : sink wire %r / src wire %r ; same net %r ; WIRED-TERMINAL counts "
             "sink %d -> %d, src %d -> %d"
             % (sink_uid, si, src_uid, ri, (srow or {}).get("wire"), (rrow or {}).get("wire"),
                job["same_wire_uid"], job["sink_wired_before"], job["sink_wired_after"],
                job["src_wired_before"], job["src_wired_after"]))
        gate("M2 row #%d t%r <- #%d t%r: the WIRED-TERMINAL count rose on BOTH ends and they share ONE wire "
             "uid (49(e))" % (sink_uid, si, src_uid, ri),
             job["same_wire_uid"] and job["sink_wired_after"] > job["sink_wired_before"]
             and job["src_wired_after"] > job["src_wired_before"],
             "wire %r" % (job["wire_uid"],))
        job["exec_state_after"] = unit_boundary("after row #%d t%r <- #%d t%r" % (sink_uid, si, src_uid, ri))
        results.append(job)
        K.setdefault("rows", []).append(job)
        dump()
    for row in NOT_ATTEMPTED:
        fact("[M2] NOT ATTEMPTED - %s (verb %s): %s" % (row["row"], row["verb"], row["why"]))
    return nodes, results


def step_final(all_moved, hints):
    print("\n---------- [Z] THE PASS CRITERION, THE FINAL SAVE, THE RESTART AND THE COLD REOPEN", flush=True)
    es = read_es("[Z] before the pass-criterion decision", WORK)
    K["counts_final"] = counts(WORK, "[Z] final, in memory")
    _l, lrows = node_view(WORK, LOOP11_UID, hints, "[Z] #%d the WhileLoop" % LOOP11_UID, quiet=True)
    K["loop637_after"] = {"n_terms": len(lrows), "n_wired": wired_count(lrows)}
    fact("[Z] #%d (WhileLoop): %d terminals, %d WIRED (before: %r)"
         % (LOOP11_UID, len(lrows), wired_count(lrows), K.get("loop637_before")))
    gate("Z1 #%d's terminal/wired counts are UNCHANGED - no new tunnel (37(e)/50(e))" % LOOP11_UID,
         K["loop637_after"] == K.get("loop637_before"),
         "%r -> %r" % (K.get("loop637_before"), K["loop637_after"]))
    for uid in SET_UIDS:
        own, _e = safe("[Z] owner_of(%d)" % uid, lambda u=uid: owner_of(WORK, u))
        fact("[Z] owner_of(%d) = %r (REPORTED ALONGSIDE the Nodes[] census, NEVER the gate - 53(d^8))"
             % (uid, own))
    ok = bool(all_moved) and es == 1
    gate("Z2 *** THE PASS CRITERION: all seven in Diagram #%d's Nodes[] AND ExecState 1 ***" % BODY_A_UID,
         ok, "all_moved %r ; ExecState %r" % (all_moved, es))
    if not ok:
        fact("[Z] THE FINAL SAVE IS NOT TAKEN - the pass criterion is not met. Intermediate artefacts saved "
             "at ExecState 1, if any, STAY on disk. `allow_broken` is never set and `gui_save` is never called.")
        return None
    rec = save_artefact("[Z] the M3 artefact", FINAL_PATH, BED_MD5, "the bed")
    D.fresh("[Z] LabVIEW RESTART before the COLD reopen")
    R["handles"]["after_final_restart"] = labview_handles()
    es_cold = read_es("[Z] COLD, after the restart", FINAL_PATH)
    K["exec_state_cold"] = es_cold
    gate("Z3 *** the saved artefact reopens COLD at ExecState 1 ***", es_cold == 1, "%r" % (es_cold,))
    K["counts_cold"] = counts(FINAL_PATH, "[Z] COLD")
    safe("[Z] close_panel(final)", lambda: g.close_panel(FINAL_PATH))
    return rec


# ======================================================================= main
def main():
    print("=== diag_c66b_s3b_m3  %s  (bgrun --max-min 40)" % STAMP, flush=True)
    aborted = None
    try:
        phase_0()
        hints = step_E()
        p1 = step_P1(hints)
        a2 = step_A2(p1)
        if a2:
            aborted = "A2"
            R["aborted_at"] = aborted
            fact("*** ABORT CLAUSE A2 FIRED. STOPPING BEFORE THE FIRST `move_in`: no .vi is saved, the "
                 "working copy is removed, and nothing further is attempted. ***")
            raise Stop("abort clause A2")
        if left_s() < M3_MIN_S:
            R["m3_not_started"] = "only %.0f s left before the reserve; M3 needs %.0f s" % (left_s(), M3_MIN_S)
            gate("M0 there is enough wall-clock left to start M3", False, R["m3_not_started"])
            raise Stop("no wall-clock for M3")
        gate("M0 there is enough wall-clock left to start M3", True, "%.0f s left before the reserve"
             % left_s())
        nodes, all_moved, after_hints = step_M1(hints)
        step_M2(nodes, after_hints)
        step_final(all_moved, after_hints)
    except Stop as e:
        fact("STOP: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        R["unexpected_exception"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("UNEXPECTED EXCEPTION: %s" % R["unexpected_exception"])
    finally:
        safe("close_panel(WORK)", lambda: g.close_panel(WORK))
        for path, tag in ((WORK, "the working copy"),):
            if os.path.exists(path):
                safe("remove %s" % tag, lambda p=path: os.remove(p))
            gate("Y scratch %s is gone (exists=False)" % os.path.basename(path), not os.path.exists(path),
                 "")
        print("\n---------- [Y] THE md5 PINS AFTER, THE REFS AND THE HANDLES", flush=True)
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops", S2_ARTEFACT, S2_MD5),
                               ("D1_s3a_focus_ind", S3A_ARTEFACT, S3A_MD5),
                               ("D1_s3b_row1a", ROW1A_ARTEFACT, ROW1A_MD5),
                               ("D1_s3b_row1", ROW1_ARTEFACT, ROW1_MD5), ("THE BED", BED, BED_MD5)):
            pr = probe("Y %s AFTER" % tag, path)
            gate("Y %s md5 is STILL its pin %s" % (tag, pin[:8]), pr.get("md5") == pin,
                 "%r" % (pr.get("md5"),))
        rc = g.ref_counts()
        R["ref_counts"] = rc
        fact("refs: %r" % (rc,))
        gate("Y refs opened == closed and 0 live", rc.get("live") == 0, "%r" % (rc,))
        R["handles"]["after"] = labview_handles()
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"]["after"], R["handles"].get("before")))
        fact("ARTEFACTS THIS RUN LEFT ON DISK: %r"
             % [(os.path.basename(a["dest"]), a.get("md5"), a.get("size"))
                for a in R["artefacts_on_disk"]])
        dump()
        print("\n=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                    ("; failing: " + ", ".join(fails)) if fails else ""),
              flush=True)
        print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
