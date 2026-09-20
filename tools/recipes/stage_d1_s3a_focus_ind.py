"""stage_d1_s3a_focus_ind - D1 STAGE S3a: ONE file carrying BOTH S3a indicators.

DELIVERABLE: claudeDev\\D1_s3a_focus_ind.vi, built from claudeDev\\D1_s2_loops.vi (md5 6ff19497...) by this
recipe, carrying BOTH front-panel indicators on Diagram #639:
  * the NUMERIC one, wired to #10757 t1 'element'  (wire 10990) - cycle 57's route, 35 pass / 0 fail
  * the BOOLEAN one, wired to #10686 t0 'x .and. y?' (wire 10799) - cycle 58's route, 36 pass / 0 fail
Both legs are REPLAYS of runs that already passed. NO new verb, NO new op VI, NO new device, NO discovery.

WHAT ALREADY EXISTED - checked on disk BEFORE a line of this was written (CLAUDE.md "check what already
exists"; 47(g) "before commissioning a read, grep the bench logs for the reading first"):
  * tools/gscript.py - every verb this recipe calls already exists and NONE is patched here:
      build_index_array :2322 · build_property :2194 · create_indicator :2388 · delete_object :2240 ·
      wire_indicators :1756 · node_info :2462 · node_terms_uid :925 · panel_wiring :826 · fp_labels :2440 ·
      report_all :488 · uids :1017 · count :1005 · exec_state :1977 · save :2062 · open_panel :1241 ·
      close_panel :1257 · ref_counts :233
  * tools/recipes/build_d1_v0.py - diag_index / owner_of / move_in (:318, :338, :357)
  * tools/recipes/build_opconnectnested_v1.py - connect_nested_v1, the 42(b) ordered-pass carrier
  * tools/bench/diag_s2_scaffold.py - fresh() / Preload() / file_facts(), unchanged
  * tools/bench/diag_s57_typepair.py - the NUMERIC leg, 35/0 (BGRUN END rc=0 after 242s). Its phases B/C/D/G/I
    are replayed here as N1/N2, helpers and gate shapes included, rather than re-invented.
  * tools/bench/diag_s58_boolwire.py - the BOOLEAN leg, 36/0 (BGRUN END rc=0 after 306s). Its B1/B2/B3 are
    replayed here as B1/B2/B3, helpers and gate shapes included.
  * tools/recipes/stage_d1_s1.py, stage_d1_s2.py, stage_d1_s2_loops.py - the stage-recipe shape this follows.
  NOTHING new is built. The only thing this file adds is the ORDER: both legs, one file, saves in between.

=====================================================================================================
THE TWO LEGS, AND WHY THEY DIFFER (Pre-decided 47(d) + 48(a)(b)):
  `Terminal.Create Indicator` 6349C02 takes NO type argument, so a created indicator inherits the TYPE of the
  terminal it is created from.
  LEG N - the carrier terminal is the Index Array's `index`, a SINK. No wire is created from a sink, which is
          exactly why that indicator comes out NUMERIC. Nothing to delete but the carrier.
  LEG B - a BOOLEAN type needs a SOURCE terminal, and create_indicator on a SOURCE makes a REAL Wire object
          (48(b): whole-VI Wire 1905 -> 1906). That wire is OURS and its uid is held, so it is deleted BY UID
          BEFORE the carrier (48(d)'s named fix, measured working in 48(j)).
  `remove_bad_wires_scripted` is REFUSED by 48(d) - measured over-removal on this VI
  (archive/2026-09-17-status-d1-route-b-2.md:45 "DELETES THE TUNNEL", a rule-1a hazard). It is NOT imported and
  NOT called; the GUI menu form (gscript.py:1629) is not called either. This run performs NO GUI action.

=====================================================================================================
SIX SUB-STEPS, SIX SAVE POINTS, EACH STARTING FROM THE PREVIOUS FILE IN A FRESH LabVIEW INSTANCE
(the user's 2026-09-19 rule: a step is not done until it has left a file; 47(e): the save goes at the LAST
point the VI is measured legal, before the next mutation; 42(b)/NAMES.md:912-918: the ordered second pass
leaves the VI at ExecState 0, so the SAVE always precedes the `Is Broken?` read and a RESTART always follows
it). Every index and every label is resolved LIVE (34(h)); nothing is cached across a restart except the
label STRING read off the machine, which is re-matched against a live panel row on the next file.

 N1  from claudeDev\\D1_s2_loops.vi -> claudeDev\\D1_s3a_focus_ind_n1_<stamp>.vi
     build_index_array at the `VI -> Block Diagram` head -> create_indicator(Nodes[k].Terminals[2] = 'index',
     a SINK, so NO wire) -> delete_object(IndexArray) -> ExecState 1 -> move_in(CT -> Diagram #639 at its LIVE
     Traverse index, (120,4000)) -> purge the junk `Invoke` in-run -> SAVE.
     PASS: owner_of(CT) == ('Diagram',639) AND ExecState == 1.
 N2  restart; cold from N1 -> ..._n2_<stamp>.vi
     wire_indicators(-> #10757 t1 'element', diagram_index = the LIVE index of the diagram the INDICATOR lives
     on, i.e. #639 - 47(b), gscript.py:1787-1789 scopes the INDICATOR lookup, never the source) -> SAVE ->
     THEN the ordered second pass (42(b)) -> `Is Broken?`.     PASS: Is Broken? == False.
 B1  restart; cold from N2 -> ..._b1_<stamp>.vi
     build_property('VI Server:VI',[242]) at the same head -> create_indicator on t4 'Def Err Handling', a
     SOURCE -> delete_object(target,'Wire',<idx>,verify=True) on THAT wire's uid (the uid resolved to a
     Traverse index off the LIVE `Wire` census; verify=True returns the uid SET that vanished) ->
     delete_object(Property carrier) -> ExecState 1 -> SAVE.     PASS: ExecState == 1.
 B2  restart; cold from B1 -> ..._b2_<stamp>.vi
     move_in(CT -> Diagram #639 @ LIVE index, (120,4200)) -> purge the junk `Invoke` -> SAVE.
     PASS: owner_of == ('Diagram',639) AND ExecState == 1.   *** 47(e)'s save point, BEFORE any wiring ***
 B3  restart; cold from B2 -> claudeDev\\D1_s3a_focus_ind.vi   *** THE DELIVERABLE'S OWN PATH ***
     wire_indicators(-> #10686 t0 'x .and. y?') -> SAVE -> THEN the ordered second pass -> `Is Broken?`.
     PASS: Is Broken? == False.
 Z0  restart; reopen claudeDev\\D1_s3a_focus_ind.vi COLD, READ ONLY - no mutation, no save.
     PASS: ExecState 1, BOTH ControlTerminals owned by ('Diagram',639), ControlTerminal census 116.

(gscript has NO save-as verb - save() persists to the target's OWN path, gscript.py:2062 - so each sub-step
works on a byte copy of the previous artefact at its own path. NOTHING SAVED IS EVER DELETED; an UNSAVED
working file, which is by construction a byte-identical duplicate of its parent, is removed.)

=====================================================================================================
PREDICTION CONTRACT - every gate is the readback of a CALL to the machine (46(g): a gate that makes no call
is a note, never a FAIL):
  T1     the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                      (FATAL)
  T1b    claudeDev\\D1_s1_copy.vi md5 == 3e3d23cefd3a334001aa9d6156bf1aee
  T2     claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                           (FATAL)
  N1_T3  the N1 working file is byte-identical to D1_s2_loops.vi at creation
  N1_A1  diag_index(#639) resolves to an int          N1_A2  diag_index(#536) resolves to 0
  N1_A3  owner_of(#10757) answers ('Diagram', 639)
  N1_A4  #10757 carries a SOURCE terminal named 'element' whose wire uid is read off the machine
  N1_a   build_index_array put exactly 1 new IndexArray on the target, owner ('TopLevelDiagram', 536)
  N1_a2  node_info(max_n=40) gained exactly ONE entry
  N1_a3  the carrier's terminal 2 is named 'index' and is a SINK (the 47(d) reason this leg is NUMERIC)
  N1_b   create_indicator returned a ControlTerminal and the census went 114 -> 115
  N1_b2  exactly ONE new front-panel row appeared and its label was READ off the machine
  N1_b3  create_indicator added ZERO whole-VI Wire objects   (the SINK contrast to 48(b)'s SOURCE behaviour)
  N1_b4  that label carries no newline and duplicates no existing panel label
  N1_c   delete_object removed exactly 1 IndexArray, and NO pre-existing wire uid disappeared
  N1_d   ExecState == 1 after the carrier delete
  N1_m   move_in returned without raising
  N1_c2  the ControlTerminal census is unchanged across the move
  N1_PASS owner_of(CT) == ('Diagram',639) AND ExecState == 1                *** THE N1 PASS CRITERION ***
  N1_S   g.save() returned a byte count and the version bytes read 26 00 80 00 (LV2026)
  N2_C   the COLD reopen of the N1 file reads ExecState 1
  N2_w   wire_indicators returned an EMPTY error column      (a RAISE is a LEGITIMATE reading, RISK (iii))
  N2_w2  the indicator's wire uid changed from 0                                        (the EFFECT gate)
  N2_w3  #10757's wired-terminal count is unchanged across the wiring                            (37(e))
  N2_w4  #637's terminal count is unchanged - NO tunnel and NO border object appeared            (37(e))
  N2_w5  the whole-VI Wire delta across the wiring is 0            (a BRANCH adds no Wire, :1771-1772)
  N2_S   ExecState == 1 at the save point and g.save() returned a byte count, version 26 00 80 00
  N2_PASS the ORDERED second-pass `Is Broken?` reads False                  *** THE N2 PASS CRITERION ***
  B1_C   the COLD reopen of the N2 file reads ExecState 1
  B1_a   build_property put exactly 1 new Property on the target, owner ('TopLevelDiagram', 536)
  B1_a2  node_info gained exactly ONE entry
  B1_a3  the terminal table holds a SOURCE terminal that is not reference out / error out
  B1_b   create_indicator returned a ControlTerminal and the census went 115 -> 116
  B1_b2  exactly ONE new front-panel row appeared and its label was READ off the machine
  B1_b3  create_indicator added EXACTLY ONE whole-VI Wire object                                  (48(b))
  B1_b4  that label carries no newline and duplicates no existing panel label (the numeric one included)
  B1_c   delete_object removed exactly 1 Wire
  B1_c2  the set that disappeared IS EXACTLY the wire create_indicator added         (the NARROWNESS gates,
  B1_c3  NO pre-existing wire uid disappeared                                                     rule 1a)
  B1_c4  the ControlTerminal census is unchanged across the wire delete
  B1_d   delete_object removed exactly 1 Property (the carrier)
  B1_PASS ExecState == 1 after BOTH deletes                                 *** THE B1 PASS CRITERION ***
  B1_S   g.save() returned a byte count and the version bytes read 26 00 80 00
  B2_C   the COLD reopen of the B1 file reads ExecState 1
  B2_m   move_in returned without raising     B2_c the ControlTerminal census is unchanged across the move
  B2_PASS owner_of(CT) == ('Diagram',639) AND ExecState == 1                *** THE B2 PASS CRITERION ***
  B2_S   g.save() returned a byte count and the version bytes read 26 00 80 00
  B3_C   the COLD reopen of the B2 file reads ExecState 1
  B3_w   wire_indicators returned an EMPTY error column        B3_w2 the indicator's wire uid changed from 0
  B3_w3  #10686's wired-terminal count is unchanged            B3_w4 #637's terminal count is unchanged
  B3_w5  the whole-VI Wire delta across the wiring is 0
  B3_S   ExecState == 1 at the save point and g.save() returned a byte count, version 26 00 80 00
  B3_PASS the ORDERED second-pass `Is Broken?` reads False                  *** THE B3 PASS CRITERION ***
  Z0_a   the DELIVERABLE reopens COLD, in a freshly restarted LabVIEW, at ExecState 1
  Z0_b   owner_of(the NUMERIC ControlTerminal) == ('Diagram', 639)
  Z0_c   owner_of(the BOOLEAN ControlTerminal) == ('Diagram', 639)
  Z0_d   the ControlTerminal census on the deliverable is 116 (114 at the S2 baseline, +1 per leg)
  Z1     ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 unchanged after everything
  Z2     refs opened == closed, 0 live

PREDICTED RISKS, written down BEFORE the run:
  (i)   move_in leaves JUNK `Invoke` node(s) - the uid a deleted object released (measured four times:
        probe_move_ctlterm_v0.log:135; cycle 57 dispatches 3/4; cycle 58 dispatches 1/2). Recorded, then
        purged in-run as tools/recipes/build_d1_routeb_v0.py:1279-1287 does; the purge set is `after - before`,
        so nothing pre-existing can be touched.
  (ii)  Nodes[] and Traverse indices SHIFT when an object is added to or removed from a diagram (34(h)). Every
        index is re-resolved by uid readback immediately before use, including after each cold reload.
  (iii) wire_indicators RAISES when the target reads ExecState != 1 after the connection (gscript.py:1794-1797)
        even though the connection WAS made. Captured VERBATIM; the leg continues to the save attempt and the
        ordered pass, exactly as cycle 57 dispatch 3 did.
  (iv)  the SECOND leg runs on a file that already carries the first leg's indicator, which the first two
        replays never did. The label-duplicate gate (B1_b4) and the census gates are what would catch a
        collision; wire_indicators selects the indicator BY LABEL, and the two labels differ ('index' vs
        'Automatic Error Handling'), both READ off the machine rather than retyped.
  (v)   a leg may reach ExecState 0 at a save point. Then NOTHING is saved, the run STOPS there with NO
        improvised repair (48(e)'s rule), and every artefact already on disk stands. That is a LEGITIMATE
        outcome and is reported as such - this recipe neither chooses nor recommends a route.

BOUNDS: NO VI IS RUN (34(f)). NO new op VI (47(i) route 2 is not this run's act). No new process device (user,
2026-09-18 08:53). No GUI action. No motor / ASI / camera (rig 조립 / ASSEMBLED). Originals are never opened
for write. `allow_broken` stays False and `gui_save` is NEVER called. Verification level is STRUCTURAL, never
functional. NO ROUTE IS CHOSEN OR RECOMMENDED - that is the judgement session's call.
"""
import contextlib
import io
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
from build_d1_v0 import diag_index, owner_of, move_in                              # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
import build_opconnectnested_v1 as CN1                                             # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "stage_d1_s3a_focus_ind_%s.json" % STAMP)
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

# ---- the six files. The LAST one is the deliverable and carries the name the plan gives it.
N1_PATH = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind_n1_%s.vi" % STAMP)
N2_PATH = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind_n2_%s.vi" % STAMP)
B1_PATH = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind_b1_%s.vi" % STAMP)
B2_PATH = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind_b2_%s.vi" % STAMP)
FINAL_PATH = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")

D639 = 639                      # the frame-loop BODY diagram (nested); owner WhileLoop #637
D536 = 536                      # the TopLevelDiagram (47(a)/47(b))
D686 = 686                      # the FlatSequenceFrame diagram that owns #637
LOOP11_UID = 637                # While loop 1.1 - the 37(e) tunnel/border witness
LOOP11_NODES_PIN = 4            # historical Nodes[] index of #637 on Diagram #686 - never trusted without echo

NUM_SRC_UID = 10757             # the NUMERIC payload source (45(c)); class measured IndexArray
NUM_TERM_NAME = "element"       # 45(c)'s name; READ back off the machine before it is used
NUM_TERM_INDEX_PIN = 1          # 47(i): #10757 terminals [(0,'array',sink),(1,'element',SOURCE),(2,'index',sink)]
NUM_WIRE_PIN = 10990            # a PIN, re-measured every time
NUM_NODES_PIN = None            # no historical Nodes[] index for #10757 on #639 - a bounded scan resolves it

BOOL_SRC_UID = 10686            # 'And', t0 'x .and. y?', wire 10799
BOOL_TERM_INDEX = 0             # the terminal 47(d) names; its NAME is read off the machine, never retyped
BOOL_WIRE_PIN = 10799           # a PIN, re-measured every time
BOOL_NODES_PIN = 25             # cycle 56/58 read #10686 at Nodes[] index 25 on #639

IA_TERM_INDEX = 2               # the Index Array terminal 46(a)/47(a) names for create_indicator ('index')
IA_TERM_NAME_EXPECT = "index"   # dispatch-verified reading; RE-READ here and gated, never retyped
NODE_LOCATION = (6200, 5200)    # far from every existing object; the carrier is deleted in the same sub-step
MOVE_POSITION_N = (120, 4000)   # a position INSIDE Diagram #639 (the brief's own coordinate)
MOVE_POSITION_B = (120, 4200)   # offset so the two indicators do not sit on top of each other - COSMETIC ONLY
SCAN_LIMIT = 80
NON_VALUE_SOURCE_TERMS = ("reference out", "error out")
CLASS_CANDIDATES = ("Function", "IndexArray", "SubVI", "Property", "Invoke", "CaseStructure", "WhileLoop",
                    "ForLoop", "Sequence", "EventStructure", "Constant", "LoopTunnel", "ControlTerminal",
                    "Bundle", "Unbundle", "ArraySubset")
CT_BASELINE_EXPECT = 114        # the S2 artefact's ControlTerminal census; RE-MEASURED, never assumed
CT_FINAL_EXPECT = 116           # 114 + one indicator per leg

# ---------------------------------------------------------------- the BOOLEAN carrier of record (48(c))
CARRIER = {
    "cid": "C2", "verb": "build_property", "cls": "VI Server:VI", "props": [("242", False)],
    "node_class": "Property",
    "what": "VI.Automatic Error Handling (242), Boolean R/W",
    "expected_carrier_terminal": "Def Err Handling",
    "expected_indicator_label": "Automatic Error Handling",   # READ off the machine twice already; re-read here
    "citation": "Pre-decided 48(c): C2 is the carrier of record - one property, ExecState 1 throughout its "
                "placement, indicator label non-duplicate and newline-free. C3 withdrawn (ExecState 0 at "
                "placement); C1 is the alternate and is not used here.",
}

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "D1 STAGE S3a: ONE file carrying BOTH indicators - the NUMERIC leg (cycle 57's route, 47(a)) and "
             "the BOOLEAN leg (cycle 58's route, 48(j)) - built from claudeDev\\D1_s2_loops.vi in six saved "
             "sub-steps, each starting from the PREVIOUS FILE in a FRESH LabVIEW instance.",
     "deliverable": FINAL_PATH,
     "both_legs_are_replays": {
         "numeric": "tools/bench/diag_s57_typepair.py, 35 pass / 0 fail, BGRUN END rc=0 after 242s",
         "boolean": "tools/bench/diag_s58_boolwire.py, 36 pass / 0 fail, BGRUN END rc=0 after 306s",
         "what_is_new_here": "only the ORDER: both legs on ONE file, with a save and a restart between them. "
                             "No new verb, no new op VI, no discovery."},
     "remove_bad_wires_scripted": "REFUSED by Pre-decided 48(d) (measured over-removal on this VI - "
                                  "archive/2026-09-17-status-d1-route-b-2.md:45 'DELETES THE TUNNEL', a rule-1a "
                                  "hazard). Not imported, not called; the GUI menu form (gscript.py:1629) is not "
                                  "called either.",
     "carrier": CARRIER,
     "chooses_no_route": True, "recommends_no_route": True, "interprets_nothing": True,
     "no_vi_was_run": True, "no_new_op": True, "no_new_device": True, "no_gui_action": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "verification_level": "STRUCTURAL (object counts, owners, ExecState, Is Broken?) - NEVER functional",
     "rig_state": "조립 / ASSEMBLED (motors + ASI forbidden; camera not needed and not touched)",
     "citations": {"numeric_route": "docs/cycle27-plan.md Pre-decided 47(a)",
                   "boolean_route": "Pre-decided 48(j)",
                   "created_wire_is_ours": "Pre-decided 48(b)",
                   "rbw_refused": "Pre-decided 48(d)",
                   "carrier_of_record": "Pre-decided 48(c)",
                   "save_at_the_last_legal_point": "Pre-decided 47(e)",
                   "wire_indicators_scopes_the_indicator": "Pre-decided 47(b); tools/gscript.py:1787-1789",
                   "no_type_argument_on_6349C02": "Pre-decided 47(d)",
                   "delete_object": "tools/gscript.py:2240",
                   "move_in_owner_of_diag_index": "tools/recipes/build_d1_v0.py:318,:338,:357",
                   "junk_invoke_purge": "tools/recipes/build_d1_routeb_v0.py:1279-1287",
                   "is_broken": "docs/NAMES.md:902-911",
                   "ordered_second_pass_perturbs_execstate": "Pre-decided 42(b); docs/NAMES.md:912-918",
                   "index_shift_after_mutation": "34(h)",
                   "branch_adds_no_wire_object": "tools/gscript.py:1771-1772",
                   "wire_indicators_raises_on_break": "tools/gscript.py:1794-1797",
                   "no_save_as_verb": "tools/gscript.py:2062 (save persists to the target's OWN path)",
                   "tunnel_border_grain": "Pre-decided 37(e)",
                   "gate_must_make_a_call": "Pre-decided 46(g)",
                   "a_step_leaves_a_file": "user 2026-09-19; CLAUDE.md 'Big or blocked work is SPLIT'"},
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "handles": {}, "hash_probe": [], "N1": {}, "N2": {}, "B1": {}, "B2": {}, "B3": {}, "Z0": {},
     "artefacts": [],
     "pass_criteria": {"N1": None, "N2": None, "B1": None, "B2": None, "B3": None, "Z0": None}}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
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


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["elapsed_s"] = round(time.time() - T_START, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def census(rec, tag, target):
    c = {}
    for k in ("Diagram", "WhileLoop", "SubVI", "Invoke", "Property", "IndexArray", "LoopTunnel", "Wire",
              "ControlTerminal", "Function"):
        try:
            c[k] = g.count(target, k)
        except Exception as e:                                                     # noqa: BLE001
            c[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    rec.setdefault("censuses", {})[tag] = c
    fact("class census [%s] %r" % (tag, c))
    return c


def read_exec_state(rec, tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    rec.setdefault("exec_state_timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def wire_uid_set(rec, tag, target):
    try:
        s = set(g.uids(target, "Wire"))
        err = ""
    except Exception as e:                                                         # noqa: BLE001
        s, err = set(), "%s: %s" % (type(e).__name__, str(e)[:160])
    rec.setdefault("wire_uid_reads", []).append({"tag": tag, "n": len(s), "error_verbatim": err})
    fact("whole-VI Wire uid SET [%s]: %d uids (error VERBATIM %r)" % (tag, len(s), err))
    return s


def panel_rows(target):
    try:
        return list(g.panel_wiring(target) or [])
    except Exception as e:                                                         # noqa: BLE001
        fact("panel_wiring raised %s: %s" % (type(e).__name__, str(e)[:200]))
        return []


def fp_label_list(target):
    try:
        return list(g.fp_labels(target, max_n=200) or [])
    except Exception as e:                                                         # noqa: BLE001
        fact("fp_labels raised %s: %s" % (type(e).__name__, str(e)[:200]))
        return []


def owner_read(rec, tag, uid, target):
    """owner_of with the strict identity-echo guard first, then non-strict - either answer is REPORTED."""
    rd = {"tag": tag, "uid": uid}
    for strict in (True, False):
        try:
            cls, ouid = owner_of(target, uid, strict=strict)
            rd.update({"strict": strict, "owner_class": cls, "owner_uid": ouid, "error_verbatim": ""})
            break
        except Exception as e:                                                     # noqa: BLE001
            rd.update({"strict": strict, "owner_class": None, "owner_uid": None,
                       "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:250])})
    rec.setdefault("owner_reads", []).append(rd)
    fact("%s: owner_of(#%s) = (%r, %r) [strict=%r] error VERBATIM %r"
         % (tag, uid, rd.get("owner_class"), rd.get("owner_uid"), rd.get("strict"), rd.get("error_verbatim")))
    return rd


def node_index_of(target, diagram_index, uid, pin):
    """The 34(h)-safe Nodes[] index: try the historical PIN, accept it ONLY if the uid echoes back, else scan."""
    if pin is not None:
        try:
            u, rows = g.node_terms_uid(target, diagram_index, pin)
            if u == uid:
                return pin, "pin %d survived its uid echo" % pin, rows
        except Exception as e:                                                     # noqa: BLE001
            fact("node_terms_uid(d=%r, pin=%r) raised %s: %s"
                 % (diagram_index, pin, type(e).__name__, str(e)[:140]))
    for i in range(SCAN_LIMIT):
        try:
            u, rows = g.node_terms_uid(target, diagram_index, i)
        except Exception:                                                          # noqa: BLE001
            break
        if not u:
            break
        if u == uid:
            return i, "bounded scan (pin %r did not echo)" % pin, rows
    return None, "NOT FOUND in a bounded scan of %d Nodes[] entries" % SCAN_LIMIT, []


def wired_counts(rec, tag, target, diagram_index, uid, pin):
    """(node uid readback, n terminals, n WIRED terminals, the rows) - the 37(e) per-node metric, index-safe."""
    out = {"tag": tag, "diagram_index": diagram_index, "uid_expect": uid}
    i, how, rows = node_index_of(target, diagram_index, uid, pin)
    out["node_index"] = i
    out["index_resolution"] = how
    if i is None:
        out["error"] = "node #%s was not found on diagram index %r" % (uid, diagram_index)
    else:
        out.update({"node_uid_readback": uid, "n_terms": len(rows),
                    "n_wired": sum(1 for r in rows if r.get("wire")),
                    "terms": [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                               "wire": r["wire"]} for r in rows]})
    rec.setdefault("wired_counts", []).append(out)
    fact("%s: node #%s at Nodes[%r] (%s), %r terminals, %r WIRED"
         % (tag, uid, i, how, out.get("n_terms"), out.get("n_wired")))
    return out


def class_membership(target, uid):
    rows, errs = [], {}
    for cls in CLASS_CANDIDATES:
        try:
            u = [o["uid"] for o in g.report_all(target, cls)]
        except Exception as e:                                                     # noqa: BLE001
            errs[cls] = "%s: %s" % (type(e).__name__, str(e)[:160])
            continue
        if uid in u:
            rows.append({"class": cls, "index": u.index(uid), "members": len(u)})
    return rows, errs


def close_quietly(target):
    try:
        g.close_panel(target)
    except Exception as e:                                                         # noqa: BLE001
        fact("close_panel(%s) raised %s: %s" % (os.path.basename(target), type(e).__name__, e))


def op_indicators():
    rd = {}
    try:
        vi = g.op(CN1.OP)
        for k in ("UID", "Name", "UID 2", "Is Broken?"):
            try:
                rd[k] = vi.GetControlValue(k)
            except Exception as e:                                                 # noqa: BLE001
                rd[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:60])
    except Exception as e:                                                         # noqa: BLE001
        rd["_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
    return rd


def pick_value_source(rows):
    """THE SELECTION RULE, fixed before the run: of the terminals READ OFF THE MACHINE, take the SOURCE ones,
    drop 'reference out'/'error out', take the FIRST that remains. NO TYPE IS ASSUMED."""
    sources = [r for r in rows if r.get("is_source")]
    valued = [r for r in sources if r.get("name") not in NON_VALUE_SOURCE_TERMS]
    if not valued:
        return None, ("no SOURCE terminal outside %r; sources were %r"
                      % (list(NON_VALUE_SOURCE_TERMS), [r.get("name") for r in sources]))
    return valued[0], ("first SOURCE terminal that is not %r; the candidates were %r"
                       % (list(NON_VALUE_SOURCE_TERMS), [r.get("name") for r in valued]))


def delete_by_uid(rec, tag, target, cls, uid):
    """delete_object(target, cls, index, verify=True) - tools/gscript.py:2240 - addresses by (Traverse CLASS,
    Traverse INDEX); there is no by-uid form in the fleet, so the uid is resolved to its index over the SAME
    class list the census uses. verify=True keeps the before/after uid snapshots, so the RETURN is the uid set
    that disappeared and the call raises unless exactly one object went."""
    rd = {"tag": tag, "class": cls, "uid": uid,
          "signature": "delete_object(target, cls, index, verify=True)  # tools/gscript.py:2240"}
    try:
        cur = [o["uid"] for o in g.report_all(target, cls)]
        rd["members"] = len(cur)
        rd["index"] = cur.index(uid)
    except Exception as e:                                                         # noqa: BLE001
        rd["index"] = None
        rd["error_verbatim"] = "index resolution failed %s: %s" % (type(e).__name__, str(e)[:250])
        rec.setdefault("deletes", []).append(rd)
        fact("%s: could NOT resolve #%r to a %s Traverse index - %s" % (tag, uid, cls, rd["error_verbatim"]))
        return rd
    try:
        gone = g.delete_object(target, cls, rd["index"])
        rd["gone"] = sorted(gone) if gone else gone
        rd["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rd["gone"] = None
        rd["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:500])
    rec.setdefault("deletes", []).append(rd)
    fact("%s: delete_object(target, %r, %r, verify=True) on uid #%r (of %r members) -> gone %r ; "
         "error VERBATIM %r" % (tag, cls, rd["index"], uid, rd.get("members"), rd.get("gone"),
                                rd["error_verbatim"]))
    return rd


def read_new_label(rec, tag, target, rows_before, fpl_before):
    """READ the newly created panel object's label OFF THE MACHINE, with its hex. Nothing is ever retyped."""
    rows_after = panel_rows(target)
    fpl_after = fp_label_list(target)
    before_keys = {(r.get("uid"), r.get("label")) for r in rows_before}
    new_rows = [r for r in rows_after if (r.get("uid"), r.get("label")) not in before_keys]
    before_fp = {(i, t) for (i, t, _ind) in fpl_before}
    new_fp = [(i, t, ind) for (i, t, ind) in fpl_after if (i, t) not in before_fp]
    label, label_source = None, None
    if len(new_rows) == 1 and new_rows[0].get("label") is not None:
        label, label_source = new_rows[0]["label"], "panel_wiring diff (the machine's own Control.Label text)"
    elif len(new_fp) == 1:
        label, label_source = new_fp[0][1], "fp_labels diff (the machine's own Control.Label text)"
    existing = [r.get("label") for r in rows_before]
    rd = {"tag": tag, "label_repr": repr(label), "label_source": label_source,
          "label_utf8_hex": (label or "").encode("utf-8").hex() if label is not None else None,
          "contains_newline": (("\n" in label) or ("\r" in label)) if label is not None else None,
          "is_duplicate_of_an_existing_panel_label": (label in existing) if label is not None else None,
          "new_panel_rows": new_rows, "new_fp_labels": new_fp,
          "existing_panel_labels_at_this_moment": existing}
    rec.setdefault("labels", []).append(rd)
    fact("%s THE LABEL, VERBATIM: %r  (utf-8 hex %r, source: %s)" % (tag, label, rd["label_utf8_hex"],
                                                                     label_source))
    fact("%s contains a NEWLINE: %r ; is a DUPLICATE of an existing panel label: %r"
         % (tag, rd["contains_newline"], rd["is_duplicate_of_an_existing_panel_label"]))
    return label, rd, new_rows, new_fp


def purge_junk_invokes(rec, tag, target, inv_before):
    """PREDICTED RISK (i): the junk `Invoke` residue move_in/the ops leave behind. The purge set is
    `after - before`, so nothing pre-existing can be touched (build_d1_routeb_v0.py:1279-1287)."""
    try:
        inv_after = set(g.uids(target, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_after = set()
        fact("%s uids(Invoke) AFTER raised %s: %s" % (tag, type(e).__name__, str(e)[:140]))
    junk = sorted(inv_after - inv_before)
    rec.setdefault("junk_invokes", []).append({"tag": tag, "uids": junk})
    fact("%s left %r junk `Invoke`(s): %r (PREDICTED RISK (i))" % (tag, len(junk), junk))
    out = []
    for ju in junk:
        out.append(delete_by_uid(rec, "%s junk Invoke purge" % tag, target, "Invoke", ju))
    return junk, out


def save_if_legal(K, tag, target, role, step):
    """The save goes at the LAST point the VI is measured legal (47(e)). allow_broken stays False and
    gui_save is NEVER called; an ExecState != 1 here STOPS the sub-step with NO improvised repair."""
    es_save = read_exec_state(K, "%s immediately before the save attempt" % tag, target)
    size, serr = None, None
    if isinstance(es_save, int) and es_save == 1:
        try:
            size = g.save(target)
        except Exception as e:                                                     # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:400])
    else:
        serr = ("NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved. Under 47(e)/48(e) that STOPS "
                "the run here with NO improvised repair - a legitimate outcome, reported as such." % (es_save,))
    K["exec_state_before_save"] = es_save
    K["saved_bytes"] = size
    K["save_reason_verbatim"] = serr
    K["allow_broken"] = False
    K["gui_save"] = False
    fact("%s g.save() returned %r ; exception/reason VERBATIM %r" % (tag, size, serr))
    K["file_after"] = D.file_facts("%s the artefact after the save attempt" % tag, target)
    R["artefacts"].append({"step": step, "role": role, "path": target, "saved": isinstance(size, int),
                           "file": K["file_after"]})
    vb = K["file_after"].get("version_candidates") if K["file_after"].get("exists") else None
    gate("%s_S g.save() returned a byte count and the version bytes read 26 00 80 00 (LV2026)" % step,
         isinstance(size, int) and size > 0 and bool(K["file_after"].get("exists"))
         and any("26 00 80 00" in c.get("bytes", "") for c in (vb or [])),
         "ExecState %r, bytes %r, version %r, reason %r" % (es_save, size, vb, serr))
    dump()
    return size


def cold_start(K, step, src_path, dst_path, note):
    """Restart LabVIEW, byte-copy the previous artefact to this sub-step's own path (no save-as verb,
    gscript.py:2062), and report the handles across the restart."""
    print("\n===================================================================", flush=True)
    print("=== %s   from %s, COLD, in a FRESH LabVIEW ; -> %s"
          % (step, os.path.basename(src_path), os.path.basename(dst_path)), flush=True)
    print("=== %s" % note, flush=True)
    print("===================================================================", flush=True)
    K["handles_before_restart"] = labview_handles()
    D.fresh("%s RESTART (so the previous file loads COLD, from disk, with nothing preloaded)" % step)
    K["handles_after_restart"] = labview_handles()
    fact("%s LabVIEW handles across the restart: %r -> %r"
         % (step, K["handles_before_restart"], K["handles_after_restart"]))
    if os.path.exists(dst_path):
        os.remove(dst_path)
    shutil.copy2(src_path, dst_path)
    q = probe("%s the working file at creation (byte copy of the previous artefact)" % step, dst_path)
    K["file_at_creation"] = q
    K["source_file"] = src_path
    K["working_file"] = dst_path
    fact("%s the working file is a byte copy of %s (md5 %s)" % (step, os.path.basename(src_path), q.get("md5")))
    dump()
    return q


def resolve_diagrams(K, step, target, uids=(D639, D536, D686)):
    out = {}
    for uid in uids:
        key = "diag_index_%d" % uid
        try:
            out[uid] = diag_index(target, uid)
            K[key] = out[uid]
            K[key + "_error_verbatim"] = ""
        except Exception as e:                                                    # noqa: BLE001
            out[uid] = None
            K[key] = None
            K[key + "_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s diag_index(#%d) LIVE on this file = %r ; error VERBATIM %r"
             % (step, uid, out[uid], K[key + "_error_verbatim"]))
    return out


# ===================================================================== the shared WIRING + ORDERED PASS
def wire_leg(K, step, target, src_uid, src_nodes_pin, term_pick, label, wire_pin):
    """wire_indicators + the 37(e) censuses + the SAVE + the ORDERED second pass (42(b)) + `Is Broken?`.
    `term_pick` is a callable(rows) -> the source terminal row, READ off the machine on THIS file."""
    dd = resolve_diagrams(K, step, target)
    d639, d686 = dd[D639], dd[D686]

    rows_live, errs_live = class_membership(target, src_uid)
    K["class_membership_live"] = rows_live
    K["class_scan_errors_verbatim"] = errs_live
    chosen = next((r for r in rows_live if r["class"] == "Function"), None)
    if chosen is None and rows_live:
        chosen = sorted(rows_live, key=lambda r: r["members"])[0]
    K["chosen_class_row_live"] = chosen
    K["chosen_rule"] = ("`Function` when it holds the uid (the addressing both proven legs used); otherwise "
                        "the class with the fewest members that holds it.")
    fact("%s LIVE: diag_index(#639) = %r, #%d class membership %r, addressing it as %r"
         % (step, d639, src_uid, rows_live, chosen))

    src_before = wired_counts(K, "%s BEFORE #%d (the source node)" % (step, src_uid), target,
                              d639 if isinstance(d639, int) else 0, src_uid, src_nodes_pin)
    st = term_pick(src_before.get("terms", []))
    K["source_terminal_live"] = st
    fact("%s #%d's FULL terminal list: %r" % (step, src_uid, src_before.get("terms")))
    fact("%s the source terminal READ off the machine: %r (utf-8 hex %r); the recorded wire PIN is %r"
         % (step, st, (st or {}).get("name", "").encode("utf-8").hex(), wire_pin))
    loop_before = wired_counts(K, "%s BEFORE #%d (loop 1.1, the tunnel/border witness)" % (step, LOOP11_UID),
                               target, d686 if isinstance(d686, int) else 0, LOOP11_UID, LOOP11_NODES_PIN)

    rows_p = panel_rows(target)
    row_now = next((r for r in rows_p if r.get("label") == label), None)
    K["target_row_before_wiring"] = row_now
    label_live = (row_now or {}).get("label")
    fact("%s the indicator row re-read on this file: %r (label VERBATIM %r, utf-8 hex %r)"
         % (step, row_now, label_live, (label_live or "").encode("utf-8").hex()))

    wire_b = (row_now or {}).get("wire")
    wires_b = g.count(target, "Wire")
    es_pre = read_exec_state(K, "%s BEFORE wire_indicators" % step, target)
    wi_dt, wi_err = None, None
    if not chosen or st is None or not isinstance(d639, int) or label_live is None:
        wi_err = ("NOT ATTEMPTED: class row %r / terminal %r / diagram index %r / label %r unresolved."
                  % (chosen, st, d639, label_live))
    else:
        try:
            wi_dt = g.wire_indicators(target, chosen["index"], [st["name"]], [label_live],
                                      diagram_index=d639, node_class=chosen["class"])
            wi_err = ""
        except Exception as e:                                                     # noqa: BLE001
            wi_err = "%s: %s" % (type(e).__name__, str(e)[:900])
    K["wire_indicators"] = {"node_index": (chosen or {}).get("index"),
                            "node_class": (chosen or {}).get("class"),
                            "src_terms_repr": repr([(st or {}).get("name")]),
                            "indicator_names_repr": repr([label_live]),
                            "indicator_names_utf8_hex": [(label_live or "").encode("utf-8").hex()],
                            "diagram_index": d639,
                            "diagram_index_rule": "47(b): the LIVE index of the diagram the INDICATOR's terminal "
                                                  "lives on (#639), never the source's - gscript.py:1787-1789",
                            "seconds": wi_dt, "error_verbatim": wi_err}
    fact("%s wire_indicators(%s[%r], [%r] -> [%r], diagram_index=%r) error VERBATIM %r"
         % (step, (chosen or {}).get("class"), (chosen or {}).get("index"), (st or {}).get("name"), label_live,
            d639, wi_err))
    gate("%s_w wire_indicators returned an EMPTY error column" % step, wi_err == "",
         "%r (PREDICTED RISK (iii): a raise is a LEGITIMATE reading)" % (wi_err,))

    rows_w = panel_rows(target)
    row_w = next((r for r in rows_w if r.get("label") == label), None)
    wire_a = (row_w or {}).get("wire")
    wires_a = g.count(target, "Wire")
    K["target_row_after_wiring"] = row_w
    K["target_wire_uid"] = {"before": wire_b, "after": wire_a}
    delta = (wires_a - wires_b) if isinstance(wires_a, int) and isinstance(wires_b, int) else None
    K["whole_vi_wire_count"] = {"before": wires_b, "after": wires_a, "delta": delta}
    fact("%s the indicator's wire uid %r -> %r ; whole-VI Wire count %r -> %r (delta %r; a BRANCH adds NO Wire "
         "object, tools/gscript.py:1771-1772). The source terminal's own wire reads %r (recorded pin %r)"
         % (step, wire_b, wire_a, wires_b, wires_a, delta, (st or {}).get("wire"), wire_pin))
    gate("%s_w2 the indicator's wire uid changed from 0" % step, bool(wire_a) and wire_a != wire_b,
         "%r -> %r" % (wire_b, wire_a))
    gate("%s_w5 the whole-VI Wire delta across the wiring is 0 (a branch onto an existing net)" % step,
         delta == 0, "%r -> %r (delta %r)" % (wires_b, wires_a, delta))
    es_post = read_exec_state(K, "%s AFTER wire_indicators" % step, target)
    K["exec_state"] = {"before": es_pre, "after": es_post}

    src_after = wired_counts(K, "%s AFTER #%d (the source node)" % (step, src_uid), target,
                             d639 if isinstance(d639, int) else 0, src_uid, src_nodes_pin)
    loop_after = wired_counts(K, "%s AFTER #%d (loop 1.1, the tunnel/border witness)" % (step, LOOP11_UID),
                              target, d686 if isinstance(d686, int) else 0, LOOP11_UID, LOOP11_NODES_PIN)
    gate("%s_w3 #%d's wired-terminal count is unchanged across the wiring (37(e))" % (step, src_uid),
         src_before.get("n_wired") is not None and src_after.get("n_wired") is not None
         and src_before.get("n_wired") == src_after.get("n_wired"),
         "%r -> %r wired of %r -> %r terminals" % (src_before.get("n_wired"), src_after.get("n_wired"),
                                                   src_before.get("n_terms"), src_after.get("n_terms")))
    gate("%s_w4 #%d's terminal count unchanged - NO tunnel or border object appeared (37(e))"
         % (step, LOOP11_UID),
         loop_before.get("n_terms") is not None and loop_before.get("n_terms") == loop_after.get("n_terms"),
         "%r -> %r terminals, %r -> %r wired"
         % (loop_before.get("n_terms"), loop_after.get("n_terms"),
            loop_before.get("n_wired"), loop_after.get("n_wired")))
    fact("%s_w4 EXPLICIT (37(e) grain): #%d terminals %r -> %r, wired %r -> %r; a tunnel or border object would "
         "show as a terminal-count INCREASE. Increase observed: %r"
         % (step, LOOP11_UID, loop_before.get("n_terms"), loop_after.get("n_terms"),
            loop_before.get("n_wired"), loop_after.get("n_wired"),
            (loop_after.get("n_terms") or 0) - (loop_before.get("n_terms") or 0)))
    census(K, "%s after the wiring attempt" % step, target)
    dump()

    # ---- the SAVE comes BEFORE the ordered pass: the `Is Broken?` read perturbs ExecState (NAMES.md:912-918)
    print("\n--------- %s SAVE  (IFF ExecState == 1; every earlier artefact stands either way)" % step,
          flush=True)
    size = save_if_legal(K, step, target, "indicator WIRED to #%d" % src_uid, step)

    # ---- the ORDERED SECOND PASS (42(b)) - THE TYPE ANSWER
    print("\n--------- %s ORDERED SECOND PASS (42(b)): `Is Broken?` AFTER the save" % step, flush=True)
    P = K.setdefault("ordered_pass", {})
    if not wire_a:
        P["not_attempted_because"] = ("the wiring produced no wire on the indicator (uid %r -> %r), so 42(b)'s "
                                      "ordered pass has nothing to read." % (wire_b, wire_a))
        fact("%s ORDERED PASS NOT ATTEMPTED: %s" % (step, P["not_attempted_because"]))
        gate("%s_PASS *** THE %s PASS CRITERION: the ORDERED `Is Broken?` reads False ***" % (step, step), False,
             "NOT ATTEMPTED: %s" % P["not_attempted_because"])
        dump()
        return size
    src_i, src_how, _rows = node_index_of(target, d639, src_uid, src_nodes_pin)
    net_wire = (st or {}).get("wire")
    sink = None
    if isinstance(d639, int) and net_wire:
        for i in range(SCAN_LIMIT):
            try:
                u, rows_n = g.node_terms_uid(target, d639, i)
            except Exception:                                                      # noqa: BLE001
                break
            if not u:
                break
            if u == src_uid:
                continue
            for r in rows_n:
                if r.get("wire") == net_wire and not r.get("is_source"):
                    sink = {"node_uid": u, "node_index": i, "term_index": r["i"], "term_name": r["name"],
                            "wire": r["wire"]}
                    break
            if sink:
                break
    P["source"] = {"uid": src_uid, "node_index": src_i, "index_resolution": src_how,
                   "term_index": (st or {}).get("i"), "term_name": (st or {}).get("name"), "wire": net_wire}
    P["sink_discovered"] = sink
    P["method"] = ("an IDEMPOTENT re-connect of an EXISTING connection on the SAME net (wire %r): the source "
                   "terminal #%d into a non-source terminal already carrying that wire, DISCOVERED by a bounded "
                   "scan of Diagram #%d. A front-panel ControlTerminal is not in Nodes[], so no 6371004 carrier "
                   "can address the indicator end; the same NET is read instead. wire_delta must be 0."
                   % (net_wire, src_uid, D639))
    fact("%s the ordered pass will re-connect: source %r -> sink %r" % (step, P["source"], sink))
    if sink is None or src_i is None:
        P["not_attempted_because"] = ("the 6371004 carrier needs BOTH ends addressable in Nodes[]: source index "
                                      "%r, a sink already on wire %r %r." % (src_i, net_wire, sink))
        fact("%s ORDERED PASS NOT ATTEMPTED: %s" % (step, P["not_attempted_because"]))
        gate("%s_PASS *** THE %s PASS CRITERION: the ORDERED `Is Broken?` reads False ***" % (step, step), False,
             "NOT ATTEMPTED: %s" % P["not_attempted_because"])
        dump()
        return size
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, d639, sink["node_index"], sink["term_index"],
                                     d639, src_i, (st or {}).get("i", 0), V1_LABELS)
        P.update({"wire_delta": dw, "exec_state_returned": es, "error_verbatim": err})
    except Exception as e:                                                         # noqa: BLE001
        P.update({"wire_delta": None, "exec_state_returned": None,
                  "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    P["op_indicators"] = op_indicators()
    ib = P["op_indicators"].get("Is Broken?")
    P["is_broken_ordered"] = ib
    R["pass_criteria"][step] = ib
    fact("%s ORDERED `Is Broken?` = %r on wire uid %r (op error column %r, wire_delta %r - expected 0). EITHER "
         "value is a LEGITIMATE reading: it IS this leg's answer."
         % (step, ib, P["op_indicators"].get("UID 2"), P.get("error_verbatim"), P.get("wire_delta")))
    gate("%s_PASS *** THE %s PASS CRITERION: the ORDERED `Is Broken?` reads False ***" % (step, step),
         ib is False,
         "Is Broken? = %r on wire %r ; wire_delta %r ; op error %r"
         % (ib, P["op_indicators"].get("UID 2"), P.get("wire_delta"), P.get("error_verbatim")))
    read_exec_state(K, "%s after the Is Broken? read (SUSPECT, docs/NAMES.md:912-918; the save already happened)"
                    % step, target)
    dump()
    return size


# ============================================================================== SUB-STEP N1
def step_n1():
    """from D1_s2_loops.vi: build_index_array -> create_indicator('index', a SINK) -> delete the carrier ->
    ExecState 1 -> move_in onto Diagram #639 -> purge the junk Invoke -> SAVE."""
    K = R["N1"]
    target = N1_PATH
    print("\n===================================================================", flush=True)
    print("=== N1   from D1_s2_loops.vi ; %s" % os.path.basename(target), flush=True)
    print("=== LEG N - the NUMERIC indicator (47(a)); its carrier terminal is a SINK, so NO wire is created",
          flush=True)
    print("===================================================================", flush=True)
    K["working_file"] = target
    K["source_file"] = S2_ARTEFACT
    if os.path.exists(target):
        os.remove(target)
    shutil.copy2(S2_ARTEFACT, target)
    p = probe("N1_T3 the working file at creation (copied from D1_s2_loops.vi)", target)
    K["file_at_creation"] = p
    gate("N1_T3 the N1 working file is byte-identical to D1_s2_loops.vi at creation", p.get("md5") == S2_MD5,
         "%s (expected %s)" % (p.get("md5", "?"), S2_MD5))
    dump()
    with D.Preload("N1"):
        g.open_panel(target)
        time.sleep(1.0)
        try:
            _n1_body(K, target)
        finally:
            close_quietly(target)
    dump()
    return isinstance(K.get("saved_bytes"), int)


def _n1_body(K, target):
    print("\n--------- N1 A  (resolve LIVE; assume nothing, 34(h))", flush=True)
    base = census(K, "N1 before everything", target)
    dd = resolve_diagrams(K, "N1", target)
    d639, d536 = dd[D639], dd[D536]
    gate("N1_A1 diag_index(#639) resolves to an int", isinstance(d639, int),
         "%r (the historical 43 / 46 are NOT reused)" % (d639,))
    gate("N1_A2 diag_index(#536) resolves to 0", d536 == 0, "%r" % (d536,))
    if not isinstance(d639, int) or not isinstance(d536, int):
        raise Stop("N1: diag_index(#639)=%r / diag_index(#536)=%r did not resolve." % (d639, d536))

    A = K.setdefault("A", {})
    A["owner_of_10757"] = owner_read(K, "N1_A3 owner of the NUMERIC source #%d" % NUM_SRC_UID, NUM_SRC_UID,
                                     target)
    gate("N1_A3 owner_of(#%d) answers ('Diagram', 639)" % NUM_SRC_UID,
         (A["owner_of_10757"].get("owner_class"), A["owner_of_10757"].get("owner_uid")) == ("Diagram", D639),
         "(%r, %r)" % (A["owner_of_10757"].get("owner_class"), A["owner_of_10757"].get("owner_uid")))
    num_terms = wired_counts(K, "N1_A4 the NUMERIC source #%d" % NUM_SRC_UID, target, d639, NUM_SRC_UID,
                             NUM_NODES_PIN)
    el = next((t for t in num_terms.get("terms", []) if t["name"] == NUM_TERM_NAME), None)
    A["element_terminal"] = el
    fact("N1_A4 #%d's FULL terminal list: %r" % (NUM_SRC_UID, num_terms.get("terms")))
    fact("N1_A4 the %r terminal READ off the machine: %r (utf-8 hex %r); the recorded index pin is %r and the "
         "recorded wire pin is %r"
         % (NUM_TERM_NAME, el, (el or {}).get("name", "").encode("utf-8").hex(), NUM_TERM_INDEX_PIN,
            NUM_WIRE_PIN))
    gate("N1_A4 #%d carries a SOURCE terminal named %r whose wire uid was read off the machine"
         % (NUM_SRC_UID, NUM_TERM_NAME),
         bool(el) and bool(el.get("is_source")) and bool(el.get("wire")), "%r" % (el,))

    # ---------------------------------------------------- N1a: place the Index Array carrier
    print("\n--------- N1a  (build_index_array at the `VI -> Block Diagram` head)", flush=True)
    B = K.setdefault("place", {})
    rows_before = panel_rows(target)
    fpl_before = fp_label_list(target)
    ct_before = g.count(target, "ControlTerminal")
    B["panel_rows_before"] = len(rows_before)
    B["control_terminal_before"] = ct_before
    fact("N1a the S2 baseline ControlTerminal census is %r (the recorded baseline is %r)"
         % (ct_before, CT_BASELINE_EXPECT))
    R["control_terminal_baseline"] = ct_before
    es_base = read_exec_state(K, "N1 BASELINE, before any mutation", target)
    B["exec_state_baseline"] = es_base
    B["wire_count_baseline"] = base.get("Wire")
    wires_base = wire_uid_set(K, "N1 BASELINE", target)

    try:
        top0 = g.node_info(target, max_n=40)
        B["node_info_before_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        top0 = None
        B["node_info_before_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    B["node_info_before"] = top0
    fact("N1a node_info(max_n=40) BEFORE: %r entries -> %r ; error VERBATIM %r"
         % (len(top0) if isinstance(top0, list) else top0, top0, B["node_info_before_error_verbatim"]))

    new_ia, ia_err = None, None
    try:
        new_ia = g.build_index_array(target, NODE_LOCATION)
        ia_err = ""
    except Exception as e:                                                         # noqa: BLE001
        ia_err = "%s: %s" % (type(e).__name__, str(e)[:600])
    B["call"] = "build_index_array(target, %r)" % (NODE_LOCATION,)
    B["new"] = new_ia
    B["error_verbatim"] = ia_err
    fact("N1a %s -> new %r ; error VERBATIM %r" % (B["call"], new_ia, ia_err))
    ia_uid = (new_ia[0]["uid"] if isinstance(new_ia, list) and new_ia else None)
    ia_owner = owner_read(K, "N1a the new IndexArray's owner", ia_uid, target) if ia_uid else {}
    B["carrier_uid"] = ia_uid
    B["carrier_owner"] = ia_owner
    gate("N1_a build_index_array put 1 new IndexArray on the target, owner ('TopLevelDiagram', 536)",
         isinstance(new_ia, list) and len(new_ia) == 1
         and (ia_owner.get("owner_class"), ia_owner.get("owner_uid")) == ("TopLevelDiagram", D536),
         "new %r, owner (%r, %r), error %r"
         % (new_ia, ia_owner.get("owner_class"), ia_owner.get("owner_uid"), ia_err))
    if ia_uid is None:
        raise Stop("N1: build_index_array placed no node (error VERBATIM %r)." % (ia_err,))

    try:
        top1 = g.node_info(target, max_n=40)
        B["node_info_after_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        top1 = None
        B["node_info_after_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    B["node_info_after"] = top1
    n0 = len(top0) if isinstance(top0, list) else None
    n1 = len(top1) if isinstance(top1, list) else None
    fact("N1a node_info(max_n=40) AFTER: %r entries -> %r ; error VERBATIM %r"
         % (n1, top1, B["node_info_after_error_verbatim"]))
    gate("N1_a2 node_info gained exactly ONE entry", n0 is not None and n1 is not None and n1 == n0 + 1,
         "%r -> %r" % (n0, n1))
    node_i = (top1[-1][0] if isinstance(top1, list) and top1 else None)
    B["node_index"] = node_i

    tt, tt_err = [], ""
    if node_i is not None:
        try:
            u_echo, rows_t = g.node_terms_uid(target, d536, node_i)
            B["node_uid_echo"] = u_echo
            tt = [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]), "wire": r["wire"]}
                  for r in rows_t]
        except Exception as e:                                                     # noqa: BLE001
            tt_err = "%s: %s" % (type(e).__name__, str(e)[:300])
    B["terminal_table"] = tt
    B["terminal_table_error_verbatim"] = tt_err
    fact("N1a THE CARRIER'S FULL TERMINAL TABLE [(index, label, is_source, wire)], READ OFF THE MACHINE: %r "
         "(uid echo %r; error VERBATIM %r)" % (tt, B.get("node_uid_echo"), tt_err))
    carrier_term = next((t for t in tt if t["i"] == IA_TERM_INDEX), None)
    B["chosen_terminal"] = carrier_term
    fact("N1a the terminal create_indicator will be called on: %r (utf-8 hex %r) - the recorded reading is %r, "
         "a SINK, which is 47(d)'s reason this leg comes out NUMERIC"
         % (carrier_term, (carrier_term or {}).get("name", "").encode("utf-8").hex(), IA_TERM_NAME_EXPECT))
    gate("N1_a3 the carrier's terminal %d is named %r and is a SINK" % (IA_TERM_INDEX, IA_TERM_NAME_EXPECT),
         bool(carrier_term) and carrier_term.get("name") == IA_TERM_NAME_EXPECT
         and not carrier_term.get("is_source"), "%r" % (carrier_term,))
    B["exec_state_after_place"] = read_exec_state(K, "N1a after build_index_array placed the carrier", target)
    B["wire_count_after_place"] = g.count(target, "Wire")
    dump()

    # ---------------------------------------------------- N1b: create the indicator
    print("\n--------- N1b  (create_indicator on the SINK terminal; 6349C02 takes NO type argument, 47(d))",
          flush=True)
    C = K.setdefault("create", {})
    new_ct, ci_err = None, None
    try:
        new_ct = g.create_indicator(target, node_i, IA_TERM_INDEX)
        ci_err = ""
    except Exception as e:                                                         # noqa: BLE001
        ci_err = "%s: %s" % (type(e).__name__, str(e)[:600])
    ct_after = g.count(target, "ControlTerminal")
    new_ct_uid = (new_ct[0].get("uid") if isinstance(new_ct, list) and new_ct else None)
    C.update({"node_index": node_i, "terminal_index": IA_TERM_INDEX,
              "terminal_name": (carrier_term or {}).get("name"), "new": new_ct, "new_ct_uid": new_ct_uid,
              "error_verbatim": ci_err, "control_terminal_before": ct_before,
              "control_terminal_after": ct_after})
    fact("N1b create_indicator(Nodes[%r].Terminals[%r] = %r) -> new %r ; error VERBATIM %r"
         % (node_i, IA_TERM_INDEX, (carrier_term or {}).get("name"), new_ct, ci_err))
    gate("N1_b create_indicator returned a ControlTerminal and the census went %r -> %r" % (ct_before, ct_after),
         isinstance(new_ct_uid, int) and isinstance(ct_before, int) and ct_after == ct_before + 1,
         "new uid %r, census %r -> %r, error %r" % (new_ct_uid, ct_before, ct_after, ci_err))
    if not isinstance(new_ct_uid, int):
        raise Stop("N1: create_indicator returned no ControlTerminal uid (error VERBATIM %r)." % (ci_err,))
    C["exec_state_after_create"] = read_exec_state(K, "N1b after create_indicator", target)
    C["wire_count_after_create"] = g.count(target, "Wire")
    wires_created = wire_uid_set(K, "N1b after create_indicator", target)
    added = sorted(wires_created - wires_base)
    C["wire_uids_added_by_create_indicator"] = added
    fact("N1b whole-VI Wire count %r -> %r -> %r ; the wire uid(s) create_indicator ADDED: %r  (48(b) says a "
         "SOURCE terminal makes ONE; this carrier terminal is a SINK, so the prediction is ZERO)"
         % (B["wire_count_baseline"], B["wire_count_after_place"], C["wire_count_after_create"], added))
    gate("N1_b3 create_indicator added ZERO whole-VI Wire objects (the SINK contrast to 48(b))",
         len(added) == 0, "added %r (count %r -> %r)"
         % (added, B["wire_count_after_place"], C["wire_count_after_create"]))

    label, lrec, new_rows, new_fp = read_new_label(K, "N1b", target, rows_before, fpl_before)
    C["label_record"] = lrec
    gate("N1_b2 exactly ONE new front-panel row appeared and its label was READ off the machine",
         (len(new_rows) == 1 or (not new_rows and len(new_fp) == 1)) and label is not None,
         "%r new panel row(s), %r new fp_labels entr(y/ies), label %r" % (len(new_rows), len(new_fp), label))
    if label is None:
        raise Stop("N1: the indicator's label could not be READ off the machine, and a label is never retyped.")
    gate("N1_b4 the label carries no newline and duplicates no existing panel label",
         lrec.get("contains_newline") is False
         and lrec.get("is_duplicate_of_an_existing_panel_label") is False,
         "newline %r, duplicate %r, label %r" % (lrec.get("contains_newline"),
                                                 lrec.get("is_duplicate_of_an_existing_panel_label"), label))
    K["new_ct_uid"] = new_ct_uid
    K["label"] = label
    R["numeric_indicator"] = {"uid": new_ct_uid, "label": label, "label_utf8_hex": lrec.get("label_utf8_hex")}
    dump()

    # ---------------------------------------------------- N1c: delete the carrier
    print("\n--------- N1c  (delete the IndexArray carrier - nothing else to delete, the terminal was a SINK)",
          flush=True)
    Dd = K.setdefault("carrier_delete", {})
    rd = delete_by_uid(K, "N1c the IndexArray carrier", target, "IndexArray", ia_uid)
    Dd["delete"] = rd
    wires_final = wire_uid_set(K, "N1c after the carrier delete", target)
    Dd["wire_count_after_carrier_delete"] = g.count(target, "Wire")
    Dd["pre_existing_uids_that_disappeared"] = sorted(wires_base - wires_final)
    ct_post = g.count(target, "ControlTerminal")
    Dd["control_terminal_after_delete"] = ct_post
    gate("N1_c delete_object removed exactly 1 IndexArray and NO pre-existing wire uid disappeared",
         isinstance(rd.get("gone"), list) and len(rd["gone"]) == 1
         and Dd["pre_existing_uids_that_disappeared"] == [],
         "gone %r ; pre-existing wire uids lost %r ; ControlTerminal %r -> %r ; error %r"
         % (rd.get("gone"), Dd["pre_existing_uids_that_disappeared"], ct_after, ct_post,
            rd.get("error_verbatim")))
    es_after_del = read_exec_state(K, "N1c after the carrier delete", target)
    Dd["exec_state_after_delete"] = es_after_del
    gate("N1_d ExecState == 1 after the carrier delete", es_after_del == 1, "%r" % (es_after_del,))
    fact("N1 ExecState TIMELINE: %r (baseline) -> %r (after build_index_array) -> %r (after create_indicator) "
         "-> %r (after the CARRIER delete)"
         % (es_base, B["exec_state_after_place"], C["exec_state_after_create"], es_after_del))
    dump()

    # ---------------------------------------------------- N1d: move_in onto Diagram #639
    print("\n--------- N1d  (move_in the ControlTerminal onto Diagram #639 at its LIVE Traverse index)",
          flush=True)
    M = K.setdefault("move", {})
    M["owner_before"] = owner_read(K, "N1d the ControlTerminal's owner BEFORE the move", new_ct_uid, target)
    ct_b = g.count(target, "ControlTerminal")
    rows_b = panel_rows(target)
    es_b = read_exec_state(K, "N1d BEFORE the move", target)
    try:
        inv_before = set(g.uids(target, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_before = set()
        fact("N1d uids(Invoke) BEFORE raised %s: %s" % (type(e).__name__, str(e)[:140]))
    d639_live = diag_index(target, D639)
    M["diag_index_639_live_at_move"] = d639_live
    fact("N1d diag_index(#639) RE-RESOLVED immediately before the move (34(h)) = %r" % (d639_live,))
    mv_ret, mv_err = None, None
    try:
        mv_ret = move_in(target, new_ct_uid, d639_live, MOVE_POSITION_N)
        mv_err = ""
    except Exception as e:                                                         # noqa: BLE001
        mv_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    M["move_in"] = {"call": "move_in(target, %r, %r, %r)" % (new_ct_uid, d639_live, MOVE_POSITION_N),
                    "returned": mv_ret, "error_verbatim": mv_err}
    fact("N1d move_in(#%r -> Diagram #%d at LIVE Traverse index %r, position %r) returned %r ; error VERBATIM %r"
         % (new_ct_uid, D639, d639_live, MOVE_POSITION_N, mv_ret, mv_err))
    gate("N1_m move_in returned without raising", mv_err == "", "returned %r, error %r" % (mv_ret, mv_err))
    purge_junk_invokes(K, "N1d move_in", target, inv_before)
    M["owner_after"] = owner_read(K, "N1d the ControlTerminal's owner AFTER the move", new_ct_uid, target)
    ct_a = g.count(target, "ControlTerminal")
    rows_a = panel_rows(target)
    es_a = read_exec_state(K, "N1d AFTER the move (and the junk purge)", target)
    M["control_terminal_census"] = {"before": ct_b, "after": ct_a}
    M["panel_row_count"] = {"before": len(rows_b), "after": len(rows_a)}
    M["exec_state"] = {"before": es_b, "after": es_a}
    fact("N1d panel rows %r -> %r ; the target indicator's row now: %r"
         % (len(rows_b), len(rows_a), next((r for r in rows_a if r.get("label") == label), None)))
    gate("N1_c2 the ControlTerminal census is unchanged across the move", ct_b == ct_a, "%r -> %r" % (ct_b, ct_a))
    owner_ok = (M["owner_after"].get("owner_class"), M["owner_after"].get("owner_uid")) == ("Diagram", D639)
    R["pass_criteria"]["N1"] = {"owner_of": (M["owner_after"].get("owner_class"),
                                             M["owner_after"].get("owner_uid")), "exec_state": es_a}
    gate("N1_PASS *** THE N1 PASS CRITERION: owner_of == ('Diagram',639) AND ExecState == 1 ***",
         owner_ok and es_a == 1,
         "owner (%r, %r) -> (%r, %r), ExecState %r -> %r"
         % (M["owner_before"].get("owner_class"), M["owner_before"].get("owner_uid"),
            M["owner_after"].get("owner_class"), M["owner_after"].get("owner_uid"), es_b, es_a))
    census(K, "N1 after the move", target)
    dump()

    print("\n--------- N1 SAVE  (the last point the VI is measured legal, 47(e))", flush=True)
    size = save_if_legal(K, "N1", target, "NUMERIC indicator created and moved onto Diagram #639, UNWIRED", "N1")
    if not isinstance(size, int):
        raise Stop("N1: ExecState was %r at the save point, so nothing was saved and the run STOPS here (no "
                   "improvised repair)." % (K.get("exec_state_before_save"),))


# ============================================================================== SUB-STEP N2
def step_n2():
    """restart -> reopen the N1 file COLD -> wire to #10757 t 'element' -> SAVE -> ordered pass -> Is Broken?"""
    K = R["N2"]
    cold_start(K, "N2", N1_PATH, N2_PATH,
               "LEG N, second half: wire the NUMERIC indicator to #%d t %r (wire %r)"
               % (NUM_SRC_UID, NUM_TERM_NAME, NUM_WIRE_PIN))
    with D.Preload("N2"):
        g.open_panel(N2_PATH)
        time.sleep(1.0)
        try:
            _n2_body(K, N2_PATH)
        finally:
            close_quietly(N2_PATH)
    dump()
    return isinstance(K.get("saved_bytes"), int)


def _n2_body(K, target):
    new_ct_uid = R["N1"].get("new_ct_uid")
    label = R["N1"].get("label")
    es_cold = read_exec_state(K, "N2 COLD reopen of the N1 file (fresh instance)", target)
    K["cold_exec_state"] = es_cold
    gate("N2_C the COLD reopen of the N1 file reads ExecState 1", es_cold == 1, "%r" % (es_cold,))
    K["owner_of_new_ct_cold"] = owner_read(K, "N2 the moved ControlTerminal's owner on the COLD open",
                                           new_ct_uid, target)
    census(K, "N2 on the cold reopen", target)
    wire_leg(K, "N2", target, NUM_SRC_UID, NUM_NODES_PIN,
             lambda rows: next((t for t in rows if t["name"] == NUM_TERM_NAME), None), label, NUM_WIRE_PIN)
    if not isinstance(K.get("saved_bytes"), int):
        raise Stop("N2: ExecState was %r at the save point, so nothing was saved and the run STOPS here."
                   % (K.get("exec_state_before_save"),))


# ============================================================================== SUB-STEP B1
def step_b1():
    """restart -> reopen the N2 file COLD -> place C2 -> create_indicator on its Boolean SOURCE -> delete the
    created wire BY UID -> delete the carrier -> ExecState -> SAVE."""
    K = R["B1"]
    cold_start(K, "B1", N2_PATH, B1_PATH,
               "LEG B, first half: carrier of record %s %s" % (CARRIER["cid"], CARRIER["what"]))
    with D.Preload("B1"):
        g.open_panel(B1_PATH)
        time.sleep(1.0)
        try:
            _b1_body(K, B1_PATH)
        finally:
            close_quietly(B1_PATH)
    dump()
    return isinstance(K.get("saved_bytes"), int)


def _b1_body(K, target):
    es_cold = read_exec_state(K, "B1 COLD reopen of the N2 file (fresh instance)", target)
    K["cold_exec_state"] = es_cold
    gate("B1_C the COLD reopen of the N2 file reads ExecState 1", es_cold == 1, "%r" % (es_cold,))
    base = census(K, "B1 on the cold reopen", target)
    dd = resolve_diagrams(K, "B1", target)
    d639, d536 = dd[D639], dd[D536]
    if not isinstance(d536, int):
        raise Stop("B1: diag_index(#536) did not resolve (%r)." % (d536,))

    A = K.setdefault("A", {})
    A["owner_of_10686"] = owner_read(K, "B1 owner of the BOOLEAN sink #%d" % BOOL_SRC_UID, BOOL_SRC_UID, target)
    gate("B1_A3 owner_of(#%d) answers ('Diagram', 639)" % BOOL_SRC_UID,
         (A["owner_of_10686"].get("owner_class"), A["owner_of_10686"].get("owner_uid")) == ("Diagram", D639),
         "(%r, %r)" % (A["owner_of_10686"].get("owner_class"), A["owner_of_10686"].get("owner_uid")))

    print("\n--------- B1a  (place C2 at the `VI -> Block Diagram` head)", flush=True)
    B = K.setdefault("place", {})
    rows_before = panel_rows(target)
    fpl_before = fp_label_list(target)
    ct_before = g.count(target, "ControlTerminal")
    B["panel_rows_before"] = len(rows_before)
    B["control_terminal_before"] = ct_before
    es_base = read_exec_state(K, "B1 BASELINE, before any mutation", target)
    B["exec_state_baseline"] = es_base
    B["wire_count_baseline"] = base.get("Wire")
    wires_base = wire_uid_set(K, "B1 BASELINE", target)
    fact("B1a BEFORE: panel_wiring rows %r, fp_labels %r, ControlTerminal census %r, Wire count %r"
         % (len(rows_before), len(fpl_before), ct_before, B["wire_count_baseline"]))

    try:
        top0 = g.node_info(target, max_n=40)
        B["node_info_before_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        top0 = None
        B["node_info_before_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    B["node_info_before"] = top0
    fact("B1a node_info(max_n=40) BEFORE: %r entries -> %r ; error VERBATIM %r"
         % (len(top0) if isinstance(top0, list) else top0, top0, B["node_info_before_error_verbatim"]))

    node_cls = CARRIER["node_class"]
    new_node, pl_err = None, None
    try:
        new_node = g.build_property(target, CARRIER["cls"], CARRIER["props"], NODE_LOCATION,
                                    diagram_index=d536)
        pl_err = ""
    except Exception as e:                                                         # noqa: BLE001
        pl_err = "%s: %s" % (type(e).__name__, str(e)[:600])
    B["call"] = ("build_property(target, %r, %r, %r, diagram_index=%r)"
                 % (CARRIER["cls"], CARRIER["props"], NODE_LOCATION, d536))
    B["new"] = new_node
    B["error_verbatim"] = pl_err
    fact("B1a %s -> new %r ; error VERBATIM %r" % (B["call"], new_node, pl_err))
    node_uid = (new_node[0]["uid"] if isinstance(new_node, list) and new_node else None)
    node_owner = owner_read(K, "B1a the new carrier's owner", node_uid, target) if node_uid else {}
    B["carrier_uid"] = node_uid
    B["carrier_owner"] = node_owner
    gate("B1_a build_property put 1 new %s on the target, owner ('TopLevelDiagram', 536)" % node_cls,
         isinstance(new_node, list) and len(new_node) == 1
         and (node_owner.get("owner_class"), node_owner.get("owner_uid")) == ("TopLevelDiagram", D536),
         "new %r, owner (%r, %r), error %r"
         % (new_node, node_owner.get("owner_class"), node_owner.get("owner_uid"), pl_err))
    if node_uid is None:
        raise Stop("B1: the builder placed no node (error VERBATIM %r)." % (pl_err,))

    try:
        top1 = g.node_info(target, max_n=40)
        B["node_info_after_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        top1 = None
        B["node_info_after_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    B["node_info_after"] = top1
    n0 = len(top0) if isinstance(top0, list) else None
    n1 = len(top1) if isinstance(top1, list) else None
    fact("B1a node_info(max_n=40) AFTER: %r entries -> %r ; error VERBATIM %r"
         % (n1, top1, B["node_info_after_error_verbatim"]))
    gate("B1_a2 node_info gained exactly ONE entry", n0 is not None and n1 is not None and n1 == n0 + 1,
         "%r -> %r" % (n0, n1))
    node_i = (top1[-1][0] if isinstance(top1, list) and top1 else None)
    B["node_index"] = node_i

    tt, tt_err = [], ""
    if node_i is not None:
        try:
            u_echo, rows_t = g.node_terms_uid(target, d536, node_i)
            B["node_uid_echo"] = u_echo
            tt = [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]), "wire": r["wire"]}
                  for r in rows_t]
        except Exception as e:                                                     # noqa: BLE001
            tt_err = "%s: %s" % (type(e).__name__, str(e)[:300])
    B["terminal_table"] = tt
    B["terminal_table_error_verbatim"] = tt_err
    fact("B1a THE CARRIER'S FULL TERMINAL TABLE [(index, label, is_source, wire)], READ OFF THE MACHINE: %r "
         "(uid echo %r; error VERBATIM %r)" % (tt, B.get("node_uid_echo"), tt_err))
    B["exec_state_after_place"] = read_exec_state(K, "B1a after build_property placed the carrier", target)
    B["wire_count_after_place"] = g.count(target, "Wire")
    bool_row, how = pick_value_source(tt)
    B["chosen_terminal"] = bool_row
    B["chosen_rule"] = how
    fact("B1a the terminal create_indicator will be called on: %r (utf-8 hex %r)  (rule: %s; the recorded "
         "reading is %r)" % (bool_row, (bool_row or {}).get("name", "").encode("utf-8").hex(), how,
                             CARRIER["expected_carrier_terminal"]))
    gate("B1_a3 the terminal table holds a SOURCE terminal that is not reference out / error out",
         bool(bool_row), "%r (%s)" % (bool_row, how))
    if bool_row is None:
        raise Stop("B1: the carrier exposes no value-carrying SOURCE terminal (%s)." % how)

    print("\n--------- B1b  (create_indicator on that SOURCE terminal; 6349C02 takes NO type argument, 47(d))",
          flush=True)
    C = K.setdefault("create", {})
    new_ct, ci_err = None, None
    try:
        new_ct = g.create_indicator(target, node_i, bool_row["i"])
        ci_err = ""
    except Exception as e:                                                         # noqa: BLE001
        ci_err = "%s: %s" % (type(e).__name__, str(e)[:600])
    ct_after = g.count(target, "ControlTerminal")
    new_ct_uid = (new_ct[0].get("uid") if isinstance(new_ct, list) and new_ct else None)
    C.update({"node_index": node_i, "terminal_index": bool_row["i"], "terminal_name": bool_row["name"],
              "new": new_ct, "new_ct_uid": new_ct_uid, "error_verbatim": ci_err,
              "control_terminal_before": ct_before, "control_terminal_after": ct_after})
    fact("B1b create_indicator(Nodes[%r].Terminals[%r] = %r) -> new %r ; error VERBATIM %r"
         % (node_i, bool_row["i"], bool_row["name"], new_ct, ci_err))
    gate("B1_b create_indicator returned a ControlTerminal and the census went %r -> %r" % (ct_before, ct_after),
         isinstance(new_ct_uid, int) and isinstance(ct_before, int) and ct_after == ct_before + 1,
         "new uid %r, census %r -> %r, error %r" % (new_ct_uid, ct_before, ct_after, ci_err))
    if not isinstance(new_ct_uid, int):
        raise Stop("B1: create_indicator returned no ControlTerminal uid (error VERBATIM %r)." % (ci_err,))
    C["exec_state_after_create"] = read_exec_state(K, "B1b after create_indicator", target)
    C["wire_count_after_create"] = g.count(target, "Wire")
    wires_created = wire_uid_set(K, "B1b after create_indicator", target)
    added = sorted(wires_created - wires_base)
    C["wire_uids_added_by_create_indicator"] = added
    fact("B1b whole-VI Wire count %r -> %r -> %r ; the wire uid(s) create_indicator ADDED: %r  (48(b): on a "
         "SOURCE terminal the indicator is born WIRED to the carrier)"
         % (B["wire_count_baseline"], B["wire_count_after_place"], C["wire_count_after_create"], added))
    gate("B1_b3 create_indicator added EXACTLY ONE whole-VI Wire object", len(added) == 1,
         "added %r (count %r -> %r)" % (added, B["wire_count_after_place"], C["wire_count_after_create"]))

    label, lrec, new_rows, new_fp = read_new_label(K, "B1b", target, rows_before, fpl_before)
    C["label_record"] = lrec
    fact("B1b equals the recorded machine-read %r: %r"
         % (CARRIER["expected_indicator_label"], label == CARRIER["expected_indicator_label"]))
    gate("B1_b2 exactly ONE new front-panel row appeared and its label was READ off the machine",
         (len(new_rows) == 1 or (not new_rows and len(new_fp) == 1)) and label is not None,
         "%r new panel row(s), %r new fp_labels entr(y/ies), label %r" % (len(new_rows), len(new_fp), label))
    if label is None:
        raise Stop("B1: the indicator's label could not be READ off the machine, and a label is never retyped.")
    gate("B1_b4 the label carries no newline and duplicates no existing panel label (the NUMERIC one included)",
         lrec.get("contains_newline") is False
         and lrec.get("is_duplicate_of_an_existing_panel_label") is False,
         "newline %r, duplicate %r, label %r ; the numeric leg's label is %r"
         % (lrec.get("contains_newline"), lrec.get("is_duplicate_of_an_existing_panel_label"), label,
            R["N1"].get("label")))
    K["new_ct_uid"] = new_ct_uid
    K["label"] = label
    R["boolean_indicator"] = {"uid": new_ct_uid, "label": label, "label_utf8_hex": lrec.get("label_utf8_hex")}
    dump()

    print("\n--------- B1c  (DELETE THE CREATED WIRE BY UID - 48(b)+48(d); remove_bad_wires_scripted is REFUSED)",
          flush=True)
    W = K.setdefault("wire_delete", {})
    W["refused_verb"] = R["remove_bad_wires_scripted"]
    fact("B1c %s" % W["refused_verb"])
    ct_pre_wd = g.count(target, "ControlTerminal")
    if len(added) != 1:
        W["not_attempted_because"] = ("create_indicator added %r wire uid(s), not exactly 1, so there is no "
                                      "single uid to address narrowly." % (added,))
        fact("B1c NOT ATTEMPTED: %s" % W["not_attempted_because"])
        raise Stop("B1: %s" % W["not_attempted_because"])
    created_wire = added[0]
    W["created_wire_uid"] = created_wire
    rd = delete_by_uid(K, "B1c the created wire", target, "Wire", created_wire)
    W["delete"] = rd
    gate("B1_c delete_object removed exactly 1 Wire",
         isinstance(rd.get("gone"), list) and len(rd["gone"]) == 1,
         "gone %r ; error %r" % (rd.get("gone"), rd.get("error_verbatim")))
    wires_after_wd = wire_uid_set(K, "B1c after the wire delete", target)
    W["wire_count_after_delete"] = g.count(target, "Wire")
    went = sorted(wires_created - wires_after_wd)
    W["uids_that_disappeared"] = went
    W["pre_existing_uids_that_disappeared"] = sorted(wires_base - wires_after_wd)
    ct_post_wd = g.count(target, "ControlTerminal")
    W["control_terminal_census"] = {"before": ct_pre_wd, "after": ct_post_wd}
    W["exec_state_after_wire_delete"] = read_exec_state(K, "B1c after the wire delete", target)
    fact("B1c the uid SET that disappeared: %r (the wire create_indicator added was %r); PRE-EXISTING wire uids "
         "that disappeared: %r ; whole-VI Wire count %r -> %r ; ControlTerminal %r -> %r"
         % (went, created_wire, W["pre_existing_uids_that_disappeared"], C["wire_count_after_create"],
            W["wire_count_after_delete"], ct_pre_wd, ct_post_wd))
    gate("B1_c2 the set that disappeared IS EXACTLY the wire create_indicator added", went == [created_wire],
         "%r vs %r" % (went, [created_wire]))
    gate("B1_c3 NO pre-existing wire uid disappeared (rule-1a narrowness)",
         W["pre_existing_uids_that_disappeared"] == [], "%r" % (W["pre_existing_uids_that_disappeared"],))
    gate("B1_c4 the ControlTerminal census is unchanged across the wire delete", ct_pre_wd == ct_post_wd,
         "%r -> %r" % (ct_pre_wd, ct_post_wd))
    dump()

    print("\n--------- B1d  (delete the carrier node, AFTER the wire)", flush=True)
    Dd = K.setdefault("carrier_delete", {})
    rd2 = delete_by_uid(K, "B1d the carrier", target, node_cls, node_uid)
    Dd["delete"] = rd2
    gate("B1_d delete_object removed exactly 1 %s (the carrier)" % node_cls,
         isinstance(rd2.get("gone"), list) and len(rd2["gone"]) == 1,
         "gone %r ; error %r" % (rd2.get("gone"), rd2.get("error_verbatim")))
    Dd["wire_count_after_carrier_delete"] = g.count(target, "Wire")
    wires_final = wire_uid_set(K, "B1d after the carrier delete", target)
    Dd["pre_existing_uids_that_disappeared_overall"] = sorted(wires_base - wires_final)
    es_final = read_exec_state(K, "B1d after the carrier delete", target)
    Dd["exec_state_after_carrier_delete"] = es_final
    try:
        Dd["node_info_after"] = g.node_info(target, max_n=40)
    except Exception as e:                                                         # noqa: BLE001
        Dd["node_info_after"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
    fact("B1d whole-VI Wire count %r -> %r ; node_info(max_n=40) now %r ; wire uids lost versus the B1 BASELINE "
         "over the whole of B1: %r"
         % (W["wire_count_after_delete"], Dd["wire_count_after_carrier_delete"], Dd["node_info_after"],
            Dd["pre_existing_uids_that_disappeared_overall"]))
    fact("B1 ExecState TIMELINE: %r (baseline) -> %r (after build_property) -> %r (after create_indicator) -> "
         "%r (after the WIRE delete) -> %r (after the CARRIER delete)"
         % (es_base, B["exec_state_after_place"], C["exec_state_after_create"],
            W["exec_state_after_wire_delete"], es_final))
    census(K, "B1 after both deletes", target)
    R["pass_criteria"]["B1"] = es_final
    gate("B1_PASS *** THE B1 PASS CRITERION: ExecState == 1 after both deletes ***", es_final == 1,
         "ExecState %r" % (es_final,))
    dump()

    print("\n--------- B1 SAVE  (only at ExecState 1; allow_broken False, gui_save never called)", flush=True)
    size = save_if_legal(K, "B1", target,
                         "BOOLEAN carrier placed, indicator created, created wire + carrier deleted", "B1")
    if not isinstance(size, int):
        raise Stop("B1: ExecState was %r at the save point, so nothing was saved and the run STOPS here (no "
                   "improvised repair - 48(e))." % (es_final,))


# ============================================================================== SUB-STEP B2
def step_b2():
    """restart -> reopen the B1 file COLD -> move_in(CT -> Diagram #639) -> purge the junk Invoke -> SAVE.
    47(e)'s save point for the BOOLEAN leg: it comes BEFORE any wiring."""
    K = R["B2"]
    cold_start(K, "B2", B1_PATH, B2_PATH,
               "47(e): THIS is the BOOLEAN leg's save point - it comes BEFORE any wiring")
    with D.Preload("B2"):
        g.open_panel(B2_PATH)
        time.sleep(1.0)
        try:
            _b2_body(K, B2_PATH)
        finally:
            close_quietly(B2_PATH)
    dump()
    return isinstance(K.get("saved_bytes"), int)


def _b2_body(K, target):
    new_ct_uid = R["B1"].get("new_ct_uid")
    label = R["B1"].get("label")
    es_cold = read_exec_state(K, "B2 COLD reopen of the B1 file (fresh instance)", target)
    K["cold_exec_state"] = es_cold
    gate("B2_C the COLD reopen of the B1 file reads ExecState 1", es_cold == 1, "%r" % (es_cold,))
    census(K, "B2 on the cold reopen", target)
    dd = resolve_diagrams(K, "B2", target, uids=(D639, D686))
    d639 = dd[D639]

    K["owner_before"] = owner_read(K, "B2 the ControlTerminal's owner BEFORE the move", new_ct_uid, target)
    rows_b = panel_rows(target)
    row_b = next((r for r in rows_b if r.get("label") == label), None)
    K["target_row_before_move"] = row_b
    fact("B2 the indicator row re-read on this file: %r (label VERBATIM %r, utf-8 hex %r)"
         % (row_b, label, (label or "").encode("utf-8").hex()))
    ct_b = g.count(target, "ControlTerminal")
    es_b = read_exec_state(K, "B2 BEFORE the move", target)
    try:
        inv_before = set(g.uids(target, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_before = set()
        fact("B2 uids(Invoke) BEFORE raised %s: %s" % (type(e).__name__, str(e)[:140]))

    mv_ret, mv_err = None, None
    if not isinstance(d639, int):
        mv_err = "NOT ATTEMPTED: diag_index(#639) did not resolve (%r)." % (d639,)
    else:
        try:
            mv_ret = move_in(target, new_ct_uid, d639, MOVE_POSITION_B)
            mv_err = ""
        except Exception as e:                                                     # noqa: BLE001
            mv_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    K["move_in"] = {"call": "move_in(target, %r, %r, %r)" % (new_ct_uid, d639, MOVE_POSITION_B),
                    "returned": mv_ret, "error_verbatim": mv_err,
                    "position_note": "offset from the NUMERIC indicator's %r so the two do not overlap - "
                                     "COSMETIC ONLY, never functional" % (MOVE_POSITION_N,)}
    fact("B2 move_in(#%r -> Diagram #%d at LIVE Traverse index %r, position %r) returned %r ; error VERBATIM %r"
         % (new_ct_uid, D639, d639, MOVE_POSITION_B, mv_ret, mv_err))
    gate("B2_m move_in returned without raising", mv_err == "", "returned %r, error %r" % (mv_ret, mv_err))
    purge_junk_invokes(K, "B2 move_in", target, inv_before)

    K["owner_after"] = owner_read(K, "B2 the ControlTerminal's owner AFTER the move", new_ct_uid, target)
    ct_a = g.count(target, "ControlTerminal")
    rows_a = panel_rows(target)
    es_a = read_exec_state(K, "B2 AFTER the move (and the junk purge)", target)
    K["control_terminal_census"] = {"before": ct_b, "after": ct_a}
    K["panel_row_count"] = {"before": len(rows_b), "after": len(rows_a)}
    K["exec_state"] = {"before": es_b, "after": es_a}
    fact("B2 panel rows %r -> %r ; the target indicator's row now: %r"
         % (len(rows_b), len(rows_a), next((r for r in rows_a if r.get("label") == label), None)))
    gate("B2_c the ControlTerminal census is unchanged across the move", ct_b == ct_a, "%r -> %r" % (ct_b, ct_a))
    owner_ok = (K["owner_after"].get("owner_class"), K["owner_after"].get("owner_uid")) == ("Diagram", D639)
    R["pass_criteria"]["B2"] = {"owner_of": (K["owner_after"].get("owner_class"),
                                             K["owner_after"].get("owner_uid")), "exec_state": es_a}
    gate("B2_PASS *** THE B2 PASS CRITERION: owner_of == ('Diagram',639) AND ExecState == 1 ***",
         owner_ok and es_a == 1,
         "owner (%r, %r) -> (%r, %r), ExecState %r -> %r"
         % (K["owner_before"].get("owner_class"), K["owner_before"].get("owner_uid"),
            K["owner_after"].get("owner_class"), K["owner_after"].get("owner_uid"), es_b, es_a))
    census(K, "B2 after the move", target)
    dump()

    print("\n--------- B2 SAVE  (47(e)'s save point - BEFORE any wiring)", flush=True)
    size = save_if_legal(K, "B2", target, "BOOLEAN indicator moved onto Diagram #639, UNWIRED (47(e))", "B2")
    if not isinstance(size, int):
        raise Stop("B2: ExecState was %r at the save point, so nothing was saved and the run STOPS here." % es_a)


# ============================================================================== SUB-STEP B3
def step_b3():
    """restart -> reopen the B2 file COLD, AS THE DELIVERABLE'S OWN PATH -> wire to #10686 t0 -> SAVE ->
    ordered pass -> Is Broken?"""
    K = R["B3"]
    cold_start(K, "B3", B2_PATH, FINAL_PATH,
               "THE DELIVERABLE'S OWN PATH: %s (gscript has no save-as, :2062)" % os.path.basename(FINAL_PATH))
    with D.Preload("B3"):
        g.open_panel(FINAL_PATH)
        time.sleep(1.0)
        try:
            _b3_body(K, FINAL_PATH)
        finally:
            close_quietly(FINAL_PATH)
    dump()
    return isinstance(K.get("saved_bytes"), int)


def _b3_body(K, target):
    new_ct_uid = R["B1"].get("new_ct_uid")
    label = R["B1"].get("label")
    es_cold = read_exec_state(K, "B3 COLD reopen of the B2 file (fresh instance)", target)
    K["cold_exec_state"] = es_cold
    gate("B3_C the COLD reopen of the B2 file reads ExecState 1", es_cold == 1, "%r" % (es_cold,))
    K["owner_of_new_ct_cold"] = owner_read(K, "B3 the moved ControlTerminal's owner on the COLD open",
                                           new_ct_uid, target)
    census(K, "B3 on the cold reopen", target)
    wire_leg(K, "B3", target, BOOL_SRC_UID, BOOL_NODES_PIN,
             lambda rows: next((t for t in rows if t["i"] == BOOL_TERM_INDEX), None), label, BOOL_WIRE_PIN)


# ============================================================================== Z0: the COLD read of the file
def step_z0():
    """restart -> reopen the DELIVERABLE COLD, READ ONLY. No mutation, no save, no ordered pass."""
    K = R["Z0"]
    print("\n===================================================================", flush=True)
    print("=== Z0   the DELIVERABLE, reopened COLD in a freshly restarted LabVIEW - READ ONLY", flush=True)
    print("===================================================================", flush=True)
    K["handles_before_restart"] = labview_handles()
    D.fresh("Z0 RESTART (so the deliverable loads COLD, from disk, with nothing preloaded)")
    K["handles_after_restart"] = labview_handles()
    fact("Z0 LabVIEW handles across the restart: %r -> %r"
         % (K["handles_before_restart"], K["handles_after_restart"]))
    K["path"] = FINAL_PATH
    K["file"] = D.file_facts("Z0 the deliverable on disk", FINAL_PATH)
    with D.Preload("Z0"):
        g.open_panel(FINAL_PATH)
        time.sleep(1.0)
        try:
            es = read_exec_state(K, "Z0 COLD reopen of the DELIVERABLE (fresh instance)", FINAL_PATH)
            K["cold_exec_state"] = es
            R["pass_criteria"]["Z0"] = es
            gate("Z0_a the DELIVERABLE reopens COLD, in a freshly restarted LabVIEW, at ExecState 1", es == 1,
                 "%r" % (es,))
            c = census(K, "Z0 on the cold reopen of the deliverable", FINAL_PATH)
            num = R.get("numeric_indicator") or {}
            boo = R.get("boolean_indicator") or {}
            K["owner_numeric"] = owner_read(K, "Z0 the NUMERIC indicator's owner", num.get("uid"), FINAL_PATH) \
                if num.get("uid") else {}
            K["owner_boolean"] = owner_read(K, "Z0 the BOOLEAN indicator's owner", boo.get("uid"), FINAL_PATH) \
                if boo.get("uid") else {}
            gate("Z0_b owner_of(the NUMERIC ControlTerminal #%r) == ('Diagram', 639)" % num.get("uid"),
                 (K["owner_numeric"].get("owner_class"), K["owner_numeric"].get("owner_uid"))
                 == ("Diagram", D639),
                 "(%r, %r)" % (K["owner_numeric"].get("owner_class"), K["owner_numeric"].get("owner_uid")))
            gate("Z0_c owner_of(the BOOLEAN ControlTerminal #%r) == ('Diagram', 639)" % boo.get("uid"),
                 (K["owner_boolean"].get("owner_class"), K["owner_boolean"].get("owner_uid"))
                 == ("Diagram", D639),
                 "(%r, %r)" % (K["owner_boolean"].get("owner_class"), K["owner_boolean"].get("owner_uid")))
            ct = c.get("ControlTerminal")
            K["control_terminal_census"] = ct
            gate("Z0_d the ControlTerminal census on the deliverable is %d (%r at the S2 baseline, +1 per leg)"
                 % (CT_FINAL_EXPECT, R.get("control_terminal_baseline")),
                 ct == CT_FINAL_EXPECT, "%r (baseline %r)" % (ct, R.get("control_terminal_baseline")))
            rows = panel_rows(FINAL_PATH)
            K["panel_rows_for_both_indicators"] = [r for r in rows
                                                   if r.get("label") in (num.get("label"), boo.get("label"))]
            fact("Z0 the two indicator rows READ off the deliverable: %r"
                 % (K["panel_rows_for_both_indicators"],))
        finally:
            close_quietly(FINAL_PATH)
    dump()


# ======================================================================================== MAIN
def main():
    print("=== stage_d1_s3a_focus_ind  %s   (D1 STAGE S3a: ONE file carrying BOTH indicators; both legs are "
          "REPLAYS; NO VI IS RUN, 34(f); no new op, no new device, no GUI action; CHOOSES AND RECOMMENDS "
          "NOTHING)" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    fact("DELIVERABLE: %s" % FINAL_PATH)
    fact("LEG N (numeric) replays %s" % R["both_legs_are_replays"]["numeric"])
    fact("LEG B (boolean) replays %s" % R["both_legs_are_replays"]["boolean"])
    fact("WHAT IS NEW: %s" % R["both_legs_are_replays"]["what_is_new_here"])
    fact("REFUSED: %s" % R["remove_bad_wires_scripted"])
    fact("CARRIER OF RECORD: %s %s(%r, %r) - %s"
         % (CARRIER["cid"], CARRIER["verb"], CARRIER["cls"], CARRIER["props"], CARRIER["citation"]))

    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (fresh baseline ~31,500): %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    # ---- the mechanical pre-batch restart (44(e))
    D.fresh("T2b RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    order = [("N1", step_n1, N1_PATH, None),
             ("N2", step_n2, N2_PATH, "N1"),
             ("B1", step_b1, B1_PATH, "N2"),
             ("B2", step_b2, B2_PATH, "B1"),
             ("B3", step_b3, FINAL_PATH, "B2")]
    ok = True
    for step, fn, path, parent in order:
        if not ok:
            R[step]["not_attempted"] = ("the previous sub-step did not reach its pass criterion / did not "
                                        "save, and every sub-step starts FROM THE PREVIOUS FILE.")
            fact("%s NOT ATTEMPTED: %s" % (step, R[step]["not_attempted"]))
            continue
        try:
            ok = bool(fn())
        except Stop as s:
            R[step]["stopped_at"] = str(s)
            fact("%s STOPPED: %s" % (step, s))
            ok = False
        except Exception as e:                                                     # noqa: BLE001
            R[step]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            fact("%s raised %s: %s" % (step, type(e).__name__, str(e)[:600]))
            ok = False
        if not isinstance(R[step].get("saved_bytes"), int) and os.path.exists(path):
            try:
                os.remove(path)
                fact("%s cleanup: the UNSAVED working file %s was removed (a byte-identical duplicate of its "
                     "parent, nothing of its own). NOTHING SAVED IS EVER DELETED." % (step, os.path.basename(path)))
            except Exception as e:                                                 # noqa: BLE001
                fact("%s cleanup: removing %s FAILED %s: %s"
                     % (step, os.path.basename(path), type(e).__name__, str(e)[:200]))
        dump()

    if ok:
        try:
            step_z0()
        except Stop as s:
            R["Z0"]["stopped_at"] = str(s)
            fact("Z0 STOPPED: %s" % s)
        except Exception as e:                                                     # noqa: BLE001
            R["Z0"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            fact("Z0 raised %s: %s" % (type(e).__name__, str(e)[:600]))
    else:
        R["Z0"]["not_attempted"] = "B3 did not save the deliverable, so there is no file to reopen cold."
        fact("Z0 NOT ATTEMPTED: %s" % R["Z0"]["not_attempted"])
    dump()

    # ---- Z: the closing facts
    print("\n--- Z: the closing facts", flush=True)
    R["ref_counts"] = g.ref_counts()
    fact("refs %r" % (R["ref_counts"],))
    try:
        g.reset()
    except Exception as e:                                                         # noqa: BLE001
        fact("g.reset raised %s: %s" % (type(e).__name__, e))
    R["handles"]["after"] = labview_handles()
    fact("LabVIEW handles AFTER everything: %r" % R["handles"]["after"])

    zo = probe("Z1 ORIGINAL after everything", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after everything", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after everything", S2_ARTEFACT)
    gate("Z1 ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 all unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5,
         "%s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z2 refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))

    print("\n--- THE ANSWER TABLE (readings, not a recommendation)", flush=True)
    fact("N1  owner_of/ExecState = %r ; saved %r bytes -> %r"
         % (R["pass_criteria"]["N1"], R["N1"].get("saved_bytes"), R["N1"].get("file_after", {}).get("md5")))
    fact("N2  Is Broken? = %r ; indicator wire %r -> %r ; saved %r bytes -> %r"
         % (R["pass_criteria"]["N2"], R["N2"].get("target_wire_uid", {}).get("before"),
            R["N2"].get("target_wire_uid", {}).get("after"), R["N2"].get("saved_bytes"),
            R["N2"].get("file_after", {}).get("md5")))
    fact("B1  ExecState after both deletes = %r ; created wire %r deleted by uid -> gone %r ; saved %r -> %r"
         % (R["pass_criteria"]["B1"], R["B1"].get("wire_delete", {}).get("created_wire_uid"),
            R["B1"].get("wire_delete", {}).get("delete", {}).get("gone"), R["B1"].get("saved_bytes"),
            R["B1"].get("file_after", {}).get("md5")))
    fact("B2  owner_of/ExecState = %r ; saved %r bytes -> %r"
         % (R["pass_criteria"]["B2"], R["B2"].get("saved_bytes"), R["B2"].get("file_after", {}).get("md5")))
    fact("B3  Is Broken? = %r ; indicator wire %r -> %r ; saved %r bytes -> %r"
         % (R["pass_criteria"]["B3"], R["B3"].get("target_wire_uid", {}).get("before"),
            R["B3"].get("target_wire_uid", {}).get("after"), R["B3"].get("saved_bytes"),
            R["B3"].get("file_after", {}).get("md5")))
    fact("Z0  the DELIVERABLE cold ExecState = %r ; ControlTerminal census %r ; numeric indicator %r ; boolean "
         "indicator %r"
         % (R["pass_criteria"]["Z0"], R["Z0"].get("control_terminal_census"), R.get("numeric_indicator"),
            R.get("boolean_indicator")))
    fact("ARTEFACTS ON DISK: %r" % ([{"step": a["step"], "path": a["path"],
                                      "md5": a.get("file", {}).get("md5"),
                                      "size": a.get("file", {}).get("size"),
                                      "version": a.get("file", {}).get("version_candidates")}
                                     for a in R["artefacts"] if a.get("saved")],))

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as s:
        fact("FATAL: %s" % s)
        dump()
        print("\n=== GATES %d pass / %d fail (FATAL stop)" % (len(passes), len(fails)), flush=True)
        sys.exit(1)
