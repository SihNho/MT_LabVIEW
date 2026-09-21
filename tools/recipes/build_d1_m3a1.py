"""build_d1_m3a1 - CYCLE 68 material #1: STAGE M3a-1, THE DELIVERABLE BUILD.

A RECIPE (it SAVES an artefact), gated by `py tools/bench/c60c_astcheck.py --route movein` BEFORE launch -
`--route movein` because this file calls `move_in` (Pre-decided 62: the route declares what the FILE DOES).

WHAT ALREADY EXISTS AND IS REUSED, NOT REBUILT. Checked before a line was written:
`docs/toolkit-capabilities.md`, `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`.
  - `tools/gscript.py:673` `add_shift_reg` and `:723` `wire_sr` - the BUILT register creator / one-side writer,
    REPAIRED in cycle 67 (`ensure_loaded` at :708 and :750; `tools/bench/selftest_c67_ensureloaded.log` 4/4).
  - `tools/gscript.py:769` `shift_reg` / `:802` `shift_reg_left` - the BUILT register readers.
  - `tools/gscript.py:957` `tunnels` - the BUILT LoopTunnel reader (outer terminal name / wire).
  - `tools/recipes/build_d1_v0.py:318` `move_in` / `:338` `owner_of` / `:357` `diag_index`.
  - `tools/recipes/build_opconnectnested_v1.py:418` `connect_nested_v1` - the BUILT node->node writer.
  - `tools/recipes/build_opconnectfromwire_v0.py:423` `wire_source_owner` - the ONLY BY-UID walk of a WIRE's
    own `Terms[]`, giving each endpoint's OWNER class and uid.
  - `tools/bench/diag_c66b_s3b_m3.py:183-193` (`SET`) and `:200-210` (`INTERNAL_JOBS`) - THE SEVEN MOVES AND
    THE SEVEN INTERNAL ROWS ARE COPIED VERBATIM FROM THERE, same order, same addressing, NOT re-derived.
  - `tools/bench/diag_c67_m3a.py` - every helper below (gate/fact/probe/dump/safe/read_es/counts/node_census/
    terms_at/term_state/find_node/node_view/delete_by_uid/census_and_purge/save_artefact/unit_boundary/
    loop_index_of/echo_reg_uid/reg_index_of/resolve_term/resolve_dest/body_a_node_uids/census) is reused IN
    SHAPE from it. NO new op, NO new verb, NO edit to `tools/gscript.py`, NO edit to any `*_astcheck.py`.

THE BED  `claudeDev\\D1_s3b_row2_20260921_160311.vi`, md5 26c54ff784cb5cea21edbd214d2cc3a0, 476,759 B.
  READ-ONLY, md5-pinned BEFORE and AFTER, never overwritten. All work happens on fresh stamped copies.

THE ORDER IS FIXED BY THE BRIEF (Pre-decided 59/60/61/62/63) AND IS NOT RE-ORDERED HERE:
  [0] restart, handles, the four md5 pins (+ the two TOOL pins: gscript.py and c60c_astcheck.py).
  [1] THE PROBE, ON A SCRATCH COPY, DELETED IN THE SAME STEP (Pre-decided 61). Is there an ADDRESSABLE
      SOURCE on `Diagram #686` for the net that feeds `#10407` t1 `'# slices in stack'` today - today
      `FlatSequenceInnerTunnel #9655` -> wire 9649 -> `LoopTunnel #9641` (diag_c67_addsr.log:390-392)?
      `connect_nested_v1` addresses (diagram index, Nodes[] index, terminal index), so a source is
      ADDRESSABLE only if it is a NODE listed in a diagram's `Nodes[]`. MEASURED, never inferred. The
      auto-tunnelling question can only be answered where the sink actually lives, so if a node source IS
      found the attempt is made IN SITU at step [5] and the `LoopTunnel` / `#23032`-terminal deltas measured
      around it; the baselines for that delta are taken here. NEVER a Local for this row (rule 1a).
  [2] copy the bed to WORK; the seven `move_in`s and the seven internal rows, VERBATIM from c66b.
  [3] `add_shift_reg` x2 on `#23032` with the repaired wrapper. PREDICTION: real uids are minted and
      `ExecState` goes 1 -> 0 (tools/gscript.py:683-687) - an unwired new register breaks the VI, and that
      is CORRECT, NOT A FAILURE. The minted uids and the `shift_reg` / `loop_cast` readback are recorded.
  [4] THE FOUR SR ROWS, **RightIn BEFORE LeftIn** (an untyped register takes the type of its first wire, and
      `#10407` t4 / t6 are the SOURCES): `#10407` t4 `'VISA out'`, `#10407` t6 `'position [internal units]'`,
      `#48` t3 `'VISA resource name'`, `#48` t4 `'In position'`. Verified BY WIRE UID AT BOTH ENDS.
  [5] THE FIFTH ROW, `#10407` t1, per step [1]'s measurement. If no addressable source exists on `#686`:
      that is a FACT line, nothing is wired there, nothing is substituted, and the run CARRIES ON.
  [6] THE FULL WIRED-TERMINAL CENSUS of all seven moved nodes plus both registers, same shape as
      `tools/bench/diag_c67_m3a.log:481-486`. Unconditional, whatever `ExecState` says.
  [7] `ExecState`. 1 => save `claudeDev\\D1_s3b_m3a_<stamp>.vi`, RESTART, COLD reopen, ordered `Broken?`
      read LAST (42(b)/52(f)). 0 => the brief asks for `claudeDev\\D1_s3b_m3a_BROKEN_<stamp>.vi`; the save is
      ATTEMPTED and whatever the machine answers is recorded VERBATIM. `tools/gscript.py:2087-2090` refuses a
      broken VI and its only bypasses (`allow_broken`, the GUI save) are FORBIDDEN by this brief, so if the
      refusal comes back the file is NOT written and that is reported as the one open question. A broken
      artefact, if one ever lands, is NOT a deliverable, is NEVER run (34(f)) and is NEVER used as a bed.

*** THE M3a-1 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL, EITHER WAY: ITS SHIFT REGISTERS ARE
    UNINITIALISED (initial values are stage M3a-2, a rule-1a matter). IT IS NEVER RUN (34(f)). ***

GATING POLICY - Pre-decided 63: THIS RUN GATES ON **HYGIENE ONLY** and exits 0 when hygiene passes.
  H  the md5 pins hold before and after; the bed keeps its size; the working copy starts byte-identical to
     the bed; `tools/gscript.py` and `tools/bench/c60c_astcheck.py` are byte-identical before and after;
     every scratch is `exists=False` at the end; refs opened == closed == 0 live; handles read either side;
     and NO mutator call was REFUSED BY THE MACHINE (a raised wrapper error is a refusal and IS a gate; a
     measurement that comes back negative is a FACT line and is NOT).
  Everything else - moves, rows, registers, `ExecState`, the save - is reported as FACT lines.

NO whole-VI `GObject` census anywhere (six of them took handles 34,602 -> 91,288); only the narrow classes
`Node` / `Wire` / `Tunnel` / `LoopTunnel` / `LeftShiftRegister` / `RightShiftRegister` / `ControlTerminal` /
`Local` are counted. FORBIDDEN AND ABSENT: `remove_bad_wires*` (banned since cycle 58), the broken-VI save
bypass, the GUI save, any GUI action, any new op or verb, any edit to `tools/gscript.py` or a `*_astcheck.py`,
running any deliverable VI (34(f)), motor / ASI / camera (rig ASSEMBLED), any new process device,
`retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` (54(a)),
and any edit to `docs/cycle27-plan.md` or STATUS's `## NEXT`. `CYCLE_GUARD_OFF` is never set.
No route is chosen here and none is recommended. VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)).
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
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
BED_SIZE = 476759

# THE FOUR md5 PINS THE BRIEF NAMES, checked BEFORE and AFTER.
PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5), ("S1 D1_s1_copy", S1_ARTEFACT, S1_MD5),
        ("S2 D1_s2_loops", S2_ARTEFACT, S2_MD5), ("THE BED", BED, BED_MD5))
# THE TWO TOOL PINS - "the forbidden list untouched", measured rather than asserted.
TOOL_PINS = (os.path.join(ROOT, "tools", "gscript.py"),
             os.path.join(BENCH, "c60c_astcheck.py"))

TOP = 0
D639 = 639                       # the nested diagram the loop-1.5 set lives on today
D639_RECORDED = 46
D639_NODES_RECORDED = 75
D686 = 686                       # the diagram that carries #637 and #23032
D686_RECORDED = 19               # diag_c67_addsr.log:381 - ECHOED here, never trusted as a constant
LOOP_A_UID = 23032               # the NEW While Loop; docs/cycle27-plan.md:951 - CITED, never re-derived
BODY_A_UID = 23058               # its body diagram, the destination of every move
LOOP11_UID = 637                 # the ORIGINAL While Loop that owns Diagram #639
LOOP637_TERMS_RECORDED = 59
LOOP637_WIRED_RECORDED = 48

SUBVI_UID = 48                   # ASI_adjust focus-subvi.vi
CASE_UID = 10407                 # the autofocus CaseStructure
LOCAL_ROW1_UID = 23499
LOCAL_ROW2_UID = 23523

# THE t1 NET, as diag_c67_addsr.log:390-392 measured it. Re-measured on the scratch at step [1].
T1_TERM_NAME = "# slices in stack"
T1_TERM_INDEX = 1
T1_LOOP_TUNNEL = 9641            # the LoopTunnel on #637 that carries the value in today
T1_OUTER_WIRE = 9649             # its OUTER-side wire
T1_OUTER_SOURCE = 9655           # that wire's source owner: a FlatSequenceInnerTunnel, NOT a Nodes[] entry

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

# THE FOUR SR ROWS, **RightIn BEFORE LeftIn** (Pre-decided 59: the SOURCES type the register).
# variant RightIn -> the node terminal is a SOURCE (the right register's INSIDE terminal is the sink)
# variant LeftIn  -> the node terminal is a SINK   (the left register's INSIDE terminal is the source)
# (pair, variant, node_uid, term_name, term_index, node_term_is_source)
SR_JOBS = [
    ("VISA", "RightIn", CASE_UID, "VISA out", 4, True),
    ("POS", "RightIn", CASE_UID, "position [internal units]", 6, True),
    ("VISA", "LeftIn", SUBVI_UID, "VISA resource name", 3, False),
    ("POS", "LeftIn", SUBVI_UID, "In position", 4, False),
]
SR_PAIRS = ("VISA", "POS")

SCAN_LIMIT = 60                  # nodes scanned on #686 during the probe (24 measured there)
REG_PROBE_MAX = 8
RUN_DEADLINE_S = 45 * 60.0       # the bgrun --max-min this file is launched under
RESERVE_S = 420.0                # held back for the save, the restart and the cold reopen
BUILD_MIN_S = 600.0
ROW_MIN_S = 150.0

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "build_d1_m3a1.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C68PROBE_%s.vi" % STAMP)
WORK = os.path.join(g.CLAUDEDEV, "WORK_C68M3A1_%s.vi" % STAMP)
FINAL_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a_%s.vi" % STAMP)
BROKEN_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a_BROKEN_%s.vi" % STAMP)

T_START = time.time()
passes, fails, facts, refusals = [], [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 68 material #1: STAGE M3a-1 - the t1 addressability probe on a scratch, the seven "
             "move_in calls and seven internal rows VERBATIM from diag_c66b_s3b_m3.py, two add_shift_reg "
             "pairs on #23032 with the repaired wrapper, the four SR rows RightIn-before-LeftIn, the fifth "
             "row per the probe, the full wired-terminal census, and the save",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "gating_policy": "Pre-decided 63: HYGIENE ONLY. A negative measurement is a FACT line, not a gate. A "
                      "mutator call REFUSED BY THE MACHINE is a gate.",
     "bed": {"path": BED, "md5_pin": BED_MD5, "size_pin": BED_SIZE,
             "never_overwritten": "the bed is only ever READ; all work is on SCRATCH / WORK"},
     "artefact_is_not_computation_equivalent":
         "THE M3a-1 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL - ITS SHIFT REGISTERS ARE "
         "UNINITIALISED (initial values = stage M3a-2). It is never run (34(f)).",
     "initial_values_out_of_scope":
         "wire_sr('LeftOutNode') and wire_sr('LeftOutCtl') are NOT called anywhere in this file",
     "no_new_verb": True, "no_new_op": True, "no_new_device": True,
     "no_open_panel_call_in_this_file": True, "gscript_not_edited": True,
     "no_astcheck_gate_file_edited": True, "no_gui_action": True,
     "broken_save_bypass": "NEVER used - neither the allow_broken diversion nor the GUI save",
     "remove_bad_wires_scripted": "not imported, not called (BANNED since cycle 58)",
     "no_whole_vi_gobject_census": True,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "purges": [], "build": {}, "probe": {}, "census": {}}
K = R["build"]


class Halt(Exception):
    pass


def gate(name, ok, detail=""):
    # `FAIL`, NOT `**FAIL**` (37(i)): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def refusal(where, msg):
    """A MUTATOR CALL THE MACHINE REFUSED. This is the only class of negative result that gates (63)."""
    refusals.append({"where": where, "error_verbatim": msg})
    fact("MACHINE REFUSAL at %s: %s" % (where, msg))


def probe_hash(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["machine_refusals"] = refusals
    R["elapsed_s"] = round(time.time() - T_START, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T_START) - RESERVE_S


def safe(label, fn, default=None):
    """Run one READ, record its error VERBATIM, never let it kill the run."""
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
    """NARROW CLASS CENSUSES ONLY - never a whole-VI GObject census (six of those took handles 34,602 ->
    91,288)."""
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    K.setdefault("censuses", {})[tag] = rec
    fact("%s counts: %r" % (tag, rec))
    return rec


def sr_counts(path, tag):
    rec = {}
    for c in ("LeftShiftRegister", "RightShiftRegister"):
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    fact("%s shift-register class counts: %r" % (tag, rec))
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
        refusal("%s delete %s #%s" % (tag, cls, uid), rec["error_verbatim"])
    rec["call_cost_s"] = round(time.time() - t0, 2)
    after, _ = safe("%s report_all(%r) after delete" % (tag, cls), lambda: g.report_all(path, cls), [])
    rec["census_after"] = len(after or [])
    rec["still_present"] = any(r["uid"] == uid for r in (after or []))
    fact("%s delete %s #%s at index %r: gone %r, error %r, census %r -> %r, still present %r (%.2f s)"
         % (tag, cls, uid, idx, rec.get("gone"), rec.get("error_verbatim"), rec["census_before"],
            rec["census_after"], rec["still_present"], rec.get("call_cost_s", 0.0)))
    return rec


def census_and_purge(path, nodes_before, tag, hints, keep_uids=()):
    """55(c): after EVERY move_in and EVERY connect_nested_v1, diff the `Node` census and purge the junk BY
    UID. A new node is DELETED only when it is an `Invoke` with ZERO wired terminals (the measured junk
    shape). Anything else is REPORTED VERBATIM and left alone."""
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
    final = nodes_after
    if rec["deleted"]:
        final, _ = node_census(path, "%s AFTER THE PURGE (the next step's baseline)" % tag)
        fact("%s purge arithmetic: Node %d -> %d -> %d (pre-call value %d)"
             % (tag, len(nodes_before), len(nodes_after), len(final), len(nodes_before)))
    rec["node_count_after_purge"] = len(final)
    R["purges"].append(rec)
    dump()
    return final, rec


def save_artefact(tag, dest, not_equal_to, not_equal_label):
    """g.save writes the WORKING copy in place; the artefact is a fresh path LabVIEW has never seen.
    A file byte-identical to its predecessor means THE IN-MEMORY EDITS DID NOT LAND."""
    rec = {"tag": tag, "dest": dest, "save_error_verbatim": "",
           "NOT_COMPUTATION_EQUIVALENT": "THE M3a-1 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL "
                                         "- ITS SHIFT REGISTERS ARE UNINITIALISED. It is never run."}
    rec["exec_state_at_save"] = read_es("%s immediately before the save" % tag, WORK)
    try:
        rec["save_returned_size"] = g.save(WORK)
    except Exception as e:                                                         # noqa: BLE001
        rec["save_returned_size"] = None
        rec["save_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    if rec["save_error_verbatim"]:
        fact("%s THE SAVE WAS REFUSED, VERBATIM: %s" % (tag, rec["save_error_verbatim"]))
        fact("%s NO FILE IS WRITTEN AT %s. Copying the working copy's DISK bytes would produce a file "
             "byte-identical to the bed - the in-memory edits would not be in it - so nothing is copied. "
             "The two bypasses named in tools/gscript.py:2088-2090 are FORBIDDEN by this brief and are not "
             "used." % (tag, os.path.basename(dest)))
        rec.update({"exists": False, "md5": None, "size": None})
        R["artefacts_on_disk"].append(rec)
        dump()
        return rec
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
    fact("%s FILE ON DISK: %s  md5 %r  size %r  (ExecState at the save %r ; bytes equal to %s %r)"
         % (tag, dest, rec["md5"], rec["size"], rec["exec_state_at_save"], not_equal_label,
            rec["bytes_equal_to_the_predecessor"]))
    fact("*** %s IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL - ITS SHIFT REGISTERS ARE UNINITIALISED. "
         "The initial values are stage M3a-2. IT IS NEVER RUN (34(f)). ***" % os.path.basename(dest))
    dump()
    return rec


def unit_boundary(tag):
    """The user's 2026-09-19 split rule, applied MECHANICALLY and not as a branch: read ExecState at every
    unit boundary and, WHENEVER it reads 1, leave a file on disk before the next unit starts."""
    es = read_es("[UNIT] %s" % tag, WORK)
    K.setdefault("unit_boundaries", []).append({"tag": tag, "exec_state": es})
    if es == 1:
        k = sum(1 for a in R["artefacts_on_disk"] if "_u" in os.path.basename(a["dest"])) + 1
        save_artefact("[UNIT %d] %s - ExecState 1 at a unit boundary" % (k, tag),
                      os.path.join(g.CLAUDEDEV, "D1_s3b_m3a_u%d_%s.vi" % (k, STAMP)), BED_MD5, "the bed")
    else:
        fact("[UNIT] %s: ExecState %r - NOT 1, so no intermediate file is written at this boundary" % (tag, es))
    dump()
    return es


# ============================================== the A7 pattern: a loop_index is ECHOED, never carried
def loop_index_of(uid, tag):
    rows, err = safe("%s report_all('WhileLoop')" % tag, lambda: g.report_all(WORK, "WhileLoop"), [])
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    echo = next((r["uid"] for r in (rows or []) if r["i"] == idx), None) if idx is not None else None
    K.setdefault("loop_index_echoes", []).append(
        {"tag": tag, "want_uid": uid, "loop_index": idx, "echoed_uid": echo,
         "whileloop_rows": len(rows or []), "error_verbatim": err})
    fact("%s A7 ECHO: report_all('WhileLoop')[%r].uid == %r (want #%d; %d WhileLoop row(s))"
         % (tag, idx, echo, uid, len(rows or [])))
    if echo != uid:
        refusal("%s loop_index echo" % tag,
                "report_all('WhileLoop')[%r].uid == %r, not #%d" % (idx, echo, uid))
        return None
    return idx


def echo_reg_uid(loop_index, reg_index, want_uid, tag):
    sr, err = safe("%s shift_reg(reg_index=%r) echo" % (tag, reg_index),
                   lambda: g.shift_reg(WORK, loop_index, reg_index))
    got = (sr or {}).get("uid")
    fact("%s REGECHO: shift_reg[reg_index=%r].uid == %r (want #%r)%s"
         % (tag, reg_index, got, want_uid, (" ; ERROR " + err) if err else ""))
    return got


def reg_index_of(loop_index, reg_uid, tag):
    """Map a RightShiftRegister uid to its reg_index by READING shift_reg(...) for each slot. Never assumed."""
    probes, hit = [], None
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
    return hit


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


# ======================================================================= [0] files only, zero LabVIEW
def phase_0():
    print("\n---------- [0] FILES ONLY, ZERO LabVIEW - the md5 pins BEFORE, then the pre-batch restart",
          flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; the pre-batch restart below is "
         "MANDATORY - 44(e))" % R["handles"]["before"])
    for tag, path, pin in PINS:
        pr = probe_hash("H %s BEFORE" % tag, path)
        gate("H %s md5 == its pin %s" % (tag, pin[:8]), pr.get("md5") == pin, "%r" % (pr.get("md5"),))
    pr = probe_hash("H THE BED size", BED)
    gate("H the bed is %d B" % BED_SIZE, str(pr.get("size")) == str(BED_SIZE), "%r" % (pr.get("size"),))
    K["tool_pins_before"] = {}
    for p in TOOL_PINS:
        pr = probe_hash("H TOOL %s BEFORE" % os.path.basename(p), p)
        K["tool_pins_before"][p] = pr.get("md5")

    D.fresh("[0] pre-batch LabVIEW restart (44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])
    dump()


# ========== [1] THE PROBE, ON A SCRATCH COPY, DELETED IN THE SAME STEP (Pre-decided 61)
def step_1_probe():
    print("\n---------- [1] THE PROBE ON A SCRATCH COPY: IS THERE AN ADDRESSABLE SOURCE ON Diagram #%d "
          "FOR THE `%s` NET?" % (D686, T1_TERM_NAME), flush=True)
    rec = {"scratch": SCRATCH, "question":
           "connect_nested_v1 addresses (diagram index, Nodes[] index, terminal index), so a SOURCE is "
           "ADDRESSABLE only if it is a NODE listed in some diagram's Nodes[]. Today the value reaches "
           "#10407 t1 as FlatSequenceInnerTunnel #9655 -> wire 9649 -> LoopTunnel #9641 "
           "(diag_c67_addsr.log:390-392). A TUNNEL IS NOT A NODE.",
           "never_a_local": "A Local is NEVER substituted for this row (rule 1a; a Local re-introduces the "
                            "56(j) ordering gap for a value the original delivers by wire)."}
    shutil.copy2(BED, SCRATCH)
    pr = probe_hash("[1] the scratch copy", SCRATCH)
    gate("H the probe scratch starts byte-identical to the bed", pr.get("md5") == BED_MD5,
         "%r" % (pr.get("md5"),))
    rec["cold_exec_state"] = read_es("[1] the scratch, COLD", SCRATCH)

    d686, e686 = safe("[1] diag_index(#%d)" % D686, lambda: diag_index(SCRATCH, D686))
    d639, e639 = safe("[1] diag_index(#%d)" % D639, lambda: diag_index(SCRATCH, D639))
    rec["d686_index"] = d686
    rec["d639_index"] = d639
    fact("[1] Diagram #%d -> traverse index %r (recorded %r) ; Diagram #%d -> %r (recorded %r)%s"
         % (D686, d686, D686_RECORDED, D639, d639, D639_RECORDED,
            ("; errors %r/%r" % (e686, e639)) if (e686 or e639) else ""))

    rows, lerr = safe("[1] node_labels(%r)" % d686, lambda: g.node_labels(SCRATCH, d686), [])
    uids_686 = [r["uid"] for r in (rows or [])]
    rec["d686_nodes"] = [{"i": k, "uid": r["uid"], "label": r["label"]} for k, r in enumerate(rows or [])]
    fact("[1] Diagram #%d Nodes[] census: %d node(s) -> %r%s"
         % (D686, len(uids_686), uids_686, (" ; " + lerr) if lerr else ""))

    # (a) the LoopTunnel that carries the value in today, re-read off THIS copy
    lts, lterr = safe("[1] report_all('LoopTunnel')", lambda: g.report_all(SCRATCH, "LoopTunnel"), [])
    lt_idx = next((r["i"] for r in (lts or []) if r["uid"] == T1_LOOP_TUNNEL), None)
    rec["loop_tunnel_rows"] = len(lts or [])
    rec["loop_tunnel_index"] = lt_idx
    fact("[1] report_all('LoopTunnel'): %d row(s) ; #%d is at index %r%s"
         % (len(lts or []), T1_LOOP_TUNNEL, lt_idx, (" ; " + lterr) if lterr else ""))
    if lt_idx is not None:
        tn, terr = safe("[1] tunnels(%r)" % lt_idx, lambda: g.tunnels(SCRATCH, lt_idx))
        rec["loop_tunnel_read"] = tn
        fact("[1] tunnels(%r) -> uid %r (echo of #%d: %r) ; OUTSIDE name %r is_source %r wire %r ; INSIDE "
             "names %r wires %r%s"
             % (lt_idx, (tn or {}).get("uid"), T1_LOOP_TUNNEL,
                (tn or {}).get("uid") == T1_LOOP_TUNNEL, (tn or {}).get("out_name"),
                (tn or {}).get("out_is_source"), (tn or {}).get("out_wire"), (tn or {}).get("in_names"),
                (tn or {}).get("in_wires"), (" ; " + terr) if terr else ""))

    # (b) the OUTER wire's own Terms[] walk - who SOURCES the net, by uid and owner class
    walk, werr = safe("[1] wire_source_owner(%d)" % T1_OUTER_WIRE,
                      lambda: WIRE_TERMS(SCRATCH, T1_OUTER_WIRE), [])
    rec["outer_wire_walk"] = walk
    rec["outer_wire_walk_error"] = werr
    src = next((t for t in (walk or []) if t.get("is_source") and t.get("owner_uid")), None)
    rec["outer_wire_source"] = src
    fact("[1] wire %d Terms[] walk: %r ; SOURCE endpoint %r%s"
         % (T1_OUTER_WIRE, walk, src, (" ; " + werr) if werr else ""))

    # (c) THE QUESTION ITSELF: is any NODE on #686 a source for this net, by uid or by terminal NAME?
    scan, hits_wire, hits_name = [], [], []
    for i in range(min(SCAN_LIMIT, len(uids_686))):
        if left_s() < BUILD_MIN_S:
            rec["scan_stopped"] = "wall-clock guard after %d node(s)" % len(scan)
            break
        try:
            u, tr = g.node_terms_uid(SCRATCH, d686, i)
        except Exception as e:                                                     # noqa: BLE001
            rec["scan_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
            break
        if not u:
            break
        scan.append({"nodes_index": i, "uid": u, "n_terminals": len(tr)})
        for t in tr:
            if t["wire"] == T1_OUTER_WIRE:
                hits_wire.append({"nodes_index": i, "node_uid": u, "terminal": t["i"], "name": t["name"],
                                  "is_source": t["is_source"], "wire": t["wire"]})
            if t["name"] == T1_TERM_NAME and t["is_source"]:
                hits_name.append({"nodes_index": i, "node_uid": u, "terminal": t["i"], "name": t["name"],
                                  "is_source": t["is_source"], "wire": t["wire"]})
    rec["d686_scanned"] = len(scan)
    rec["hits_on_the_outer_wire"] = hits_wire
    rec["hits_by_terminal_name"] = hits_name
    rec["source_tunnel_is_a_node_on_686"] = (T1_OUTER_SOURCE in uids_686)
    fact("[1] scanned %d node(s) of Diagram #%d ; terminals carrying wire %d: %r ; SOURCE terminals named "
         "%r: %r ; is the net's source #%d itself a Nodes[] entry on #%d? %r"
         % (len(scan), D686, T1_OUTER_WIRE, hits_wire, T1_TERM_NAME, hits_name, T1_OUTER_SOURCE, D686,
            rec["source_tunnel_is_a_node_on_686"]))

    cands = [h for h in hits_wire if h["is_source"]] + [h for h in hits_name
                                                        if h not in hits_wire]
    rec["addressable_candidates"] = cands
    rec["answer"] = bool(cands)
    fact("[1] *** THE PROBE'S ANSWER: an ADDRESSABLE (node-and-terminal) SOURCE on Diagram #%d for the "
         "`%s` net EXISTS: %r ; candidates %r ***" % (D686, T1_TERM_NAME, rec["answer"], cands))
    fact("[1] WHAT THIS DOES AND DOES NOT SETTLE: it settles whether `connect_nested_v1` CAN BE GIVEN a "
         "source for this row at all. Whether `connect_nested_v1` AUTO-CREATES a LoopTunnel across "
         "#%d's border can only be measured where the sink actually lives, so if a candidate exists the "
         "attempt is made IN SITU at step [5] with the LoopTunnel and #%d-terminal counts read either "
         "side. If none exists the question is NOT answerable this run and that is a fact, not a failure."
         % (LOOP_A_UID, LOOP_A_UID))

    # the baselines the step-[5] delta is measured against
    rec["baseline_counts"] = {}
    for c in ("LoopTunnel", "Tunnel"):
        rec["baseline_counts"][c], _ = safe("[1] count(%r)" % c, lambda cc=c: g.count(SCRATCH, cc))
    fact("[1] probe baselines on the scratch: %r" % (rec["baseline_counts"],))

    safe("[1] close_panel(scratch)", lambda: g.close_panel(SCRATCH))
    if os.path.exists(SCRATCH):
        safe("[1] remove the probe scratch", lambda: os.remove(SCRATCH))
    gate("H the probe scratch %s is gone (exists=False)" % os.path.basename(SCRATCH),
         not os.path.exists(SCRATCH), "")
    R["probe"] = rec
    dump()
    return rec


# ================================================= [2a] the working copy and its cold baseline
def step_2_baseline():
    print("\n---------- [2a] THE WORKING COPY AND ITS COLD BASELINE", flush=True)
    shutil.copy2(BED, WORK)
    pr = probe_hash("[2a] the working copy", WORK)
    gate("H the working copy starts byte-identical to the bed", pr.get("md5") == BED_MD5,
         "%r" % (pr.get("md5"),))
    es = read_es("[2a] the working copy, COLD", WORK)
    if es != 1:
        refusal("[2a] the working copy's COLD ExecState", "reads %r, not 1" % (es,))
        raise Halt("the working copy does not reopen at ExecState 1")
    c = counts(WORK, "[2a] COLD")
    K["counts_before"] = c
    for k, v in BASE.items():
        fact("[2a] %s == %r (recorded baseline %d ; match %r)" % (k, c.get(k), v, c.get(k) == v))
    fact("[2a] Tunnel == %r (recorded baseline %d ; match %r)"
         % (c.get("Tunnel"), BASE_TUNNEL, c.get("Tunnel") == BASE_TUNNEL))
    K["sr_counts_before"] = sr_counts(WORK, "[2a] COLD")

    di, err = safe("[2a] diag_index(#%d)" % D639, lambda: diag_index(WORK, D639))
    K["d639_index"] = di
    if di is None:
        refusal("[2a] diag_index(#%d)" % D639, err or "returned None")
        raise Halt("Diagram #%d does not resolve" % D639)
    rows, lerr = safe("[2a] node_labels(%r)" % di, lambda: g.node_labels(WORK, di), [])
    K["d639_nodes"] = len(rows or [])
    fact("[2a] Diagram #%d -> traverse index %r (recorded %d) ; %d node(s) (recorded %d)%s"
         % (D639, di, D639_RECORDED, len(rows or []), D639_NODES_RECORDED, (" ; " + lerr) if lerr else ""))
    ncen, _ = node_census(WORK, "[2a] whole-VI Node")
    K["node_census_before"] = ncen
    hints = [di, TOP]
    _loc, lrows = node_view(WORK, LOOP11_UID, hints, "[2a] #%d the WhileLoop" % LOOP11_UID, quiet=True)
    K["loop637_before"] = {"n_terms": len(lrows), "n_wired": wired_count(lrows)}
    fact("[2a] #%d (WhileLoop): %d terminals, %d WIRED (recorded %d / %d)"
         % (LOOP11_UID, len(lrows), wired_count(lrows), LOOP637_TERMS_RECORDED, LOOP637_WIRED_RECORDED))
    dump()
    return hints


# ================================================================= [2b] the seven `move_in` calls
def resolve_dest(tag):
    """38(e): RE-RESOLVE the destination index BY UID from a freshly-read traverse list immediately before
    every `move_in`."""
    lst, err = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(WORK, "Diagram"), [])
    uids = [o["uid"] for o in (lst or [])]
    idx = uids.index(BODY_A_UID) if BODY_A_UID in uids else None
    owns = idx is not None and uids[idx] == BODY_A_UID
    K.setdefault("dest_index_resolutions", []).append(
        {"tag": tag, "want_diagram_uid": BODY_A_UID, "resolved_index": idx, "traverse_len": len(uids),
         "index_still_owns_it": owns, "error_verbatim": err})
    fact("%s DESTINDEX: Diagram #%d -> traverse index %r (array length %d ; still owns it %r)"
         % (tag, BODY_A_UID, idx, len(uids), owns))
    if not owns:
        refusal("%s resolve_dest" % tag, "the traverse array does not list Diagram #%d" % BODY_A_UID)
    return idx


def body_a_node_uids(tag):
    """THE AUTHORITATIVE READ: Diagram #23058's own Nodes[] census, by uid."""
    idx, err = safe("%s diag_index(#%d)" % (tag, BODY_A_UID), lambda: diag_index(WORK, BODY_A_UID))
    if idx is None:
        fact("%s Diagram #%d could not be resolved: %s" % (tag, BODY_A_UID, err))
        return [], idx
    rows, lerr = safe("%s node_labels(%r)" % (tag, idx), lambda: g.node_labels(WORK, idx), [])
    uids = [r["uid"] for r in (rows or [])]
    fact("%s Diagram #%d [traverse %r] Nodes[] census: %d node(s) -> %r%s"
         % (tag, BODY_A_UID, idx, len(uids), uids, (" ; " + lerr) if lerr else ""))
    return uids, idx


def step_2_moves(hints):
    print("\n---------- [2b] THE SEVEN `move_in` CALLS, VERBATIM FROM diag_c66b_s3b_m3.py (37(d) severs "
          "every wire on the moved object)", flush=True)
    before_uids, bidx = body_a_node_uids("[2b] BEFORE")
    K["body_a_before"] = before_uids
    nodes = K["node_census_before"]
    after_hints = [bidx, hints[0], TOP]
    for uid, name, pos, why in SET:
        _loc, rows = node_view(WORK, uid, hints, "[2b] #%d BEFORE" % uid, quiet=True)
        fact("[2b] #%d %r BEFORE the move: %d terminal(s), %d WIRED  (%s)"
             % (uid, name, len(rows), wired_count(rows), why))
        bi = resolve_dest("[2b] before move #%d" % uid)
        rec = {"uid": uid, "name": name, "dest_diagram_uid": BODY_A_UID, "dest_index_used": bi,
               "position": list(pos), "wired_before": wired_count(rows), "n_terms_before": len(rows)}
        try:
            rec["echoed_uid"] = move_in(WORK, uid, bi, pos)
            rec["error_verbatim"] = ""
            fact("[2b] MOVE #%d %r -> Diagram #%d [traverse %r] at %r; the op echoed uid %r (37(d): the "
                 "echo is NOT the moved object)" % (uid, name, BODY_A_UID, bi, pos, rec["echoed_uid"]))
        except Exception as e:                                                     # noqa: BLE001
            rec["echoed_uid"] = None
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            refusal("[2b] move_in(#%d)" % uid, rec["error_verbatim"])
        nodes, _p = census_and_purge(WORK, nodes, "[2b] after move #%d" % uid, after_hints)
        after_uids, _ = body_a_node_uids("[2b] after move #%d" % uid)
        rec["in_body_a_nodes"] = uid in after_uids
        fact("[2b] #%d in Diagram #%d's Nodes[] after the move: %r (body holds %d node(s))"
             % (uid, BODY_A_UID, rec["in_body_a_nodes"], len(after_uids)))
        own, oerr = safe("[2b] owner_of(%d) after the move" % uid, lambda u=uid: owner_of(WORK, u))
        rec["owner_of_after"] = list(own) if own else None
        rec["owner_of_error"] = oerr
        fact("[2b] owner_of(%d) AFTER the move = %r (REPORTED ALONGSIDE the Nodes[] census, never instead "
             "of it - 53(d^8))" % (uid, own))
        _l2, rows2 = node_view(WORK, uid, after_hints, "[2b] #%d AFTER" % uid, quiet=True)
        rec["wired_after"] = wired_count(rows2)
        rec["n_terms_after"] = len(rows2)
        fact("[2b] #%d AFTER the move: %d terminal(s), %d WIRED (was %d)"
             % (uid, len(rows2), wired_count(rows2), rec["wired_before"]))
        rec["exec_state_after"] = unit_boundary("after move #%d %s" % (uid, name))
        K.setdefault("moves", []).append(rec)
        dump()
    final_uids, _ = body_a_node_uids("[2b] AFTER all seven")
    K["body_a_after_moves"] = final_uids
    missing = [u for u in SET_UIDS if u not in final_uids]
    K["moves_missing"] = missing
    fact("[2b] *** ALL SEVEN MOVED UIDS IN Diagram #%d's Nodes[]: %r (missing %r ; body holds %d) ***"
         % (BODY_A_UID, not missing, missing, len(final_uids)))
    K["counts_after_moves"] = counts(WORK, "[2b] after the seven moves")
    dump()
    return nodes, not missing, after_hints


# ================================================================ [2c] the seven internal rows
def one_row(nodes, hints, sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why, tag, slot,
            src_hints=None):
    """ONE `connect_nested_v1` row, addressed off the machine at both ends and verified BY WIRE UID."""
    job = {"sink_uid": sink_uid, "sink_name": sink_name, "sink_t_recorded": sink_t,
           "src_uid": src_uid, "src_name": src_name, "src_t_recorded": src_t, "evidence": why}
    if left_s() < ROW_MIN_S:
        job["result"] = "NOT STARTED - only %.0f s left before the reserve" % left_s()
        fact("%s row #%d t%r <- #%d t%r: %s" % (tag, sink_uid, sink_t, src_uid, src_t, job["result"]))
        K.setdefault(slot, []).append(job)
        dump()
        return nodes, job
    sloc, srows = node_view(WORK, sink_uid, hints, "%s sink #%d" % (tag, sink_uid), quiet=True)
    rloc, rrows = node_view(WORK, src_uid, src_hints or hints, "%s src  #%d" % (tag, src_uid), quiet=True)
    job["sink_wired_before"] = wired_count(srows)
    job["src_wired_before"] = wired_count(rrows)
    job["sink_terminals_before"] = srows
    job["src_terminals_before"] = rrows
    si, show = resolve_term(srows, sink_name, sink_t, False, "%s sink #%d" % (tag, sink_uid))
    ri, rhow = resolve_term(rrows, src_name, src_t, True, "%s src #%d" % (tag, src_uid))
    job["sink_term_resolution"] = show
    job["src_term_resolution"] = rhow
    sd = (sloc.get("found") or {}).get("diagram_index")
    sn = (sloc.get("found") or {}).get("nodes_index")
    rd = (rloc.get("found") or {}).get("diagram_index")
    rn = (rloc.get("found") or {}).get("nodes_index")
    job["addr"] = {"sink_diag": sd, "sink_node": sn, "sink_term": si,
                   "src_diag": rd, "src_node": rn, "src_term": ri}
    job["same_nested_diagram"] = (sd is not None and sd == rd)
    fact("%s row #%d t%r <- #%d t%r : %r ; sink %s ; src %s ; same diagram %r"
         % (tag, sink_uid, si, src_uid, ri, job["addr"], show, rhow, job["same_nested_diagram"]))
    if None in (si, ri, sn, rn):
        job["result"] = "NOT ADDRESSABLE - one end did not resolve"
        fact("%s row #%d t%r <- #%d t%r: %s" % (tag, sink_uid, sink_t, src_uid, src_t, job["result"]))
        K.setdefault(slot, []).append(job)
        dump()
        return nodes, job
    try:
        dw, es, err = CONNECT_V1(WORK, sd, sn, si, rd, rn, ri, V1_LABELS)
        job["connect"] = {"wire_delta": dw, "exec_state": es, "machine_error": str(err)[:200]}
    except Exception as e:                                                        # noqa: BLE001
        job["connect"] = {"call_error": "%s: %s" % (type(e).__name__, str(e)[:250])}
        refusal("%s connect_nested_v1 row #%d t%r" % (tag, sink_uid, si), job["connect"]["call_error"])
    fact("%s connect_nested_v1 -> %r" % (tag, job["connect"]))
    nodes, _p = census_and_purge(WORK, nodes, "%s after row #%d t%r" % (tag, sink_uid, si), hints)
    _l3, srows2 = node_view(WORK, sink_uid, hints, "%s sink #%d AFTER" % (tag, sink_uid), quiet=True)
    _l4, rrows2 = node_view(WORK, src_uid, src_hints or hints, "%s src  #%d AFTER" % (tag, src_uid),
                            quiet=True)
    job["sink_wired_after"] = wired_count(srows2)
    job["src_wired_after"] = wired_count(rrows2)
    srow = next((t for t in srows2 if t["i"] == si), None)
    rrow = next((t for t in rrows2 if t["i"] == ri), None)
    job["same_wire_uid"] = bool(srow and rrow and srow["wire"] and srow["wire"] == rrow["wire"])
    job["wire_uid"] = (srow or {}).get("wire")
    job["landed"] = bool(srow and srow.get("wire")) and job["sink_wired_after"] > job["sink_wired_before"]
    fact("%s row #%d t%r <- #%d t%r : sink wire %r / src wire %r ; same net %r ; WIRED-TERMINAL counts "
         "sink %d -> %d, src %d -> %d ; LANDED %r"
         % (tag, sink_uid, si, src_uid, ri, (srow or {}).get("wire"), (rrow or {}).get("wire"),
            job["same_wire_uid"], job["sink_wired_before"], job["sink_wired_after"],
            job["src_wired_before"], job["src_wired_after"], job["landed"]))
    job["exec_state_after"] = unit_boundary("after row #%d t%r <- #%d t%r" % (sink_uid, si, src_uid, ri))
    K.setdefault(slot, []).append(job)
    dump()
    return nodes, job


def step_2_rows(nodes, hints):
    print("\n---------- [2c] THE SEVEN INTERNAL ROWS, VERBATIM FROM diag_c66b_s3b_m3.py", flush=True)
    for sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why in INTERNAL_JOBS:
        nodes, _job = one_row(nodes, hints, sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why,
                              "[2c]", "internal_rows")
    landed = sum(1 for j in K.get("internal_rows", []) if j.get("landed"))
    fact("[2c] INTERNAL ROWS LANDED: %d of %d" % (landed, len(INTERNAL_JOBS)))
    return nodes


# ======================================================= [3] two add_shift_reg pairs on #23032
def step_3_registers():
    print("\n---------- [3] TWO `add_shift_reg` PAIRS ON #%d, WITH THE CYCLE-67 REPAIRED WRAPPER"
          % LOOP_A_UID, flush=True)
    K["sr_counts_before_add"] = sr_counts(WORK, "[3] before the two add_shift_reg calls")
    made = {}
    for n, pair in enumerate(SR_PAIRS):
        li = loop_index_of(LOOP_A_UID, "[3] before add_shift_reg #%d (%s)" % (n + 1, pair))
        if li is None:
            made[pair] = {"right_uid": None, "error_verbatim": "no loop_index for #%d" % LOOP_A_UID}
            continue
        y = 120 + 90 * n
        uid, err = safe("[3] add_shift_reg(y=%d)" % y,
                        lambda ll=li, yy=y: g.add_shift_reg(WORK, ll, y_position=yy))
        if err:
            refusal("[3] add_shift_reg(%s pair)" % pair, err)
        fact("[3] add_shift_reg #%d for the %s pair at y=%d -> RightShiftRegister uid %r%s"
             % (n + 1, pair, y, uid, (" ; ERROR " + err) if err else ""))
        made[pair] = {"right_uid": uid, "y": y, "error_verbatim": err}
        made[pair]["sr_counts_after"] = sr_counts(WORK, "[3] after add_shift_reg #%d (%s)" % (n + 1, pair))
        made[pair]["exec_state_after"] = unit_boundary("after add_shift_reg #%d (%s pair)" % (n + 1, pair))
    fact("[3] NOTE FOR THE RECORD: both registers come back UNTYPED with BOTH SIDES UNWIRED, so `ExecState` "
         "0 from here on is CORRECT, NOT A FAILURE (tools/gscript.py:683-687). The names 'VISA' and 'POS' "
         "are THIS RUN'S assignment of a pair to a row set; the terminal NAMES read off the machine below "
         "are what justify each row's membership.")
    # THE reg_index <-> uid MAPPING IS READ, NEVER ASSUMED, and loop_cast's own list is read alongside.
    li = loop_index_of(LOOP_A_UID, "[3] before the reg_index readback")
    if li is not None:
        lc, lerr = safe("[3] loop_cast(index=%r)" % li, lambda: g.loop_cast(WORK, li, class_name="WhileLoop"))
        K["loop_cast_readback"] = {"loop_uid": (lc or {}).get("loop_uid"),
                                   "shift_reg_uids": (lc or {}).get("shift_reg_uids"),
                                   "errors": (lc or {}).get("errors"), "error_verbatim": lerr}
        fact("[3] *** loop_cast READBACK on #%d: loop_uid %r ; shift_reg_uids %r ; op errors %r%s ***"
             % (LOOP_A_UID, (lc or {}).get("loop_uid"), (lc or {}).get("shift_reg_uids"),
                (lc or {}).get("errors"), (" ; " + lerr) if lerr else ""))
        for pair in SR_PAIRS:
            if made.get(pair, {}).get("right_uid"):
                made[pair]["reg_index"] = reg_index_of(li, made[pair]["right_uid"], "[3] %s pair" % pair)
    fact("[3] MINTED: %r" % ({p: {"right_uid": made.get(p, {}).get("right_uid"),
                                  "reg_index": made.get(p, {}).get("reg_index")} for p in SR_PAIRS},))
    K["shift_registers"] = made
    K["counts_after_add"] = counts(WORK, "[3] after the two add_shift_reg calls")
    dump()
    return made


# ============================================================= [4] the four SR rows, RightIn first
def step_4_sr_rows(made, hints):
    print("\n---------- [4] THE FOUR SHIFT-REGISTER ROWS - RightIn BEFORE LeftIn (the sources type the "
          "register)", flush=True)
    for pair, variant, node_uid, term_name, term_i, node_is_source in SR_JOBS:
        job = {"pair": pair, "variant": variant, "node_uid": node_uid,
               "term_name_recorded": term_name, "term_index_recorded": term_i,
               "node_terminal_is_source": node_is_source,
               "reg_index": (made.get(pair) or {}).get("reg_index"),
               "right_reg_uid": (made.get(pair) or {}).get("right_uid")}
        if job["reg_index"] is None:
            job["result"] = "NO reg_index resolved in step [3] - the row is NOT attempted"
            fact("[4] %s %s row on #%d: %s" % (pair, variant, node_uid, job["result"]))
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        bidx, berr = safe("[4] diag_index(#%d)" % BODY_A_UID, lambda: diag_index(WORK, BODY_A_UID))
        brows, lerr = safe("[4] node_labels(%r)" % bidx, lambda: g.node_labels(WORK, bidx), [])
        nidx = next((k for k, r in enumerate(brows or []) if r["uid"] == node_uid), None)
        job.update({"body_diagram_index": bidx, "body_nodes_index": nidx,
                    "body_nodes_len": len(brows or []), "addr_errors": [berr, lerr]})
        if nidx is None:
            job["result"] = "#%d IS NOT IN Diagram #%d's Nodes[] - the row is NOT attempted" \
                            % (node_uid, BODY_A_UID)
            fact("[4] %s %s: %s" % (pair, variant, job["result"]))
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        tt = terms_at(WORK, bidx, nidx, node_uid, "[4] %s %s #%d" % (pair, variant, node_uid))
        rows = tt.get("terminals", [])
        job["node_terminals_before"] = rows
        ti, how = resolve_term(rows, term_name, term_i, node_is_source,
                               "[4] %s %s #%d" % (pair, variant, node_uid))
        job["term_resolution"] = how
        job["term_index_used"] = ti
        fact("[4] %s %s row: node #%d at Nodes[%r] of Diagram #%d [traverse %r], terminal %r resolved %s"
             % (pair, variant, node_uid, nidx, BODY_A_UID, bidx, ti, how))
        if ti is None:
            job["result"] = "TERMINAL UNRESOLVED - the row is NOT attempted"
            fact("[4] %s %s row on #%d: %s" % (pair, variant, node_uid, job["result"]))
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        li = loop_index_of(LOOP_A_UID, "[4] before wire_sr(%s, %s)" % (variant, pair))
        if li is None:
            job["result"] = "NO loop_index for #%d - the row is NOT attempted" % LOOP_A_UID
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        job["reg_uid_echo"] = echo_reg_uid(li, job["reg_index"], job["right_reg_uid"],
                                           "[4] before wire_sr(%s, %s)" % (variant, pair))
        nodes_before, _ = node_census(WORK, "[4] before wire_sr(%s, %s)" % (variant, pair))
        t0 = time.time()
        try:
            g.wire_sr(variant, WORK, li, job["reg_index"], node_index=nidx, term_index=ti)
            job["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            job["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            refusal("[4] wire_sr(%s, %s) on #%d t%r" % (variant, pair, node_uid, ti), job["error_verbatim"])
        job["call_cost_s"] = round(time.time() - t0, 2)
        fact("[4] wire_sr(%r, loop_index=%r, reg_index=%r, node_index=%r, term_index=%r) -> error %r (%.2f s)"
             % (variant, li, job["reg_index"], nidx, ti, job["error_verbatim"], job["call_cost_s"]))
        census_and_purge(WORK, nodes_before, "[4] after wire_sr(%s, %s)" % (variant, pair), hints)
        # VERIFY BY WIRE UID AT BOTH ENDS.
        tt2 = terms_at(WORK, bidx, nidx, node_uid, "[4] %s %s #%d AFTER" % (pair, variant, node_uid),
                       quiet=True)
        after_row = next((t for t in tt2.get("terminals", []) if t["i"] == ti), None)
        job["node_terminal_after"] = after_row
        node_wire = (after_row or {}).get("wire") or 0
        srl, serr = safe("[4] shift_reg_left after the row",
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
        job["landed"] = bool(node_wire) and node_wire in reg_wires
        fact("[4] *** %s %s row #%d t%r <-> reg_index %r: node terminal carries wire %r ; %s carries %r ; "
             "ONE NON-ZERO WIRE UID AT BOTH ENDS: %r ***"
             % (pair, variant, node_uid, ti, job["reg_index"], node_wire, side_label, reg_wires,
                job["landed"]))
        job["exec_state_after"] = unit_boundary("after the %s %s row on #%d" % (pair, variant, node_uid))
        K.setdefault("sr_rows", []).append(job)
        dump()
    landed = sum(1 for j in K.get("sr_rows", []) if j.get("landed"))
    fact("[4] SR ROWS LANDED: %d of %d" % (landed, len(SR_JOBS)))
    fact("[4] NOT CALLED, DELIBERATELY OUT OF SCOPE: wire_sr('LeftOutNode') and wire_sr('LeftOutCtl') - the "
         "registers' INITIAL VALUES are STAGE M3a-2. An uninitialised register is legal LabVIEW and the "
         "initial values are a rule-1a question, not a compile question.")


# ============================================================ [5] the fifth row, #10407 t1
def step_5_t1(nodes, hints, probe_rec):
    print("\n---------- [5] THE FIFTH ROW: #%d t%d %r" % (CASE_UID, T1_TERM_INDEX, T1_TERM_NAME), flush=True)
    rec = {"probe_answer": probe_rec.get("answer"), "candidates": probe_rec.get("addressable_candidates")}
    if not probe_rec.get("answer"):
        rec["result"] = "NOT WIRED - step [1] measured NO addressable (node-and-terminal) source on " \
                        "Diagram #%d for this net" % D686
        fact("[5] *** %s. Nothing is wired here, nothing is substituted (a Local is never substituted - "
             "rule 1a), and the run carries on to the census. Whether `connect_nested_v1` auto-tunnels "
             "across #%d's border is therefore NOT ANSWERED this run. ***" % (rec["result"], LOOP_A_UID))
        K["t1_row"] = rec
        dump()
        return nodes, rec
    cand = rec["candidates"][0]
    rec["chosen_candidate"] = cand
    before = {}
    for c in ("LoopTunnel", "Tunnel"):
        before[c], _ = safe("[5] count(%r) before" % c, lambda cc=c: g.count(WORK, cc))
    _lloc, lrows = node_view(WORK, LOOP_A_UID, hints, "[5] #%d before" % LOOP_A_UID, quiet=True)
    before["loop_%d_terminals" % LOOP_A_UID] = len(lrows)
    rec["counts_before"] = before
    fact("[5] baselines before the attempt: %r" % (before,))
    d686, _e = safe("[5] diag_index(#%d)" % D686, lambda: diag_index(WORK, D686))
    nodes, job = one_row(nodes, hints, CASE_UID, T1_TERM_NAME, T1_TERM_INDEX,
                         cand["node_uid"], cand.get("name") or "", cand["terminal"],
                         "the t1 row; source measured on Diagram #%d by step [1]" % D686,
                         "[5]", "t1_row_attempt", src_hints=[d686, TOP] + list(hints))
    rec["row"] = job
    after = {}
    for c in ("LoopTunnel", "Tunnel"):
        after[c], _ = safe("[5] count(%r) after" % c, lambda cc=c: g.count(WORK, cc))
    _lloc2, lrows2 = node_view(WORK, LOOP_A_UID, hints, "[5] #%d after" % LOOP_A_UID, quiet=True)
    after["loop_%d_terminals" % LOOP_A_UID] = len(lrows2)
    rec["counts_after"] = after
    rec["auto_tunnel_delta"] = {k: (after.get(k), before.get(k)) for k in before}
    fact("[5] *** THE AUTO-TUNNEL MEASUREMENT: before %r -> after %r. A new LoopTunnel on #%d's border "
         "would show as BOTH a LoopTunnel count rise AND a terminal-count rise on #%d. ***"
         % (before, after, LOOP_A_UID, LOOP_A_UID))
    K["t1_row"] = rec
    dump()
    return nodes, rec


# ================================================================= [6] the full census
def census(tag, hints, include_registers=True):
    """THE FULL WIRED-TERMINAL CENSUS of the seven moved nodes (and both registers) - EVERY terminal, not a
    selection - plus the derived BARE list. Unconditional, whatever ExecState says."""
    print("\n---------- [6] FULL `node_terms` CENSUS OF THE SEVEN MOVED NODES PLUS BOTH SHIFT REGISTERS",
          flush=True)
    rec = {"tag": tag, "exec_state_at_census": read_es("[6] at the census", WORK),
           "nodes": {}, "bare": [], "registers": {}}
    for uid, name, _pos, _why in SET:
        loc, rows = node_view(WORK, uid, hints, "[6] #%d %s" % (uid, name))
        rec["nodes"][str(uid)] = {"uid": uid, "name": name, "found": loc.get("found"),
                                  "uid_echo": loc.get("uid_echo"), "n_terminals": len(rows),
                                  "n_wired": wired_count(rows), "terminals": rows}
        for t in rows:
            if not t.get("wire"):
                rec["bare"].append({"node_uid": uid, "node_name": name, "term_index": t.get("i"),
                                    "term_name": t.get("name"), "is_source": t.get("is_source"),
                                    "wire": t.get("wire"), "errs": t.get("errs"), "state": term_state(t)})
        fact("[6] #%d %r: %d terminal(s), %d WIRED, %d with WireUID 0"
             % (uid, name, len(rows), wired_count(rows), sum(1 for t in rows if not t.get("wire"))))
    if include_registers:
        li = loop_index_of(LOOP_A_UID, "[6] before the register read")
        for pair in SR_PAIRS:
            ri = (K.get("shift_registers") or {}).get(pair, {}).get("reg_index")
            if ri is None or li is None:
                rec["registers"][pair] = {"reg_index": ri, "note": "no reg_index / loop_index to read with"}
                fact("[6] the %s pair cannot be read back (reg_index %r, loop_index %r)" % (pair, ri, li))
                continue
            srl, err = safe("[6] shift_reg_left(%s)" % pair, lambda rr=ri: g.shift_reg_left(WORK, li, rr, 0))
            rec["registers"][pair] = {"reg_index": ri, "read": srl, "error_verbatim": err}
            fact("[6] %s pair reg_index %d -> right #%r out %r inside %r ; left #%r out %r inside %r"
                 % (pair, ri, (srl or {}).get("uid"), (srl or {}).get("out"), (srl or {}).get("inside"),
                    ((srl or {}).get("left") or {}).get("uid"), ((srl or {}).get("left") or {}).get("out"),
                    ((srl or {}).get("left") or {}).get("inside")))
            for side, d in (("right", srl or {}), ("left", (srl or {}).get("left") or {})):
                for where, t in [("outer", (d.get("out") or {}))] + \
                        [("inside", x) for x in (d.get("inside") or [])]:
                    if not t.get("wire"):
                        rec["bare"].append({"node_uid": d.get("uid"),
                                            "node_name": "%s SR %s %s" % (pair, side, where),
                                            "term_index": None, "term_name": t.get("name"),
                                            "is_source": t.get("is_source"), "wire": t.get("wire"),
                                            "errs": None, "state": "BARE (WireUID 0)"})
    print("\n  *** [6] THE BARE LIST - EVERY TERMINAL WITH WireUID 0 (%d row(s)) ***" % len(rec["bare"]),
          flush=True)
    for b in rec["bare"]:
        fact("[6] BARE  node #%-6r %-26r t%-4r %-34r is_source=%-5r state=%s"
             % (b["node_uid"], b["node_name"], b["term_index"], b["term_name"], b["is_source"], b["state"]))
    fact("[6] BARE LIST SIZE: %d terminal(s) with WireUID 0" % len(rec["bare"]))
    R["census"] = rec
    dump()
    return rec


# ============================== [7] ExecState, the save, the restart, the ordered Broken? read LAST
def step_7_save(hints):
    print("\n---------- [7] ExecState AND THE SAVE", flush=True)
    es = read_es("[7] the decision point", WORK)
    K["exec_state_decision"] = es
    K["counts_final"] = counts(WORK, "[7] final, in memory")
    K["sr_counts_final"] = sr_counts(WORK, "[7] final, in memory")
    _l, lrows = node_view(WORK, LOOP11_UID, hints, "[7] #%d the WhileLoop" % LOOP11_UID, quiet=True)
    K["loop637_after"] = {"n_terms": len(lrows), "n_wired": wired_count(lrows)}
    fact("[7] #%d (WhileLoop): %r (before %r) - 37(e)/50(e)'s no-new-tunnel comparison, REPORTED"
         % (LOOP11_UID, K["loop637_after"], K.get("loop637_before")))
    if es == 1:
        rec = save_artefact("[7] the M3a-1 artefact", FINAL_PATH, BED_MD5, "the bed")
        if not rec.get("exists"):
            return rec
        D.fresh("[7] LabVIEW RESTART before the COLD reopen")
        R["handles"]["after_final_restart"] = labview_handles()
        es_cold = read_es("[7] COLD, after the restart", FINAL_PATH)
        K["exec_state_cold"] = es_cold
        fact("[7] *** THE SAVED ARTEFACT REOPENS COLD AT ExecState %r ***" % (es_cold,))
        K["counts_cold"] = counts(FINAL_PATH, "[7] COLD")
        # THE ORDERED `Broken?` PASS, LAST OF ALL (42(b)/52(f)) - never above a save point.
        print("\n---------- [7d] THE ORDERED `Broken?` PASS, LAST OF ALL (42(b)/52(f))", flush=True)
        br, berr = safe("[7d] report_all('Wire') for the ordered pass",
                        lambda: g.report_all(FINAL_PATH, "Wire"), [])
        K["cold_wire_rows"] = len(br or [])
        fact("[7d] COLD Wire census: %d row(s)%s" % (len(br or []), (" ; " + berr) if berr else ""))
        vb, verr = safe("[7d] exec_state(FINAL) second ordered read", lambda: g.exec_state(FINAL_PATH))
        K["exec_state_cold_second"] = vb
        fact("[7d] the SECOND ordered ExecState read on the cold artefact = %r%s (52(f): the type checker "
             "answers only on a second ordered pass)" % (vb, (" ; " + verr) if verr else ""))
        safe("[7] close_panel(final)", lambda: g.close_panel(FINAL_PATH))
        return rec
    fact("[7] ExecState %r. The brief asks for `%s` in this case, so THE SAVE IS ATTEMPTED and whatever "
         "the machine answers is recorded verbatim below." % (es, os.path.basename(BROKEN_PATH)))
    rec = save_artefact("[7] the BROKEN M3a-1 artefact", BROKEN_PATH, BED_MD5, "the bed")
    if rec.get("exists"):
        fact("[7] *** %s IS NOT A DELIVERABLE. IT IS NEVER RUN (34(f)) AND IT IS NEVER USED AS A BED FOR "
             "ANY LATER STAGE. Its shift registers are uninitialised AND it does not compile. ***"
             % os.path.basename(BROKEN_PATH))
    else:
        fact("[7] *** NO BROKEN ARTEFACT IS ON DISK: the save path refused it (verbatim above) and the two "
             "bypasses at tools/gscript.py:2088-2090 are FORBIDDEN by this brief. NOTHING WAS WRITTEN "
             "UNDER %s. This is reported to judgement, not worked around. ***" % os.path.basename(
                 BROKEN_PATH))
    # A COLD REOPEN IS NOT ATTEMPTED ON A BROKEN ARTEFACT: the skill's own rule - never cold-load a
    # broken-saved VI headless (recompile spin).
    fact("[7] NO COLD REOPEN IS ATTEMPTED at ExecState 0 - the labview-automation skill's rule: never "
         "cold-load a broken-saved VI headless (recompile spin).")
    return rec


# ======================================================================= main
def main():
    print("=== build_d1_m3a1  %s  (bgrun --material --max-min 45)" % STAMP, flush=True)
    print("=== STAGE M3a-1. ANY ARTEFACT THIS RUN SAVES IS **NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL** "
          "- ITS SHIFT REGISTERS ARE UNINITIALISED (initial values = stage M3a-2). IT IS NEVER RUN (34(f)).",
          flush=True)
    hints = [D639_RECORDED, TOP]
    try:
        phase_0()
        probe_rec = step_1_probe()
        if left_s() < BUILD_MIN_S:
            fact("HALTED: only %.0f s left before the reserve; the build needs %.0f s"
                 % (left_s(), BUILD_MIN_S))
            raise Halt("no wall-clock left for the build")
        hints = step_2_baseline()
        nodes, _all_moved, after_hints = step_2_moves(hints)
        hints = after_hints
        nodes = step_2_rows(nodes, hints)
        made = step_3_registers()
        step_4_sr_rows(made, hints)
        nodes, _t1 = step_5_t1(nodes, hints, probe_rec)
        census("CENSUS", hints, include_registers=True)
        step_7_save(hints)
    except Halt as e:
        fact("HALTED: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        R["unexpected_exception"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("UNEXPECTED EXCEPTION: %s" % R["unexpected_exception"])
        refusal("main", R["unexpected_exception"])
    finally:
        safe("close_panel(WORK)", lambda: g.close_panel(WORK))
        for path in (SCRATCH, WORK):
            if os.path.exists(path):
                safe("remove %s" % os.path.basename(path), lambda p=path: os.remove(p))
            gate("H scratch %s is gone (exists=False)" % os.path.basename(path), not os.path.exists(path), "")
        print("\n---------- [H] THE md5 PINS AFTER, THE TOOL PINS, THE REFS AND THE HANDLES", flush=True)
        for tag, path, pin in PINS:
            pr = probe_hash("H %s AFTER" % tag, path)
            gate("H %s md5 is STILL its pin %s" % (tag, pin[:8]), pr.get("md5") == pin,
                 "%r" % (pr.get("md5"),))
        for p in TOOL_PINS:
            pr = probe_hash("H TOOL %s AFTER" % os.path.basename(p), p)
            gate("H TOOL %s is byte-identical before and after" % os.path.basename(p),
                 pr.get("md5") == (K.get("tool_pins_before") or {}).get(p),
                 "%r vs %r" % (pr.get("md5"), (K.get("tool_pins_before") or {}).get(p)))
        rc = g.ref_counts()
        R["ref_counts"] = rc
        fact("refs: %r" % (rc,))
        gate("H refs opened == closed and 0 live", rc.get("live") == 0, "%r" % (rc,))
        R["handles"]["after"] = labview_handles()
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"]["after"], R["handles"].get("before")))
        gate("H the LabVIEW handle count was read at entry and at exit",
             isinstance(R["handles"].get("before"), int) and isinstance(R["handles"].get("after"), int),
             "%r -> %r" % (R["handles"].get("before"), R["handles"].get("after")))
        gate("H no mutator call was REFUSED BY THE MACHINE", not refusals,
             "%d refusal(s): %r" % (len(refusals), [r["where"] for r in refusals]))
        left = [(os.path.basename(a["dest"]), a.get("md5"), a.get("size"))
                for a in R["artefacts_on_disk"] if a.get("exists")]
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
