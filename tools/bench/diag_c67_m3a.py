"""diag_c67_m3a - cycle 67 material #1 PART B: STAGE M3a-1 WITH A FULL TERMINAL CENSUS ON BOTH SIDES.

A DIAGNOSTIC under tools/bench/, never a recipe (48(n)). It executes the route the JUDGEMENT session wrote,
in the order it wrote it, and its reason for existing is CENSUS 1 and CENSUS 2 - the complete, machine-read
list of every BARE terminal on the seven moved nodes before and after the four shift-register rows. Both
censuses run UNCONDITIONALLY, whatever `ExecState` says. No route is chosen here and none is recommended.

WHAT ALREADY EXISTED AND IS REUSED, NOT REBUILT (checked before a line was written:
`docs/toolkit-capabilities.md`, `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`)
  - `tools/gscript.py:673` `add_shift_reg` (OpAddShiftReg_v0, INDEX row 37) - the BUILT register creator.
  - `tools/gscript.py:713` `wire_sr` (OpWireSR_*_v0, INDEX row 38) - the BUILT one-side register writer;
    variants LeftIn / RightIn only. `LeftOutNode` / `LeftOutCtl` are STAGE M3a-2 and are NOT called here.
  - `tools/gscript.py:753` `shift_reg` / `:786` `shift_reg_left` (OpShiftRegs_v0/v1) - the BUILT register
    readers; `shift_reg_left` is the only one that reaches the LEFT register and its OUTER terminal.
  - `tools/recipes/build_d1_v0.py:318` `move_in` / `:338` `owner_of` / `:357` `diag_index` - THE BUILT mover
    and the two uid-addressed readers. `move_in` is not in gscript at all.
  - `tools/recipes/build_opconnectnested_v1.py:418` `connect_nested_v1` - the BUILT node->node writer for two
    nodes on ONE nested diagram.
  - `tools/recipes/build_opconnectfromwire_v0.py:423` `wire_source_owner` - `OpWireSource_v5`, the ONLY BY-UID
    walk of a WIRE's own `Terms[]`, giving each terminal's OWNER class and uid. Used for the M3a-2 reads.
  - `tools/bench/diag_c66b_s3b_m3.py` - THE SEVEN `move_in` CALLS AND THE SEVEN INTERNAL ROWS ARE REUSED FROM
    IT VERBATIM (`SET` :183-193, `INTERNAL_JOBS` :200-210), same order, same addressing. They are NOT
    re-derived and NOT improved. Every helper below is reused in shape from the same file.
  - `tools/bench/c60c_astcheck.py` - the static gate, run with `--route movein` on THIS file before launch
    (this file DOES call `move_in`, so gate 7 must PASS). NOT edited.
  NO new op, NO new verb, NO edit to tools/gscript.py, NO edit to any *_astcheck.py gate file, NO recipe.

THE BED  `claudeDev\\D1_s3b_row2_20260921_160311.vi`, md5 26c54ff784cb5cea21edbd214d2cc3a0, 476,759 B.
  READ-ONLY, md5-pinned BEFORE and AFTER, never overwritten. All work happens on a fresh stamped copy.

PREDICTION CONTRACT (machine-checkable; a failed prediction is reported, never explained away)
  1  COLD: ExecState 1 / Node 632 / Wire 1907 / ControlTerminal 116 / Local 10 / LoopTunnel 135 /
     Tunnel 471 ; `Diagram #639` = traverse index 46 with 75 nodes ; `#637` = 59 TERMINALS / 48 WIRED.
     `report_all('WhileLoop')[loop_index].uid == 23032` is ECHOED immediately before every call that takes
     a `loop_index` (the A7 pattern) - the index is never carried across a call.
  2  TWO `add_shift_reg` calls on `#23032`. Both returned RightShiftRegister uids are recorded and each is
     mapped to its `reg_index` by READING `shift_reg(...)` for reg_index 0..N and matching the uid - the
     mapping is never assumed. PREDICTION: `ExecState` drops to 0 here and THAT IS CORRECT, NOT A FAILURE
     (`tools/gscript.py:683-687`).
  3  THE SEVEN `move_in`s, exactly as c66b does them; destination index RE-RESOLVED by uid before each
     (38(e)); junk `Invoke` purged BY UID after each (55(c)). PREDICTION: all seven appear in
     `Diagram #23058`'s Nodes[]; wired-terminal counts fall to 0; `ExecState` stays 0.
  4  THE SEVEN INTERNAL ROWS, exactly as c66b does them, via `connect_nested_v1`; census + purge after each.
  5  CENSUS 1 - THE MEASUREMENT THIS DISPATCH EXISTS FOR. For EACH of the seven moved nodes the FULL
     `node_terms` table (terminal index, Name, IsSource, WireUID, the four error columns) - EVERY terminal,
     not a selection - printed to the log and dumped to diag_c67_m3a.json, plus the derived BARE list of
     every terminal whose WireUID is 0. UNCONDITIONAL.
  6  THE FOUR SR ROWS, reg_index from step 2, node/terminal indices read with `node_terms_uid` on
     `#23032`'s body diagram immediately before each call:
       wire_sr('LeftIn' , reg VISA, node #48    , t3 'VISA resource name')
       wire_sr('RightIn', reg VISA, node #10407 , t4)
       wire_sr('LeftIn' , reg POS , node #48    , t4 'In position')
       wire_sr('RightIn', reg POS , node #10407 , t6 'position [internal units]')
     The registers are paired by the TYPE THE SINK DEMANDS, read off the terminal NAMES, not by creation
     order. Each row is verified BY WIRE UID AT BOTH ENDS (the node's terminal table and the register's own
     inside terminal must carry the SAME non-zero wire uid).
  7  CENSUS 2 - the same full tables for the seven moved nodes PLUS both shift registers, and the same
     derived BARE list. UNCONDITIONAL.
  8  `ExecState`. 1 => SAVE `claudeDev\\D1_s3b_m3a_<stamp>.vi`, LabVIEW RESTART, COLD reopen, `ExecState`
     again, and the ordered `Broken?` pass LAST OF ALL (42(b)/52(f) - never above a save point).
     0 => SAVE NOTHING. Census 2 has already named every bare terminal; report it and stop. No retry, no
     substituted verb, no invented row.
  M3a-2 MEASUREMENTS (reported as FACTS, nothing chosen from them):
     (i)  what feeds the OUTER-LEFT terminals of the EXISTING shift registers `#4344` and `#4274` today -
          source node uid, terminal index, terminal name, wire uid.
     (ii) whether the diagram that owns `#23032` is the VI's TOP-LEVEL diagram (the `Diagram` traverse
          index 0 / TopLevelDiagram test), since `LeftOutNode` addresses TOP-LEVEL Nodes[] only.
  Y  md5 pins hold BEFORE and AFTER: ORIGINAL 2a78e17c / D1_s1_copy 3e3d23ce / D1_s2_loops 6ff19497 /
     A1 eef91c1d / A2 THE BED 26c54ff7 / A3 row 1 72f0d47d. Every scratch `exists=False` at the end;
     `THE FILES THIS RUN LEFT ON DISK: [...]` printed. Refs opened == closed, 0 live. Handles either side.
     `#637` still 59 TERMINALS / 48 WIRED; ControlTerminal and Local censuses either side.

*** THE SAVED M3a-1 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL - ITS SHIFT REGISTERS ARE
    UNINITIALISED. *** The initial values are stage M3a-2 and are deliberately out of scope. The artefact
    is NEVER RUN (34(f)).

FORBIDDEN AND ABSENT: no `g.open_panel`; no `allow_broken`; no `gui_save`; no `remove_bad_wires*`; no GUI
action; no new op VI; no new verb; `tools/gscript.py` NOT edited; no `*_astcheck.py` edited; no recipe; no
VI run (34(f)); no motor / ASI / camera (rig ASSEMBLED); no new process device; `CYCLE_GUARD_OFF` never set.
`retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` NOT run
(54(a)). `docs/cycle27-plan.md` and STATUS's `## NEXT` are NOT touched.
VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)).
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
A1_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
A1_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
A3_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_20260921_135932.vi")
A3_MD5 = "72f0d47d0b1cbd0834d50f1483e558c1"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
BED_SIZE = 476759

# THE SIX md5 PINS, in the brief's own order. Checked BEFORE and AFTER.
PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy", S1_ARTEFACT, S1_MD5),
        ("D1_s2_loops", S2_ARTEFACT, S2_MD5), ("A1 D1_s3a_focus_ind", A1_ARTEFACT, A1_MD5),
        ("A2 THE BED", BED, BED_MD5), ("A3 D1_s3b_row1", A3_ARTEFACT, A3_MD5))

TOP = 0
D639 = 639                       # the nested diagram the 1.5 set lives on today
D639_RECORDED = 46
D639_NODES_RECORDED = 75
LOOP_A_UID = 23032               # the NEW While Loop; 37(h) \ docs\cycle27-plan.md:1127-1129 - CITED.
BODY_A_UID = 23058               # its body diagram, the destination
LOOP11_UID = 637                 # the ORIGINAL While Loop that owns Diagram #639
LOOP637_TERMS_RECORDED = 59
LOOP637_WIRED_RECORDED = 48

SUBVI_UID = 48                   # ASI_adjust focus-subvi.vi
CASE_UID = 10407                 # the autofocus CaseStructure
LOCAL_ROW1_UID = 23499
LOCAL_ROW2_UID = 23523
EXISTING_LEFT_SRS = (4344, 4274)  # the M3a-2 question (i): what feeds their OUTER-LEFT terminals today

BASE = {"Node": 632, "Wire": 1907, "ControlTerminal": 116, "Local": 10, "LoopTunnel": 135}
BASE_TUNNEL = 471

# THE MOVE SET - SEVEN objects, VERBATIM from tools/bench/diag_c66b_s3b_m3.py:183-193.
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

# THE SEVEN INTERNAL ROWS - VERBATIM from tools/bench/diag_c66b_s3b_m3.py:200-210.
# (sink_uid, sink_name, sink_t, src_uid, src_name, src_t, evidence)
INTERNAL_JOBS = [
    (48, "-Inc reference", 0, 3529, "- Inc (PgDn)", 0, "w4833; c53_row_class.json :1919 / :2096"),
    (48, "+Inc reference", 1, 3560, "+ Inc (PgUp)", 0, "w2819; d1_rewire_sources.json:1946 / :2126"),
    (48, "Focus inc reference", 2, 3447, "Focus Step (F1)", 0, "w1893; d1_rewire_sources.json:1973 / :2156"),
    (10407, "Outgoing Handle", 3, 48, "Outgoing Handle", 6, "w11232; d1_rewire_sources.json:1820 / :2066"),
    (10407, "Out position", 5, 48, "Out position", 5, "w7388; d1_rewire_sources.json:1865 / :2036"),
    (10407, "", 0, LOCAL_ROW1_UID, "", 0,
     "row 1; wire 23502 measured at #10407 t0 and at Local #23499 t0"),
    (10407, "index", 2, LOCAL_ROW2_UID, "index", 0,
     "row 2; wire 23540 measured at #10407 t2 and at Local #23523 t0"),
]

# THE FOUR SR ROWS. `pair` names the register by THE TYPE THE SINK DEMANDS, read off the terminal NAMES.
# variant LeftIn  -> the node terminal is a SINK   (the left register's INSIDE terminal is the source)
# variant RightIn -> the node terminal is a SOURCE (the right register's INSIDE terminal is the sink)
# (pair, variant, node_uid, term_name, term_index, node_term_is_source)
SR_JOBS = [
    ("VISA", "LeftIn", SUBVI_UID, "VISA resource name", 3, False),
    ("VISA", "RightIn", CASE_UID, "", 4, True),
    ("POS", "LeftIn", SUBVI_UID, "In position", 4, False),
    ("POS", "RightIn", CASE_UID, "position [internal units]", 6, True),
]
SR_PAIRS = ("VISA", "POS")

# THE PART A PEER'S FALSIFIABLE PREDICTION, RECORDED SO THE CENSUS CAN BE SCORED AGAINST IT.
# archive/peer/2026-09-21-c67-m3a-srrows.md sec.4, claude/hypothesis, opus/effort max, ANSWERED 622 s:
#   "Predicted AFTER-census if I am right: #48 zero bare; #3529/#3560/#3447/#23499/#23523 zero bare;
#    #10407 exactly one bare terminal, t1 '# slices in stack' - with ExecState still 0. If instead
#    #10407 shows zero bare and ExecState reads 1, the claim stands."
# REPORTED ONLY. It is NOT a gate, it changes no step, and the census runs identically whatever it says.
# Every ROUTE change the same review proposed (re-ordering the four rows to RightIn-first, adding the
# #10407 t1 tunnel row, the t6 second-sink rule-1a question) was NOT acted on and is quoted verbatim to
# the judgement session - see that file's "What was done with it".
PEER_PREDICTION = {"3529": 0, "3560": 0, "3447": 0, "23499": 0, "23523": 0, "48": 0, "10407": 1}
PEER_PREDICTION_EXEC_STATE = 0
PEER_PREDICTION_NAMED_BARE = (10407, 1, "# slices in stack")

SCAN_LIMIT = 140
REG_PROBE_MAX = 8               # how many reg_index slots are probed when mapping uid -> reg_index
RUN_DEADLINE_S = 40 * 60.0       # the bgrun --max-min this file is launched under
RESERVE_S = 420.0                # held back for the final save, the restart and the cold reopen
M3_MIN_S = 540.0
ROW_MIN_S = 150.0

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c67_m3a.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

WORK = os.path.join(g.CLAUDEDEV, "WORK_C67M3A_%s.vi" % STAMP)
FINAL_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a_%s.vi" % STAMP)

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 67 material #1 PART B: STAGE M3a-1 - two add_shift_reg pairs on #23032, the seven "
             "move_in calls and the seven internal rows VERBATIM from diag_c66b_s3b_m3.py, a FULL terminal "
             "census of the seven moved nodes, the four SR rows, and the same census again",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "bed": {"path": BED, "md5_pin": BED_MD5, "size_pin": BED_SIZE,
             "never_overwritten": "the bed is only ever READ; all work is on WORK, a fresh stamped name"},
     "artefact_is_not_computation_equivalent":
         "THE SAVED M3a-1 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL - ITS SHIFT REGISTERS ARE "
         "UNINITIALISED. The initial values are stage M3a-2. The artefact is NEVER RUN (34(f)).",
     "initial_values_out_of_scope":
         "wire_sr('LeftOutNode') and wire_sr('LeftOutCtl') are NOT called anywhere in this file",
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "no_open_panel_call_in_this_file": True, "gscript_not_edited": True,
     "no_astcheck_gate_file_edited": True, "no_gui_action": True,
     "allow_broken": "NEVER True", "gui_save": "NEVER called",
     "remove_bad_wires_scripted": "not imported, not called",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "purges": [], "build": {}, "census_1": {}, "census_2": {}, "m3a2": {}}
K = R["build"]


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
    read is never deleted and stops the build instead."""
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


def save_artefact(tag, dest, not_equal_to, not_equal_label):
    """g.save writes the WORKING copy in place; the artefact is a fresh path LabVIEW has never seen.
    A file byte-identical to its predecessor means THE IN-MEMORY EDITS DID NOT LAND - reported as a FAILURE."""
    rec = {"tag": tag, "dest": dest, "save_error_verbatim": "",
           "NOT_COMPUTATION_EQUIVALENT": "THE SAVED M3a-1 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE "
                                         "ORIGINAL - ITS SHIFT REGISTERS ARE UNINITIALISED. It is never run."}
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
    fact("*** %s IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL - ITS SHIFT REGISTERS ARE UNINITIALISED. "
         "The initial values are stage M3a-2. IT IS NEVER RUN (34(f)). ***" % os.path.basename(dest))
    gate("%s *** A FILE IS ON DISK at %s ***" % (tag, os.path.basename(dest)), bool(rec["exists"]),
         "md5 %r size %r" % (rec["md5"], rec["size"]))
    gate("%s that file is NOT byte-identical to %s (the in-memory edits LANDED)" % (tag, not_equal_label),
         bool(rec["exists"]) and not rec["bytes_equal_to_the_predecessor"] and not rec["save_error_verbatim"],
         "md5 %r vs %s %r ; save error %r"
         % (rec["md5"], not_equal_label, not_equal_to, rec["save_error_verbatim"]))
    dump()
    return rec


def unit_boundary(tag):
    """The user's 2026-09-19 split rule, applied MECHANICALLY and not as a branch: read ExecState at every
    unit boundary and, WHENEVER it reads 1, leave a file on disk before the next unit starts. With two
    uninitialised registers in the VI from step 2 onwards this is expected never to fire; it is kept so the
    rule is enforced by code rather than by expectation."""
    es = read_es("[UNIT] %s" % tag, WORK)
    K.setdefault("unit_boundaries", []).append({"tag": tag, "exec_state": es})
    if es == 1:
        k = sum(1 for a in R["artefacts_on_disk"] if "_u" in os.path.basename(a["dest"])) + 1
        save_artefact("[UNIT %d] %s - ExecState 1 at a unit boundary" % (k, tag),
                      os.path.join(g.CLAUDEDEV, "D1_s3b_m3a_u%d_%s.vi" % (k, STAMP)), BED_MD5, "the bed")
    else:
        fact("[UNIT] %s: ExecState %r - NOT 1, so no intermediate file is written at this boundary "
             "(`allow_broken` is never set and `gui_save` is never called)" % (tag, es))
    dump()
    return es


# ============================================== the A7 pattern: a loop_index is ECHOED, never carried
def loop_index_of(uid, tag, fatal=True):
    """Gate A7: resolve the loop's index in report_all('WhileLoop') FRESH, and ECHO that
    report_all('WhileLoop')[loop_index].uid == uid, immediately before every call that takes a loop_index."""
    rows, err = safe("%s report_all('WhileLoop')" % tag, lambda: g.report_all(WORK, "WhileLoop"), [])
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    echo = None
    if idx is not None:
        echo = next((r["uid"] for r in (rows or []) if r["i"] == idx), None)
    rec = {"tag": tag, "want_uid": uid, "loop_index": idx, "echoed_uid": echo,
           "whileloop_rows": len(rows or []), "error_verbatim": err}
    K.setdefault("loop_index_echoes", []).append(rec)
    fact("%s A7 ECHO: report_all('WhileLoop')[%r].uid == %r (want #%d; %d WhileLoop row(s))"
         % (tag, idx, echo, uid, len(rows or [])))
    gate("A7 %s report_all('WhileLoop')[loop_index].uid == %d" % (tag, uid), echo == uid,
         "loop_index %r echoed %r" % (idx, echo), fatal=fatal)
    return idx


def echo_reg_uid(loop_index, reg_index, want_uid, tag):
    """The A7 pattern applied to a reg_index: re-READ the register at that slot and echo its uid immediately
    before the call that uses it, so a slot that renumbered is caught rather than trusted."""
    sr, err = safe("%s shift_reg(reg_index=%r) echo" % (tag, reg_index),
                   lambda: g.shift_reg(WORK, loop_index, reg_index))
    got = (sr or {}).get("uid")
    fact("%s REGECHO: shift_reg[reg_index=%r].uid == %r (want #%r)%s"
         % (tag, reg_index, got, want_uid, (" ; ERROR " + err) if err else ""))
    gate("A7r %s shift_reg[reg_index=%r].uid == %r" % (tag, reg_index, want_uid), got == want_uid,
         "read %r" % (got,))
    return got


def reg_index_of(loop_index, reg_uid, tag):
    """Map a RightShiftRegister uid to its reg_index by READING shift_reg(...) for each slot. Never assumed."""
    probes = []
    hit = None
    for k in range(REG_PROBE_MAX):
        sr, err = safe("%s shift_reg(reg_index=%d)" % (tag, k),
                       lambda kk=k: g.shift_reg(WORK, loop_index, kk))
        row = {"reg_index": k, "uid": (sr or {}).get("uid"), "error_verbatim": err,
               "out": (sr or {}).get("out"), "inside": (sr or {}).get("inside"),
               "op_errors": (sr or {}).get("errors")}
        probes.append(row)
        fact("%s shift_reg[reg_index=%d] -> uid %r ; out %r ; inside %r ; errors %r"
             % (tag, k, row["uid"], row["out"], row["inside"], row["op_errors"]))
        if row["uid"] == reg_uid and hit is None:
            hit = k
        if err:
            break
    K.setdefault("reg_index_probes", []).append({"tag": tag, "want_uid": reg_uid, "resolved": hit,
                                                 "probes": probes})
    fact("%s REGINDEX: RightShiftRegister #%r -> reg_index %r (READ, never assumed)" % (tag, reg_uid, hit))
    return hit, probes


# ======================================================================= PHASE 0 - files only, zero LabVIEW
def phase_0():
    print("\n---------- [0] FILES ONLY, ZERO LabVIEW - the six md5 pins BEFORE", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; the pre-batch restart below is "
         "MANDATORY - 44(e))" % R["handles"]["before"])
    for tag, path, pin in PINS:
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


# ================================================= STEP 1 - cold ExecState + the baseline censuses
def step_1():
    print("\n---------- [1] COLD ExecState AND THE BASELINE CENSUSES", flush=True)
    es = read_es("[1] the bed, COLD", WORK)
    gate("1a the bed reopens COLD at ExecState 1", es == 1, "%r" % (es,), fatal=True)
    c = counts(WORK, "[1] COLD")
    K["counts_before"] = c
    for k, v in BASE.items():
        gate("1b %s == %d (the recorded baseline)" % (k, v), c.get(k) == v, "%r" % (c.get(k),))
    gate("1b Tunnel == %d" % BASE_TUNNEL, c.get("Tunnel") == BASE_TUNNEL, "%r" % (c.get("Tunnel"),))

    di, err = safe("[1] diag_index(#%d)" % D639, lambda: diag_index(WORK, D639))
    K["d639_index"] = di
    gate("1c Diagram #%d resolves to traverse index %d" % (D639, D639_RECORDED), di == D639_RECORDED,
         "%r%s" % (di, (" ; ERROR " + err) if err else ""), fatal=True)
    rows, lerr = safe("[1] node_labels(%r)" % di, lambda: g.node_labels(WORK, di), [])
    K["d639_nodes"] = len(rows or [])
    gate("1d Diagram #%d carries %d nodes" % (D639, D639_NODES_RECORDED),
         len(rows or []) == D639_NODES_RECORDED, "%d%s" % (len(rows or []), (" ; " + lerr) if lerr else ""))

    ncen, _ = node_census(WORK, "[1] whole-VI")
    K["node_census_before"] = ncen
    hints = [di, TOP]
    _loc, lrows = node_view(WORK, LOOP11_UID, hints, "[1] #%d the WhileLoop" % LOOP11_UID, quiet=True)
    K["loop637_before"] = {"n_terms": len(lrows), "n_wired": wired_count(lrows)}
    gate("1e #%d has %d TERMINALS and %d WIRED (a count pair, NOT a position)"
         % (LOOP11_UID, LOOP637_TERMS_RECORDED, LOOP637_WIRED_RECORDED),
         len(lrows) == LOOP637_TERMS_RECORDED and wired_count(lrows) == LOOP637_WIRED_RECORDED,
         "%r" % (K["loop637_before"],))

    # The M3a-2 measurements are taken HERE, on the untouched cold copy, so nothing this run does can
    # contaminate them. REPORTED AS FACTS; nothing is chosen from them.
    step_m3a2(hints)
    dump()
    return hints


# ============================================ the two M3a-2 measurements - facts only, no route chosen
def m3a2_left_sr_feed(hints):
    """(i) What feeds the OUTER-LEFT terminals of the EXISTING shift registers #4344 and #4274 today."""
    print("\n---------- [M3a-2 (i)] WHAT FEEDS THE OUTER-LEFT TERMINALS OF #4344 AND #4274 TODAY", flush=True)
    li = loop_index_of(LOOP11_UID, "[M3a-2] #%d" % LOOP11_UID, fatal=False)
    out = {"loop_uid": LOOP11_UID, "loop_index": li, "registers": {}}
    found = {}
    if li is None:
        fact("[M3a-2 (i)] #%d has no index in report_all('WhileLoop') - the (i) measurement CANNOT be taken "
             "this run. REPORTED as a gap; nothing is inferred from it." % LOOP11_UID)
    for k in range(REG_PROBE_MAX if li is not None else 0):
        stop = False
        for lx in range(3):
            srl, err = safe("[M3a-2] shift_reg_left(reg=%d, left=%d)" % (k, lx),
                            lambda kk=k, ll=lx: g.shift_reg_left(WORK, li, kk, ll))
            if err or not srl:
                stop = True
                break
            lreg = srl.get("left") or {}
            luid = lreg.get("uid")
            fact("[M3a-2] reg_index %d left_index %d -> right #%r ; left #%r ; left.out %r ; left_uids %r"
                 % (k, lx, srl.get("uid"), luid, lreg.get("out"), srl.get("left_uids")))
            if luid in EXISTING_LEFT_SRS and luid not in found:
                found[luid] = {"reg_index": k, "left_index": lx, "right_uid": srl.get("uid"),
                               "left_uid": luid, "left_out": lreg.get("out"),
                               "left_inside": lreg.get("inside"), "op_errors": srl.get("errors")}
            if lx + 1 >= len(srl.get("left_uids") or [1]):
                break
        if stop or len(found) == len(EXISTING_LEFT_SRS):
            break
    for luid in EXISTING_LEFT_SRS:
        rec = found.get(luid)
        if rec is None:
            out["registers"][str(luid)] = {"located": False,
                                           "note": "NOT located among the probed reg/left slots"}
            fact("[M3a-2 (i)] LeftShiftRegister #%d was NOT located among the probed slots - REPORTED as a "
                 "gap in the measurement, nothing is inferred from it" % luid)
            continue
        wire_uid = (rec.get("left_out") or {}).get("wire") or 0
        rec["outer_left_wire_uid"] = wire_uid
        if not wire_uid:
            rec["feeder"] = None
            fact("[M3a-2 (i)] #%d OUTER-LEFT terminal %r carries WIRE 0 - it is UNINITIALISED ON THIS BED "
                 "TODAY. Reported as a fact; nothing is concluded from it here."
                 % (luid, rec.get("left_out")))
        else:
            walk, werr = safe("[M3a-2] wire_source_owner(%d)" % wire_uid,
                              lambda w=wire_uid: WIRE_TERMS(WORK, w), [])
            rec["wire_walk"] = walk
            rec["wire_walk_error"] = werr
            src = next((t for t in (walk or []) if t.get("is_source") and t.get("owner_uid")), None)
            rec["source_owner"] = src
            fact("[M3a-2 (i)] #%d OUTER-LEFT wire %d ; wire_source_owner walk %r ; SOURCE owner %r"
                 % (luid, wire_uid, walk, src))
            if src and src.get("owner_uid"):
                loc, srows = node_view(WORK, src["owner_uid"], hints,
                                       "[M3a-2 (i)] feeder #%s" % src["owner_uid"], quiet=True)
                hit = next((t for t in srows if t.get("wire") == wire_uid), None)
                rec["feeder"] = {"node_uid": src["owner_uid"], "owner_class": src.get("owner_class"),
                                 "found": loc.get("found"), "terminal": hit}
                fact("[M3a-2 (i)] #%d IS FED BY node #%s (%s) at terminal index %r name %r, wire uid %d"
                     % (luid, src["owner_uid"], src.get("owner_class"),
                        (hit or {}).get("i"), (hit or {}).get("name"), wire_uid))
            else:
                rec["feeder"] = None
                fact("[M3a-2 (i)] #%d: the wire walk returned no source owner - REPORTED, nothing inferred"
                     % luid)
        out["registers"][str(luid)] = rec
    R["m3a2"]["i_outer_left_feeds"] = out
    dump()


def m3a2_toplevel(hints):
    """(ii) Is the diagram that owns #23032 the VI's TOP-LEVEL diagram? `LeftOutNode` addresses TOP-LEVEL
    Nodes[] only, so M3a-2's route depends on this. MEASURED AND REPORTED; no route is chosen."""
    print("\n---------- [M3a-2 (ii)] IS #23032's OWNING DIAGRAM THE TOP-LEVEL DIAGRAM?", flush=True)
    diags, derr = safe("[M3a-2 (ii)] report_all('Diagram')", lambda: g.report_all(WORK, "Diagram"), [])
    zero = next((d for d in (diags or []) if d["i"] == 0), None)
    loc = find_node(WORK, LOOP_A_UID, [TOP] + list(hints), "[M3a-2 (ii)] #%d" % LOOP_A_UID)
    f = loc.get("found") or {}
    toprows, terr = safe("[M3a-2 (ii)] node_labels(0)", lambda: g.node_labels(WORK, 0), [])
    in_top = any(r["uid"] == LOOP_A_UID for r in (toprows or []))
    rec = {"loop_uid": LOOP_A_UID, "found": f, "diagram_traverse_index": f.get("diagram_index"),
           "owning_diagram_uid": f.get("diagram_uid"),
           "owning_diagram_class_verbatim": f.get("diagram_class"),
           "traverse_index_0_row": zero, "diagram_rows": len(diags or []),
           "listed_in_node_labels_0": in_top, "node_labels_0_len": len(toprows or []),
           "diagram_census_error": derr, "node_labels_0_error": terr}
    R["m3a2"]["ii_toplevel_test"] = rec
    fact("[M3a-2 (ii)] #%d is listed by Diagram traverse index %r (uid %r, class %r); traverse index 0 is "
         "%r with %d node(s); #%d in node_labels(0): %r"
         % (LOOP_A_UID, f.get("diagram_index"), f.get("diagram_uid"), f.get("diagram_class"), zero,
            len(toprows or []), LOOP_A_UID, in_top))
    fact("[M3a-2 (ii)] THE ANSWER AS A FACT: the owning diagram's traverse index is %r and index 0 is the "
         "VI's top-level diagram, so 'is #%d on the top-level diagram' reads %r. REPORTED ONLY - no route "
         "for M3a-2 is chosen or recommended here."
         % (f.get("diagram_index"), LOOP_A_UID, bool(in_top)))
    dump()


def step_m3a2(hints):
    m3a2_left_sr_feed(hints)
    m3a2_toplevel(hints)


# ======================================================= STEP 2 - two add_shift_reg pairs on #23032
def step_2():
    print("\n---------- [2] TWO `add_shift_reg` PAIRS ON #%d" % LOOP_A_UID, flush=True)
    made = {}
    for n, pair in enumerate(SR_PAIRS):
        li = loop_index_of(LOOP_A_UID, "[2] before add_shift_reg #%d (%s)" % (n + 1, pair))
        y = 120 + 90 * n
        uid, err = safe("[2] add_shift_reg(y=%d)" % y,
                        lambda ll=li, yy=y: g.add_shift_reg(WORK, ll, y_position=yy))
        fact("[2] add_shift_reg #%d for the %s pair at y=%d -> RightShiftRegister uid %r%s"
             % (n + 1, pair, y, uid, (" ; ERROR " + err) if err else ""))
        gate("2a add_shift_reg #%d (%s pair) returned a RightShiftRegister uid" % (n + 1, pair),
             bool(uid), "%r ; %s" % (uid, err), fatal=True)
        made[pair] = {"right_uid": uid, "y": y, "error_verbatim": err}
        unit_boundary("after add_shift_reg #%d (%s pair)" % (n + 1, pair))
    # THE reg_index <-> uid MAPPING IS READ, NEVER ASSUMED. Both slots are echoed whatever the answer is.
    li = loop_index_of(LOOP_A_UID, "[2] before the reg_index echo")
    for pair in SR_PAIRS:
        idx, _probes = reg_index_of(li, made[pair]["right_uid"], "[2] %s pair" % pair)
        made[pair]["reg_index"] = idx
        gate("2b the %s pair's RightShiftRegister #%r maps to a reg_index READ off the machine"
             % (pair, made[pair]["right_uid"]), idx is not None, "reg_index %r" % (idx,))
    gate("2c the two pairs resolved to DIFFERENT reg_index values",
         made[SR_PAIRS[0]].get("reg_index") is not None
         and made[SR_PAIRS[0]]["reg_index"] != made[SR_PAIRS[1]].get("reg_index"),
         "%r vs %r" % (made[SR_PAIRS[0]].get("reg_index"), made[SR_PAIRS[1]].get("reg_index")))
    fact("[2] NOTE FOR THE RECORD: both registers come back UNTYPED and with BOTH SIDES UNWIRED, so "
         "`ExecState` 0 from here on is CORRECT, NOT A FAILURE (tools/gscript.py:683-687). The names "
         "'VISA' and 'POS' are THIS RUN'S assignment of a pair to a row set, recorded before the rows are "
         "written; the terminal NAMES read off the machine below are what justify each row's membership.")
    K["shift_registers"] = made
    K["counts_after_add"] = counts(WORK, "[2] after the two add_shift_reg calls")
    dump()
    return made


# ================================================================= STEP 3 - the seven `move_in` calls
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
    """THE AUTHORITATIVE GATE: Diagram #23058's own Nodes[] census, by uid."""
    idx, err = safe("%s diag_index(#%d)" % (tag, BODY_A_UID), lambda: diag_index(WORK, BODY_A_UID))
    if idx is None:
        fact("%s Diagram #%d could not be resolved: %s" % (tag, BODY_A_UID, err))
        return [], idx
    rows, lerr = safe("%s node_labels(%r)" % (tag, idx), lambda: g.node_labels(WORK, idx), [])
    uids = [r["uid"] for r in (rows or [])]
    fact("%s Diagram #%d [traverse %r] Nodes[] census: %d node(s) -> %r%s"
         % (tag, BODY_A_UID, idx, len(uids), uids, (" ; " + lerr) if lerr else ""))
    return uids, idx


def step_3(hints):
    print("\n---------- [3] THE SEVEN `move_in` CALLS, VERBATIM FROM diag_c66b_s3b_m3.py (37(d) severs "
          "every wire)", flush=True)
    before_uids, bidx = body_a_node_uids("[3] BEFORE")
    K["body_a_before"] = before_uids
    nodes = K["node_census_before"]
    after_hints = [bidx, hints[0], TOP]
    for uid, name, pos, why in SET:
        _loc, rows = node_view(WORK, uid, hints, "[3] #%d BEFORE" % uid, quiet=True)
        fact("[3] #%d %r BEFORE the move: %d terminal(s), %d WIRED  (%s)"
             % (uid, name, len(rows), wired_count(rows), why))
        bi = resolve_dest("[3] before move #%d" % uid)
        rec = {"uid": uid, "name": name, "dest_diagram_uid": BODY_A_UID, "dest_index_used": bi,
               "position": list(pos), "wired_before": wired_count(rows), "n_terms_before": len(rows)}
        try:
            rec["echoed_uid"] = move_in(WORK, uid, bi, pos)
            rec["error_verbatim"] = ""
            fact("[3] MOVE #%d %r -> Diagram #%d [traverse %r] at %r; the op echoed uid %r (37(d): the echo "
                 "is NOT the moved object)" % (uid, name, BODY_A_UID, bi, pos, rec["echoed_uid"]))
        except Exception as e:                                                     # noqa: BLE001
            rec["echoed_uid"] = None
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            fact("[3] MOVE #%d RAISED %s" % (uid, rec["error_verbatim"]))
        nodes, _p = census_and_purge(WORK, nodes, "[3] after move #%d" % uid, after_hints)
        after_uids, _ = body_a_node_uids("[3] after move #%d" % uid)
        rec["in_body_a_nodes"] = uid in after_uids
        gate("3a #%d appears in Diagram #%d's Nodes[] census (THE authoritative gate)" % (uid, BODY_A_UID),
             rec["in_body_a_nodes"], "body has %d node(s)" % len(after_uids))
        own, oerr = safe("[3] owner_of(%d) after the move" % uid, lambda u=uid: owner_of(WORK, u))
        rec["owner_of_after"] = list(own) if own else None
        rec["owner_of_error"] = oerr
        fact("[3] owner_of(%d) AFTER the move = %r (REPORTED ALONGSIDE, never the gate - 53(d^8))"
             % (uid, own))
        _l2, rows2 = node_view(WORK, uid, after_hints, "[3] #%d AFTER" % uid, quiet=True)
        rec["wired_after"] = wired_count(rows2)
        rec["n_terms_after"] = len(rows2)
        fact("[3] #%d AFTER the move: %d terminal(s), %d WIRED (was %d)"
             % (uid, len(rows2), wired_count(rows2), rec["wired_before"]))
        rec["exec_state_after"] = unit_boundary("after move #%d %s" % (uid, name))
        K.setdefault("moves", []).append(rec)
        dump()

    final_uids, _ = body_a_node_uids("[3] AFTER all seven")
    K["body_a_after_moves"] = final_uids
    missing = [u for u in SET_UIDS if u not in final_uids]
    gate("3b *** ALL SEVEN MOVED UIDS ARE IN Diagram #%d's Nodes[] CENSUS ***" % BODY_A_UID, not missing,
         "missing %r ; body now holds %d node(s)" % (missing, len(final_uids)))
    K["node_census_after_moves"] = nodes
    K["counts_after_moves"] = counts(WORK, "[3] after the seven moves")
    dump()
    return nodes, not missing, after_hints


# ================================================================ STEP 4 - the seven internal rows
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


def step_4(nodes, hints):
    print("\n---------- [4] THE SEVEN INTERNAL ROWS, VERBATIM FROM diag_c66b_s3b_m3.py", flush=True)
    for sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why in INTERNAL_JOBS:
        job = {"sink_uid": sink_uid, "sink_name": sink_name, "sink_t_recorded": sink_t,
               "src_uid": src_uid, "src_name": src_name, "src_t_recorded": src_t, "evidence": why}
        if left_s() < ROW_MIN_S:
            job["result"] = "NOT STARTED - only %.0f s left before the reserve" % left_s()
            gate("4 row #%d t%d <- #%d: there is enough wall-clock left to start it"
                 % (sink_uid, sink_t, src_uid), False, job["result"])
            K.setdefault("rows", []).append(job)
            dump()
            continue
        sloc, srows = node_view(WORK, sink_uid, hints, "[4] sink #%d" % sink_uid, quiet=True)
        rloc, rrows = node_view(WORK, src_uid, hints, "[4] src  #%d" % src_uid, quiet=True)
        job["sink_wired_before"] = wired_count(srows)
        job["src_wired_before"] = wired_count(rrows)
        job["sink_terminals_before"] = srows
        job["src_terminals_before"] = rrows
        si, show = resolve_term(srows, sink_name, sink_t, False, "[4] sink #%d" % sink_uid)
        ri, rhow = resolve_term(rrows, src_name, src_t, True, "[4] src #%d" % src_uid)
        job["sink_term_resolution"] = show
        job["src_term_resolution"] = rhow
        sd = (sloc.get("found") or {}).get("diagram_index")
        sn = (sloc.get("found") or {}).get("nodes_index")
        rd = (rloc.get("found") or {}).get("diagram_index")
        rn = (rloc.get("found") or {}).get("nodes_index")
        job["addr"] = {"sink_diag": sd, "sink_node": sn, "sink_term": si,
                       "src_diag": rd, "src_node": rn, "src_term": ri}
        fact("[4] row #%d t%r <- #%d t%r : %r ; sink %s ; src %s"
             % (sink_uid, si, src_uid, ri, job["addr"], show, rhow))
        same_diag = (sd is not None and sd == rd)
        job["same_nested_diagram"] = same_diag
        if None in (si, ri, sn, rn) or not same_diag:
            job["result"] = "NOT ADDRESSABLE" if None in (si, ri, sn, rn) else "NOT ON ONE NESTED DIAGRAM"
            gate("4 row #%d t%r <- #%d t%r is addressable on ONE nested diagram"
                 % (sink_uid, sink_t, src_uid, src_t), False, "%r ; %s" % (job["addr"], job["result"]))
            K.setdefault("rows", []).append(job)
            dump()
            continue
        try:
            dw, es, err = CONNECT_V1(WORK, sd, sn, si, rd, rn, ri, V1_LABELS)
            job["connect"] = {"wire_delta": dw, "exec_state": es, "machine_error": str(err)[:200]}
        except Exception as e:                                                     # noqa: BLE001
            job["connect"] = {"exception": "%s: %s" % (type(e).__name__, str(e)[:250])}
        fact("[4] connect_nested_v1 -> %r" % (job["connect"],))
        nodes, _p = census_and_purge(WORK, nodes, "[4] after row #%d t%r" % (sink_uid, si), hints)
        _l3, srows2 = node_view(WORK, sink_uid, hints, "[4] sink #%d AFTER" % sink_uid, quiet=True)
        _l4, rrows2 = node_view(WORK, src_uid, hints, "[4] src  #%d AFTER" % src_uid, quiet=True)
        job["sink_wired_after"] = wired_count(srows2)
        job["src_wired_after"] = wired_count(rrows2)
        srow = next((t for t in srows2 if t["i"] == si), None)
        rrow = next((t for t in rrows2 if t["i"] == ri), None)
        job["same_wire_uid"] = bool(srow and rrow and srow["wire"] and srow["wire"] == rrow["wire"])
        job["wire_uid"] = (srow or {}).get("wire")
        fact("[4] row #%d t%r <- #%d t%r : sink wire %r / src wire %r ; same net %r ; WIRED-TERMINAL counts "
             "sink %d -> %d, src %d -> %d"
             % (sink_uid, si, src_uid, ri, (srow or {}).get("wire"), (rrow or {}).get("wire"),
                job["same_wire_uid"], job["sink_wired_before"], job["sink_wired_after"],
                job["src_wired_before"], job["src_wired_after"]))
        gate("4 row #%d t%r <- #%d t%r: the WIRED-TERMINAL count rose on BOTH ends and they share ONE wire "
             "uid (49(e))" % (sink_uid, si, src_uid, ri),
             job["same_wire_uid"] and job["sink_wired_after"] > job["sink_wired_before"]
             and job["src_wired_after"] > job["src_wired_before"],
             "wire %r" % (job["wire_uid"],))
        job["exec_state_after"] = unit_boundary("after row #%d t%r <- #%d t%r" % (sink_uid, si, src_uid, ri))
        K.setdefault("rows", []).append(job)
        dump()
    return nodes


# ============================== STEPS 5 and 7 - THE CENSUS. Unconditional, whatever ExecState says.
def census(tag, slot, hints, include_registers=False):
    """THE MEASUREMENT THIS DISPATCH EXISTS FOR. For EACH of the seven moved nodes (and, when asked, both
    shift registers) the FULL terminal table - EVERY terminal, not a selection - printed AND dumped, plus
    the derived BARE list: every terminal whose WireUID is 0. It runs whatever ExecState says."""
    print("\n---------- [%s] FULL `node_terms` CENSUS OF THE SEVEN MOVED NODES%s"
          % (tag, " PLUS BOTH SHIFT REGISTERS" if include_registers else ""), flush=True)
    rec = {"tag": tag, "exec_state_at_census": read_es("[%s] at the census" % tag, WORK),
           "nodes": {}, "bare": [], "registers": {}}
    for uid, name, _pos, _why in SET:
        loc, rows = node_view(WORK, uid, hints, "[%s] #%d %s" % (tag, uid, name))
        entry = {"uid": uid, "name": name, "found": loc.get("found"),
                 "uid_echo": loc.get("uid_echo"), "n_terminals": len(rows),
                 "n_wired": wired_count(rows), "terminals": rows}
        rec["nodes"][str(uid)] = entry
        for t in rows:
            if not t.get("wire"):
                rec["bare"].append({"node_uid": uid, "node_name": name, "term_index": t.get("i"),
                                    "term_name": t.get("name"), "is_source": t.get("is_source"),
                                    "wire": t.get("wire"), "errs": t.get("errs"),
                                    "state": term_state(t)})
        fact("[%s] #%d %r: %d terminal(s), %d WIRED, %d with WireUID 0"
             % (tag, uid, name, len(rows), wired_count(rows),
                sum(1 for t in rows if not t.get("wire"))))
    if include_registers:
        li = loop_index_of(LOOP_A_UID, "[%s] before the register read" % tag)
        for pair in SR_PAIRS:
            ri = (K.get("shift_registers") or {}).get(pair, {}).get("reg_index")
            if ri is None:
                rec["registers"][pair] = {"reg_index": None, "note": "no reg_index was resolved in step 2"}
                fact("[%s] the %s pair has no resolved reg_index - REPORTED" % (tag, pair))
                continue
            srl, err = safe("[%s] shift_reg_left(%s)" % (tag, pair),
                            lambda rr=ri: g.shift_reg_left(WORK, li, rr, 0))
            rec["registers"][pair] = {"reg_index": ri, "read": srl, "error_verbatim": err}
            fact("[%s] %s pair reg_index %d -> right #%r out %r inside %r ; left #%r out %r inside %r"
                 % (tag, pair, ri, (srl or {}).get("uid"), (srl or {}).get("out"), (srl or {}).get("inside"),
                    ((srl or {}).get("left") or {}).get("uid"), ((srl or {}).get("left") or {}).get("out"),
                    ((srl or {}).get("left") or {}).get("inside")))
            for side, d in (("right", srl or {}), ("left", (srl or {}).get("left") or {})):
                for where, t in [("outer", (d.get("out") or {}))] + \
                        [("inside", x) for x in (d.get("inside") or [])]:
                    if not t.get("wire"):
                        rec["bare"].append({"node_uid": d.get("uid"), "node_name": "%s SR %s %s"
                                                                                  % (pair, side, where),
                                            "term_index": None, "term_name": t.get("name"),
                                            "is_source": t.get("is_source"), "wire": t.get("wire"),
                                            "errs": None, "state": "BARE (WireUID 0)"})
    print("\n  *** [%s] THE BARE LIST - EVERY TERMINAL WITH WireUID 0 (%d row(s)) ***"
          % (tag, len(rec["bare"])), flush=True)
    for b in rec["bare"]:
        fact("[%s] BARE  node #%-6r %-26r t%-4r %-34r is_source=%-5r state=%s"
             % (tag, b["node_uid"], b["node_name"], b["term_index"], b["term_name"], b["is_source"],
                b["state"]))
    fact("[%s] BARE LIST SIZE: %d terminal(s) with WireUID 0" % (tag, len(rec["bare"])))
    # THE PART A PEER'S PREDICTION, SCORED. REPORTED ONLY - never a gate, and nothing branches on it.
    per_node = {}
    for b in rec["bare"]:
        if b["node_uid"] in SET_UIDS:
            per_node[str(b["node_uid"])] = per_node.get(str(b["node_uid"]), 0) + 1
    score = {str(u): {"predicted": PEER_PREDICTION.get(str(u)), "measured": per_node.get(str(u), 0)}
             for u in SET_UIDS}
    named = next((b for b in rec["bare"]
                  if b["node_uid"] == PEER_PREDICTION_NAMED_BARE[0]
                  and b["term_index"] == PEER_PREDICTION_NAMED_BARE[1]), None)
    rec["peer_prediction_score"] = {
        "source": "archive/peer/2026-09-21-c67-m3a-srrows.md sec.4 (claude/hypothesis, opus/max, ANSWERED)",
        "per_node": score, "exec_state_predicted": PEER_PREDICTION_EXEC_STATE,
        "exec_state_measured": rec["exec_state_at_census"],
        "named_bare_terminal_predicted": list(PEER_PREDICTION_NAMED_BARE),
        "named_bare_terminal_measured": named,
        "matches": all(v["predicted"] == v["measured"] for v in score.values())}
    fact("[%s] PEER PREDICTION SCORED (REPORTED, never a gate): per-node bare counts predicted/measured "
         "%r ; ExecState predicted %r measured %r ; the named row #%d t%d %r measured as %r ; all per-node "
         "counts match: %r"
         % (tag, score, PEER_PREDICTION_EXEC_STATE, rec["exec_state_at_census"],
            PEER_PREDICTION_NAMED_BARE[0], PEER_PREDICTION_NAMED_BARE[1], PEER_PREDICTION_NAMED_BARE[2],
            named, rec["peer_prediction_score"]["matches"]))
    R[slot] = rec
    dump()
    return rec


# ======================================================================= STEP 6 - the four SR rows
def step_6(made, hints):
    print("\n---------- [6] THE FOUR SHIFT-REGISTER ROWS", flush=True)
    results = []
    for pair, variant, node_uid, term_name, term_i, node_is_source in SR_JOBS:
        job = {"pair": pair, "variant": variant, "node_uid": node_uid,
               "term_name_recorded": term_name, "term_index_recorded": term_i,
               "node_terminal_is_source": node_is_source,
               "reg_index": (made.get(pair) or {}).get("reg_index"),
               "right_reg_uid": (made.get(pair) or {}).get("right_uid")}
        if job["reg_index"] is None:
            job["result"] = "NO reg_index - the row is NOT attempted"
            gate("6 %s %s row on #%d has a reg_index" % (pair, variant, node_uid), False, job["result"])
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        # The node/terminal indices are read with node_terms_uid on #23032's body diagram IMMEDIATELY
        # before the call - never carried from an earlier step.
        bidx, berr = safe("[6] diag_index(#%d)" % BODY_A_UID, lambda: diag_index(WORK, BODY_A_UID))
        brows, lerr = safe("[6] node_labels(%r)" % bidx, lambda: g.node_labels(WORK, bidx), [])
        nidx = next((k for k, r in enumerate(brows or []) if r["uid"] == node_uid), None)
        job["body_diagram_index"] = bidx
        job["body_nodes_index"] = nidx
        job["body_nodes_len"] = len(brows or [])
        job["addr_errors"] = [berr, lerr]
        if nidx is None:
            job["result"] = "#%d IS NOT IN Diagram #%d's Nodes[] - the row is NOT attempted" \
                            % (node_uid, BODY_A_UID)
            gate("6 %s %s: #%d is in Diagram #%d's Nodes[]" % (pair, variant, node_uid, BODY_A_UID),
                 False, job["result"])
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        tt = terms_at(WORK, bidx, nidx, node_uid, "[6] %s %s #%d" % (pair, variant, node_uid))
        rows = tt.get("terminals", [])
        job["node_terminals_before"] = rows
        ti, how = resolve_term(rows, term_name, term_i, node_is_source,
                               "[6] %s %s #%d" % (pair, variant, node_uid))
        job["term_resolution"] = how
        job["term_index_used"] = ti
        fact("[6] %s %s row: node #%d at Nodes[%d] of Diagram #%d [traverse %r], terminal %r resolved %s"
             % (pair, variant, node_uid, nidx, BODY_A_UID, bidx, ti, how))
        if ti is None:
            job["result"] = "TERMINAL UNRESOLVED - the row is NOT attempted"
            gate("6 %s %s row on #%d resolves its terminal" % (pair, variant, node_uid), False,
                 job["result"])
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        li = loop_index_of(LOOP_A_UID, "[6] before wire_sr(%s, %s)" % (variant, pair))
        job["reg_uid_echo"] = echo_reg_uid(li, job["reg_index"], job["right_reg_uid"],
                                           "[6] before wire_sr(%s, %s)" % (variant, pair))
        nodes_before, _ = node_census(WORK, "[6] before wire_sr(%s, %s)" % (variant, pair))
        t0 = time.time()
        try:
            g.wire_sr(variant, WORK, li, job["reg_index"], node_index=nidx, term_index=ti)
            job["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            job["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        job["call_cost_s"] = round(time.time() - t0, 2)
        fact("[6] wire_sr(%r, loop_index=%r, reg_index=%r, node_index=%r, term_index=%r) -> error %r (%.2f s)"
             % (variant, li, job["reg_index"], nidx, ti, job["error_verbatim"], job["call_cost_s"]))
        census_and_purge(WORK, nodes_before, "[6] after wire_sr(%s, %s)" % (variant, pair), hints)
        # VERIFY BY WIRE UID AT BOTH ENDS.
        tt2 = terms_at(WORK, bidx, nidx, node_uid, "[6] %s %s #%d AFTER" % (pair, variant, node_uid),
                       quiet=True)
        after_row = next((t for t in tt2.get("terminals", []) if t["i"] == ti), None)
        job["node_terminal_after"] = after_row
        node_wire = (after_row or {}).get("wire") or 0
        srl, serr = safe("[6] shift_reg_left after the row",
                         lambda: g.shift_reg_left(WORK, li, job["reg_index"], 0))
        job["register_after"] = srl
        job["register_read_error"] = serr
        if variant == "LeftIn":
            side = ((srl or {}).get("left") or {}).get("inside") or []
            side_label = "the LEFT register's INSIDE terminal"
        else:
            side = (srl or {}).get("inside") or []
            side_label = "the RIGHT register's INSIDE terminal"
        reg_wires = [t.get("wire") for t in side]
        job["register_side_wires"] = reg_wires
        job["node_wire_uid"] = node_wire
        same = bool(node_wire) and node_wire in reg_wires
        job["same_wire_uid_both_ends"] = same
        fact("[6] %s %s VERIFY BY WIRE UID: node #%d t%r carries wire %r ; %s carries %r ; SAME NET %r"
             % (pair, variant, node_uid, ti, node_wire, side_label, reg_wires, same))
        gate("6 *** %s %s row #%d t%r <-> reg_index %r: ONE non-zero wire uid at BOTH ends ***"
             % (pair, variant, node_uid, ti, job["reg_index"]), same,
             "node wire %r ; register side wires %r ; call error %r"
             % (node_wire, reg_wires, job["error_verbatim"]))
        job["exec_state_after"] = unit_boundary("after the %s %s row on #%d" % (pair, variant, node_uid))
        results.append(job)
        K.setdefault("sr_rows", []).append(job)
        dump()
    fact("[6] NOT CALLED, DELIBERATELY OUT OF SCOPE: wire_sr('LeftOutNode') and wire_sr('LeftOutCtl') - the "
         "registers' INITIAL VALUES are STAGE M3a-2. An uninitialised register is legal LabVIEW and the "
         "initial values are a rule-1a question, not a compile question.")
    return results


# ============================================== STEP 8 - ExecState, the save, the restart, Broken? LAST
def step_8(all_moved, hints):
    print("\n---------- [8] ExecState, AND THE SAVE ONLY IF IT READS 1", flush=True)
    es = read_es("[8] the decision point", WORK)
    K["counts_final"] = counts(WORK, "[8] final, in memory")
    _l, lrows = node_view(WORK, LOOP11_UID, hints, "[8] #%d the WhileLoop" % LOOP11_UID, quiet=True)
    K["loop637_after"] = {"n_terms": len(lrows), "n_wired": wired_count(lrows)}
    gate("8a #%d's terminal/wired counts are UNCHANGED at %d / %d (37(e)/50(e))"
         % (LOOP11_UID, LOOP637_TERMS_RECORDED, LOOP637_WIRED_RECORDED),
         K["loop637_after"] == K.get("loop637_before"),
         "%r -> %r" % (K.get("loop637_before"), K["loop637_after"]))
    ok = bool(all_moved) and es == 1
    gate("8b *** THE PASS CRITERION: all seven in Diagram #%d's Nodes[] AND ExecState 1 ***" % BODY_A_UID,
         ok, "all_moved %r ; ExecState %r" % (all_moved, es))
    if not ok:
        fact("[8] ExecState %r - SAVE NOTHING. CENSUS 2 above has already named every bare terminal; that "
             "is the report. No retry, no substituted verb, no invented row. `allow_broken` is never set "
             "and `gui_save` is never called." % (es,))
        return None
    rec = save_artefact("[8] the M3a-1 artefact", FINAL_PATH, BED_MD5, "the bed")
    D.fresh("[8] LabVIEW RESTART before the COLD reopen")
    R["handles"]["after_final_restart"] = labview_handles()
    es_cold = read_es("[8] COLD, after the restart", FINAL_PATH)
    K["exec_state_cold"] = es_cold
    gate("8c *** the saved artefact reopens COLD at ExecState 1 ***", es_cold == 1, "%r" % (es_cold,))
    K["counts_cold"] = counts(FINAL_PATH, "[8] COLD")
    # THE ORDERED `Broken?` PASS, LAST OF ALL (42(b)/52(f)) - never above a save point.
    print("\n---------- [8d] THE ORDERED `Broken?` PASS, LAST OF ALL (42(b)/52(f))", flush=True)
    br, berr = safe("[8d] report_all('Wire') for the ordered Broken? pass",
                    lambda: g.report_all(FINAL_PATH, "Wire"), [])
    K["cold_wire_rows"] = len(br or [])
    fact("[8d] COLD Wire census: %d row(s)%s" % (len(br or []), (" ; " + berr) if berr else ""))
    vb, verr = safe("[8d] exec_state(FINAL) second ordered read", lambda: g.exec_state(FINAL_PATH))
    K["exec_state_cold_second"] = vb
    fact("[8d] the SECOND ordered ExecState read on the cold artefact = %r%s (52(f): the type checker "
         "answers only on a second ordered pass)" % (vb, (" ; " + verr) if verr else ""))
    gate("8d the second ordered read on the cold artefact also reads ExecState 1", vb == 1, "%r" % (vb,))
    safe("[8] close_panel(final)", lambda: g.close_panel(FINAL_PATH))
    return rec


# ======================================================================= main
def main():
    print("=== diag_c67_m3a  %s  (bgrun --material --max-min 40)" % STAMP, flush=True)
    print("=== STAGE M3a-1. THE ARTEFACT THIS RUN MAY SAVE IS **NOT COMPUTATION-EQUIVALENT TO THE "
          "ORIGINAL** - ITS SHIFT REGISTERS ARE UNINITIALISED (initial values = stage M3a-2). "
          "IT IS NEVER RUN (34(f)).", flush=True)
    all_moved = False
    hints = [D639_RECORDED, TOP]
    try:
        phase_0()
        hints = step_1()
        if left_s() < M3_MIN_S:
            gate("M0 there is enough wall-clock left to start the build", False,
                 "only %.0f s left before the reserve; the build needs %.0f s" % (left_s(), M3_MIN_S))
            raise Stop("no wall-clock for the build")
        gate("M0 there is enough wall-clock left to start the build", True,
             "%.0f s left before the reserve" % left_s())
        made = step_2()
        nodes, all_moved, after_hints = step_3(hints)
        hints = after_hints
        step_4(nodes, hints)
        census("CENSUS 1", "census_1", hints, include_registers=False)
        step_6(made, hints)
        census("CENSUS 2", "census_2", hints, include_registers=True)
        step_8(all_moved, hints)
    except Stop as e:
        fact("STOP: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        R["unexpected_exception"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("UNEXPECTED EXCEPTION: %s" % R["unexpected_exception"])
    finally:
        safe("close_panel(WORK)", lambda: g.close_panel(WORK))
        if os.path.exists(WORK):
            safe("remove the working copy", lambda: os.remove(WORK))
        gate("Y scratch %s is gone (exists=False)" % os.path.basename(WORK), not os.path.exists(WORK), "")
        print("\n---------- [Y] THE SIX md5 PINS AFTER, THE REFS AND THE HANDLES", flush=True)
        for tag, path, pin in PINS:
            pr = probe("Y %s AFTER" % tag, path)
            gate("Y %s md5 is STILL its pin %s" % (tag, pin[:8]), pr.get("md5") == pin,
                 "%r" % (pr.get("md5"),))
        rc = g.ref_counts()
        R["ref_counts"] = rc
        fact("refs: %r" % (rc,))
        gate("Y refs opened == closed and 0 live", rc.get("live") == 0, "%r" % (rc,))
        R["handles"]["after"] = labview_handles()
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"]["after"], R["handles"].get("before")))
        left = [(os.path.basename(a["dest"]), a.get("md5"), a.get("size"))
                for a in R["artefacts_on_disk"]]
        R["files_left_on_disk"] = left
        print("\nTHE FILES THIS RUN LEFT ON DISK: %r" % (left,), flush=True)
        fact("THE FILES THIS RUN LEFT ON DISK: %r" % (left,))
        if left:
            fact("*** EVERY FILE NAMED ABOVE IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL - ITS SHIFT "
                 "REGISTERS ARE UNINITIALISED. NONE OF THEM IS EVER RUN (34(f)). ***")
        dump()
        print("\n=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                    ("; failing: " + ", ".join(fails)) if fails else ""),
              flush=True)
        print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
