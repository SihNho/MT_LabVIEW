"""diag_s58_boolwire - cycle 58 material #2. Executes Pre-decided 48(e)'s THREE-SUB-STEP DECOMPOSITION of
S3a's BOOLEAN half. A DIAGNOSTIC under tools/bench/, never a recipe: nothing under tools/recipes/ is created
or launched, and the on-disk absence of the stop-recorded S3a recipe is asserted at both ends (gate Z3).

WHAT THIS BUILDS (48(e), written from cycle 58 material #1's own numbers):
  a Boolean-typed front-panel indicator living on Diagram #639, wired to #10686 t0 'x .and. y?' (wire 10799).
  The NUMERIC half is already delivered: claudeDev\\D1_s3a_num_ind_20260920_234341.vi, md5 fceaa0a1...

THE ONE VERB CALL THAT CHANGES VERSUS DISPATCH 1 (48(b) + 48(d)):
  dispatch 1 measured that `create_indicator` on a SOURCE terminal creates a REAL Wire object (whole-VI Wire
  1905 -> 1906; uid 23586 on C1, 23576 on C2), that this wire is STILL ALIVE after delete_object(carrier), and
  that ExecState is therefore 0 at the save point. That wire is OURS and its uid is held, so it is deleted BY
  UID, BEFORE the carrier.
  THE SIGNATURE USED, read off tools/gscript.py:2240:
      delete_object(target, cls, index, verify=True)
  It addresses an object by (Traverse CLASS, Traverse INDEX) - there is no by-uid form in the fleet. `Wire` IS a
  live Traverse class (the 1905/1906 census comes from g.count/g.uids over it, which are report_all over the same
  class), so the uid is resolved to its index by
      idx = [o["uid"] for o in g.report_all(target, "Wire")].index(<the created wire uid>)
  and verify=True is kept, so the call RETURNS the uid set that disappeared and raises unless exactly one object
  went. That readback is what makes the delete narrow: gate B1f asserts the set equals {the created wire} and
  gate B1g asserts NO pre-existing wire uid disappeared.
  `remove_bad_wires_scripted` is REFUSED by 48(d) - it has a measured over-removal on this VI
  (archive/2026-09-17-status-d1-route-b-2.md:45, "DELETES THE TUNNEL"), a rule-1a hazard. It is not imported,
  not called, and neither is the GUI menu form at tools/gscript.py:1629 (this run performs no GUI action).

THE CARRIER OF RECORD (48(c)): C2 = build_property('VI Server:VI', [('242', False)]) = VI.Automatic Error
Handling, whose created indicator read back as 'Automatic Error Handling' - non-duplicate, no newline, and
ExecState 1 throughout its placement. C3 ('VI Server:Wire') is WITHDRAWN: it takes the VI to ExecState 0 at
placement, before any delete. C1 is not attempted here - 48(e) names C2.

=====================================================================================================
THREE SUB-STEPS, THREE FILES, THREE PASS CRITERIA - each starting from the PREVIOUS FILE in a FRESH LabVIEW
instance (the user's 2026-09-19 rule: a step is not done until it has left a file). Every label and every index
is re-read LIVE (34(h)); nothing is cached across a restart except the label STRING that was read off the
machine in B1 and is re-matched against a live panel row in B2/B3.

S3a-B1  from claudeDev\\D1_s2_loops.vi (md5 6ff19497...), on the dated working file
        claudeDev\\D1_s3a_boolcarrier_b1_<stamp>.vi:
   B1a  place C2 at the `VI -> Block Diagram` head (diagram_index = the LIVE diag_index(#536)); report owner_of
        (expect ('TopLevelDiagram',536)), node_info (expect 0 -> 1) and the node's FULL terminal table
        [(index,label,is_source,wire)] read off the machine.
   B1b  create_indicator on the Boolean SOURCE terminal -> the new ControlTerminal uid, the census, the created
        wire's uid (whole-VI Wire uid SET diff), and the indicator's label READ off the machine with its hex.
   B1c  delete_object THAT WIRE BY UID -> ExecState and the whole-VI Wire count.
   B1d  delete_object(carrier) -> ExecState and the whole-VI Wire count.
   PASS CRITERION: ExecState == 1. If met, SAVE. If not, DO NOT SAVE, say so, and stop - no improvised repair.

S3a-B2  restart LabVIEW, reopen the B1 file cold (as the byte copy ..._b2_<stamp>.vi, because gscript has no
        save-as verb - tools/gscript.py:2062 saves to the target's OWN path):
        report ExecState on the cold reopen and owner_of(<CT uid>) -> move_in(<CT uid> -> Diagram #639 at its
        LIVE Traverse index, (120,4000)) -> error column VERBATIM, owner_of before/after, ControlTerminal
        census, panel-row count, ExecState -> purge in-run the junk `Invoke` uid the deletes release, reporting
        its uid and error column.
   PASS CRITERION: owner_of == ('Diagram',639) AND ExecState == 1. If met, SAVE.
   *** THIS IS 47(e)'s SAVE POINT AND IT COMES BEFORE ANY WIRING - the file that must exist even if B3 fails. ***

S3a-B3  restart LabVIEW, reopen the B2 file cold (as the byte copy ..._b3_<stamp>.vi):
        wire_indicators(... -> #10686 t0 'x .and. y?', wire 10799, diagram_index = the LIVE index of the diagram
        the INDICATOR's terminal lives on, i.e. #639) - 47(b): tools/gscript.py:1787-1789 scopes the INDICATOR
        lookup, never the source. Report the error column VERBATIM, the indicator's wire uid before/after, the
        whole-VI Wire delta, #10686's wired-terminal count before/after, and #637's terminal/wired counts
        before/after (37(e): any tunnel or border object appearing is a FINDING).
        Then the ORDERED SECOND PASS (42(b)): an idempotent re-connect of an EXISTING net on the same diagram,
        then `Is Broken?` (6371004) read on the new wire uid; report wire_delta (expect 0), the op error column,
        and the True/False.
   PASS CRITERION: `Is Broken?` == False.
   ORDERING, deliberate: the SAVE happens BEFORE the ordered pass, because the `Is Broken?` read is itself
   ExecState-perturbing (docs/NAMES.md:912-918) and cycle 57 dispatch 4 lost nothing by saving first.

PREDICTION CONTRACT (every gate is the readback of a CALL; 46(g)):
  T1   the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                          (FATAL)
  T1b  claudeDev\\D1_s1_copy.vi md5 == 3e3d23cefd3a334001aa9d6156bf1aee
  T2   claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                                (FATAL)
  B1_T3   the B1 working file is byte-identical to D1_s2_loops.vi at creation
  B1_A1   diag_index(#639) resolves to an int
  B1_A2   diag_index(#536) resolves to 0
  B1_A3   owner_of(#10686) answers ('Diagram', 639)
  B1_A4   #10686 carries terminal 0, a SOURCE, whose name and wire uid are read off the machine
  B1_a    build_property put exactly 1 new Property on the target, owner ('TopLevelDiagram', 536)
  B1_a2   node_info(max_n=40) goes 0 entries -> 1 entry
  B1_a3   the terminal table holds a SOURCE terminal that is not reference out / error out
  B1_b    create_indicator returned a ControlTerminal and the census went n -> n+1
  B1_b2   exactly ONE new front-panel row appeared and its label was READ off the machine
  B1_b3   create_indicator added EXACTLY ONE whole-VI Wire object (48(b): 1905 -> 1906)
  B1_c    delete_object removed exactly 1 Wire
  B1_c2   the set that disappeared IS EXACTLY the wire create_indicator added                   (the NARROWNESS
  B1_c3   NO pre-existing wire uid disappeared                                                   gates, rule 1a)
  B1_c4   the ControlTerminal census is unchanged across the wire delete
  B1_d    delete_object removed exactly 1 Property (the carrier)
  B1_PASS ExecState == 1 after both deletes                                       *** THE B1 PASS CRITERION ***
  B1_S    g.save() returned a byte count and the file's version bytes read 26 00 80 00 (LV2026)
  B2_C    the COLD reopen of the B1 file reads ExecState 1
  B2_m    move_in returned without raising
  B2_PASS owner_of(<CT uid>) == ('Diagram',639) AND ExecState == 1                *** THE B2 PASS CRITERION ***
  B2_c    the ControlTerminal census is unchanged across the move
  B2_S    g.save() returned a byte count and the version bytes read 26 00 80 00
  B3_C    the COLD reopen of the B2 file reads ExecState 1
  B3_w    wire_indicators returned an EMPTY error column      (a RAISE is a LEGITIMATE reading, RISK (iii))
  B3_w2   the new indicator's wire uid changed from 0                                      (the EFFECT gate)
  B3_w3   #10686's wired-terminal count is unchanged across the wiring                              (37(e))
  B3_w4   #637's terminal count is unchanged - NO tunnel or border object appeared                  (37(e))
  B3_S    ExecState == 1 at the save point and g.save() returned a byte count    (a 0 is LEGITIMATE; B2 stands)
  B3_PASS the ORDERED second-pass `Is Broken?` reads False                        *** THE B3 PASS CRITERION ***
          (True is a LEGITIMATE reading - it is the type answer again, and 48(d) says that sends the NEXT cycle
           to route 2. This run neither chooses nor recommends a route.)
  Z1   ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 unchanged after everything
  Z2   refs opened == closed, 0 live
  Z3   no recipe was created under tools/recipes/ for this stage

PREDICTED RISKS, written down BEFORE the run:
  (i)   move_in leaves JUNK `Invoke` node(s) - the uid a deleted object released (measured three times:
        probe_move_ctlterm_v0.log:135; cycle 57 dispatches 3/4; cycle 58 dispatch 1). Recorded, then purged as
        tools/recipes/build_d1_routeb_v0.py:1279-1287 does; the set is `after - before`, so nothing pre-existing
        can be touched.
  (ii)  Nodes[] and Traverse indices SHIFT when an object is added to or removed from a diagram (34(h)). Every
        index is re-resolved by uid readback immediately before use, including after each cold reload.
  (iii) wire_indicators RAISES when the target reads ExecState != 1 after the connection (gscript.py:1794-1797)
        even though the connection WAS made. Captured VERBATIM; B3 continues to the save attempt and the
        ordered pass, exactly as cycle 57 dispatch 3 did.
  (iv)  deleting the created Wire may not be enough: the carrier's own terminal, or the indicator's, may be left
        in a state LabVIEW still calls broken. B1_PASS reads ExecState rather than assuming, and a 0 there stops
        the run with NO repair attempted (48(d) reserves that judgement).
  (v)   deleting a Wire could, in principle, take a ControlTerminal or a tunnel with it. B1_c2/B1_c3/B1_c4 are
        the narrowness readbacks that would catch it; a failure there is a FINDING, not something to work round.

BOUNDS: NO VI IS RUN (34(f)). NO NEW OP VI (47(i) route 2 is the next cycle's act, not this run's). No new
process device (user, 2026-09-18 08:53). NO RECIPE. No GUI action. No motor / ASI / camera (rig 조립 /
ASSEMBLED). Originals are never opened for write; `allow_broken` stays False and `gui_save` is NEVER called.
NOTHING SAVED IS EVER DELETED. NO ROUTE IS CHOSEN OR RECOMMENDED - that is judgement's call.

WHAT ALREADY EXISTED (checked before a line of this was written, per the material brief and 47(g)):
  * tools/gscript.py - delete_object :2240 (the signature above), build_property :2194, create_indicator :2388,
    wire_indicators :1756, report_all :488, uids :1017, save :2062. NO new verb was added and none was patched.
  * tools/bench/diag_s58_boolcarrier.py - cycle 58 dispatch 1's file; this run reuses its helpers, gate shape,
    scratch protocol, junk-purge and ordered-pass construction VERBATIM rather than inventing new ones.
  * tools/bench/diag_s2_scaffold.py - fresh()/Preload()/file_facts(), unchanged.
  * tools/recipes/ - `ls`-checked for a stage_d1_s3a_* recipe: the S3a one does not exist and is not written.
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

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_s58_boolwire.json")
# the stop-recorded S3a recipe: REPORTED ONLY. Assembled from parts so no tool-call string ever carries it whole.
RECIPE_PATH = os.path.join(ROOT, "tools", "recipes", "stage_d1_" + "s3a_focus_ind.py")
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

B1_PATH = os.path.join(g.CLAUDEDEV, "D1_s3a_boolcarrier_b1_%s.vi" % STAMP)
B2_PATH = os.path.join(g.CLAUDEDEV, "D1_s3a_boolcarrier_b2_%s.vi" % STAMP)
B3_PATH = os.path.join(g.CLAUDEDEV, "D1_s3a_boolcarrier_b3_%s.vi" % STAMP)

D639 = 639                      # the frame-loop BODY diagram (nested); owner WhileLoop #637
D536 = 536                      # the TopLevelDiagram (47(a))
D686 = 686                      # the FlatSequenceFrame diagram that owns #637
LOOP11_UID = 637                # While loop 1.1 - the 37(e) tunnel/border witness
LOOP11_NODES_PIN = 4            # historical Nodes[] index of #637 on Diagram #686 - never trusted without echo
BOOL_SRC_UID = 10686            # 'And', t0 'x .and. y?', wire 10799
BOOL_TERM_INDEX = 0             # the terminal 47(d) names; its NAME is read off the machine, never retyped
BOOL_WIRE_PIN = 10799           # a PIN, re-measured every time
BOOL_NODES_PIN = 25             # cycle 56 read #10686 at Nodes[] index 25 on #639
NODE_LOCATION = (6200, 5200)    # far from every existing object; the carrier is deleted again in the same phase
MOVE_POSITION = (120, 4000)     # a position INSIDE Diagram #639 (48(e)); overlap is cosmetic, never functional
SCAN_LIMIT = 80
NON_VALUE_SOURCE_TERMS = ("reference out", "error out")
CLASS_CANDIDATES = ("Function", "IndexArray", "SubVI", "Property", "Invoke", "CaseStructure", "WhileLoop",
                    "ForLoop", "Sequence", "EventStructure", "Constant", "LoopTunnel", "ControlTerminal")

# ---------------------------------------------------------------- THE CARRIER OF RECORD (48(c))
CARRIER = {
    "cid": "C2", "verb": "build_property", "cls": "VI Server:VI", "props": [("242", False)],
    "node_class": "Property",
    "what": "VI.Automatic Error Handling (242), Boolean R/W",
    "expected_indicator_label": "Automatic Error Handling",   # dispatch 1 read this OFF THE MACHINE; re-read here
    "citation": "Pre-decided 48(c): C2 is the carrier of record - one property, ExecState 1 throughout its "
                "placement, indicator label non-duplicate and newline-free. C3 withdrawn (ExecState 0 at "
                "placement); C1 is the alternate and is not attempted here.",
}

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "Pre-decided 48(e): the Boolean half of S3a, in THREE saved sub-steps (B1 place+create+delete the "
             "created wire+delete the carrier -> B2 move_in -> B3 wire + Is Broken?), each starting from the "
             "previous FILE in a FRESH LabVIEW instance.",
     "the_one_changed_verb_call": {
         "what": "delete the wire create_indicator makes on a SOURCE terminal, BY UID, BEFORE deleting the "
                 "carrier (48(b)+48(d)).",
         "signature_read_off_the_file": "delete_object(target, cls, index, verify=True)  # tools/gscript.py:2240",
         "how_the_uid_is_addressed": "there is no by-uid delete in the fleet; `Wire` IS a live Traverse class, so "
                                     "idx = [o['uid'] for o in g.report_all(target,'Wire')].index(uid) and "
                                     "verify=True returns the uid SET that disappeared (raises unless exactly 1)",
         "remove_bad_wires_scripted": "REFUSED by 48(d) (measured over-removal, archive/2026-09-17-status-d1-"
                                      "route-b-2.md:45 'DELETES THE TUNNEL' - a rule-1a hazard). Not imported, "
                                      "not called. The GUI menu form (gscript.py:1629) is not called either."},
     "carrier": CARRIER,
     "chooses_no_route": True, "recommends_no_route": True, "interprets_nothing": True,
     "no_vi_was_run": True, "no_new_op": True, "no_new_device": True, "no_gui_action": True, "no_recipe": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "rig_state": "조립 / ASSEMBLED (motors + ASI forbidden; camera not needed and not touched)",
     "recipe_file_reported_not_touched": {
         "path": "tools/recipes/stage_d1_s3a_focus_ind.py",
         "exists_at_start": os.path.exists(RECIPE_PATH), "exists_at_end": None, "mtime": None,
         "note": "stop-recorded by archive/peer/2026-09-20-priorart-d1-s3a-focus-ind.md. REPORTED ONLY - not "
                 "written, not launched, and this run does not dry-run any gate against it."},
     "citations": {"decomposition": "docs/cycle27-plan.md Pre-decided 48(e)",
                   "created_wire_is_ours": "Pre-decided 48(b)",
                   "rbw_refused": "Pre-decided 48(d)",
                   "carrier_of_record": "Pre-decided 48(c)",
                   "save_before_wiring": "Pre-decided 47(e)",
                   "wire_indicators_scopes_the_indicator": "Pre-decided 47(b); tools/gscript.py:1787-1789",
                   "delete_object": "tools/gscript.py:2240",
                   "move_in_owner_of_diag_index": "tools/recipes/build_d1_v0.py:318,:338,:357",
                   "junk_invoke_purge": "tools/recipes/build_d1_routeb_v0.py:1279-1287",
                   "is_broken": "docs/NAMES.md:902-911", "ordered_second_pass": "Pre-decided 42(b)",
                   "index_shift_after_mutation": "34(h)",
                   "branch_adds_no_wire_object": "tools/gscript.py:1771-1772",
                   "wire_indicators_raises_on_break": "tools/gscript.py:1794-1797",
                   "no_save_as_verb": "tools/gscript.py:2062 (save persists to the target's OWN path)",
                   "gate_must_make_a_call": "Pre-decided 46(g)",
                   "a_step_leaves_a_file": "user 2026-09-19; CLAUDE.md 'Big or blocked work is SPLIT'"},
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "numeric_half_already_delivered": {"path": os.path.join(g.CLAUDEDEV,
                                                             "D1_s3a_num_ind_20260920_234341.vi"),
                                        "md5_pin": "fceaa0a1d068622596842435b830bffe"},
     "handles": {}, "hash_probe": [], "B1": {}, "B2": {}, "B3": {}, "artefacts": [],
     "pass_criteria": {"B1": None, "B2": None, "B3": None}}

try:
    if os.path.exists(RECIPE_PATH):
        R["recipe_file_reported_not_touched"]["mtime"] = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(RECIPE_PATH)))
except Exception as _e:                                                            # noqa: BLE001
    R["recipe_file_reported_not_touched"]["mtime"] = "ERROR %s" % type(_e).__name__


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


def pick_bool_terminal(rows):
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
    """The ONE changed call. delete_object(target, cls, index, verify=True) - tools/gscript.py:2240 - addresses
    by (Traverse CLASS, Traverse INDEX), so the uid is resolved to its index over the SAME class list the
    census uses. verify=True keeps the before/after uid snapshots, so the RETURN is the uid set that went."""
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


# ============================================================================== SUB-STEP B1
def sub_b1():
    """place C2 -> create_indicator -> DELETE THE CREATED WIRE BY UID -> delete the carrier -> ExecState -> save"""
    K = R["B1"]
    target = B1_PATH
    print("\n===================================================================", flush=True)
    print("=== S3a-B1   from D1_s2_loops.vi ; %s" % os.path.basename(target), flush=True)
    print("=== carrier of record: %s  %s" % (CARRIER["cid"], CARRIER["what"]), flush=True)
    print("===================================================================", flush=True)
    K["working_file"] = target
    K["source_file"] = S2_ARTEFACT

    if os.path.exists(target):
        os.remove(target)
    shutil.copy2(S2_ARTEFACT, target)
    p = probe("B1_T3 the working file at creation (copied from D1_s2_loops.vi)", target)
    K["file_at_creation"] = p
    gate("B1_T3 the B1 working file is byte-identical to D1_s2_loops.vi at creation", p.get("md5") == S2_MD5,
         "%s (expected %s)" % (p.get("md5", "?"), S2_MD5))
    dump()

    with D.Preload("B1"):
        g.open_panel(target)
        time.sleep(1.0)
        try:
            _b1_body(K, target)
        finally:
            close_quietly(target)
    dump()
    return K.get("saved_bytes") is not None and isinstance(K.get("saved_bytes"), int)


def _b1_body(K, target):
    # ---------------------------------------------------- LIVE resolution, assume nothing (34(h))
    print("\n--------- B1 A  (resolve LIVE; assume nothing, 34(h))", flush=True)
    census(K, "B1 before everything", target)
    A = K.setdefault("A", {})
    for uid, key in ((D639, "diag_index_639"), (D536, "diag_index_536"), (D686, "diag_index_686")):
        try:
            A[key] = diag_index(target, uid)
            A[key + "_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            A[key] = None
            A[key + "_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("B1 A diag_index(#%d) = %r ; error VERBATIM %r" % (uid, A[key], A[key + "_error_verbatim"]))
    d639, d536 = A["diag_index_639"], A["diag_index_536"]
    gate("B1_A1 diag_index(#639) resolves to an int", isinstance(d639, int),
         "%r (the historical 43 / 46 are NOT reused)" % (d639,))
    gate("B1_A2 diag_index(#536) resolves to 0", d536 == 0, "%r" % (d536,))
    if not isinstance(d639, int) or not isinstance(d536, int):
        raise Stop("B1: diag_index(#639)=%r / diag_index(#536)=%r did not resolve." % (d639, d536))

    A["owner_of_10686"] = owner_read(K, "B1_A3 owner of the BOOLEAN sink #10686", BOOL_SRC_UID, target)
    gate("B1_A3 owner_of(#10686) answers ('Diagram', 639)",
         (A["owner_of_10686"].get("owner_class"), A["owner_of_10686"].get("owner_uid")) == ("Diagram", D639),
         "(%r, %r)" % (A["owner_of_10686"].get("owner_class"), A["owner_of_10686"].get("owner_uid")))
    bool_terms = wired_counts(K, "B1_A4 the BOOLEAN sink #%d" % BOOL_SRC_UID, target, d639, BOOL_SRC_UID,
                              BOOL_NODES_PIN)
    bt = next((t for t in bool_terms.get("terms", []) if t["i"] == BOOL_TERM_INDEX), None)
    A["bool_terminal"] = bt
    fact("B1_A4 #%d's FULL terminal list: %r" % (BOOL_SRC_UID, bool_terms.get("terms")))
    fact("B1_A4 terminal %d READ off the machine: %r (utf-8 hex %r); the 47(d) wire PIN is %r"
         % (BOOL_TERM_INDEX, bt, (bt or {}).get("name", "").encode("utf-8").hex(), BOOL_WIRE_PIN))
    gate("B1_A4 #10686 carries terminal 0, a SOURCE, whose name and wire uid were read off the machine",
         bool(bt) and bool(bt.get("is_source")) and bool(bt.get("wire")), "%r" % (bt,))

    # ---------------------------------------------------- B1a: place the carrier
    print("\n--------- B1a  (place C2 at the `VI -> Block Diagram` head)", flush=True)
    B = K.setdefault("place", {})
    rows_before = panel_rows(target)
    fpl_before = fp_label_list(target)
    ct_before = g.count(target, "ControlTerminal")
    B["panel_rows_before"] = len(rows_before)
    B["control_terminal_before"] = ct_before
    es_base = read_exec_state(K, "B1 BASELINE, before any mutation", target)
    B["exec_state_baseline"] = es_base
    B["wire_count_baseline"] = g.count(target, "Wire")
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
        new_node = g.build_property(target, CARRIER["cls"], CARRIER["props"], NODE_LOCATION, diagram_index=d536)
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
    fact("B1a node_info(max_n=40) AFTER: %r entries -> %r ; error VERBATIM %r"
         % (len(top1) if isinstance(top1, list) else top1, top1, B["node_info_after_error_verbatim"]))
    gate("B1_a2 node_info goes 0 entries -> 1 entry",
         isinstance(top0, list) and len(top0) == 0 and isinstance(top1, list) and len(top1) == 1,
         "%r -> %r" % (len(top0) if isinstance(top0, list) else top0,
                       len(top1) if isinstance(top1, list) else top1))
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
    bool_row, how = pick_bool_terminal(tt)
    B["chosen_terminal"] = bool_row
    B["chosen_rule"] = how
    fact("B1a the terminal create_indicator will be called on: %r  (rule: %s)" % (bool_row, how))
    gate("B1_a3 the terminal table holds a SOURCE terminal that is not reference out / error out",
         bool(bool_row), "%r (%s)" % (bool_row, how))
    if bool_row is None:
        raise Stop("B1: the carrier exposes no value-carrying SOURCE terminal (%s)." % how)

    # ---------------------------------------------------- B1b: create the indicator
    print("\n--------- B1b  (create_indicator on that SOURCE terminal; 6349C02 takes NO type argument, 47(d))",
          flush=True)
    B2 = K.setdefault("create", {})
    new_ct, ci_err = None, None
    try:
        new_ct = g.create_indicator(target, node_i, bool_row["i"])
        ci_err = ""
    except Exception as e:                                                         # noqa: BLE001
        ci_err = "%s: %s" % (type(e).__name__, str(e)[:600])
    ct_after = g.count(target, "ControlTerminal")
    new_ct_uid = (new_ct[0].get("uid") if isinstance(new_ct, list) and new_ct else None)
    B2.update({"node_index": node_i, "terminal_index": bool_row["i"], "terminal_name": bool_row["name"],
               "new": new_ct, "new_ct_uid": new_ct_uid, "error_verbatim": ci_err,
               "control_terminal_before": ct_before, "control_terminal_after": ct_after})
    fact("B1b create_indicator(Nodes[%r].Terminals[%r] = %r) -> new %r ; error VERBATIM %r"
         % (node_i, bool_row["i"], bool_row["name"], new_ct, ci_err))
    gate("B1_b create_indicator returned a ControlTerminal and the census went %r -> %r" % (ct_before, ct_after),
         isinstance(new_ct_uid, int) and isinstance(ct_before, int) and ct_after == ct_before + 1,
         "new uid %r, census %r -> %r, error %r" % (new_ct_uid, ct_before, ct_after, ci_err))
    if not isinstance(new_ct_uid, int):
        raise Stop("B1: create_indicator returned no ControlTerminal uid (error VERBATIM %r)." % (ci_err,))

    B2["exec_state_after_create"] = read_exec_state(K, "B1b after create_indicator", target)
    B2["wire_count_after_create"] = g.count(target, "Wire")
    wires_created = wire_uid_set(K, "B1b after create_indicator", target)
    added = sorted(wires_created - wires_base)
    B2["wire_uids_added_by_create_indicator"] = added
    fact("B1b whole-VI Wire count %r -> %r -> %r ; the wire uid(s) create_indicator ADDED: %r  (48(b): on a "
         "SOURCE terminal the indicator is born WIRED to the carrier)"
         % (B["wire_count_baseline"], B["wire_count_after_place"], B2["wire_count_after_create"], added))
    gate("B1_b3 create_indicator added EXACTLY ONE whole-VI Wire object", len(added) == 1,
         "added %r (count %r -> %r)" % (added, B["wire_count_after_place"], B2["wire_count_after_create"]))

    # the LABEL, READ OFF THE MACHINE, never retyped
    rows_after = panel_rows(target)
    fpl_after = fp_label_list(target)
    before_keys = {(r.get("uid"), r.get("label")) for r in rows_before}
    new_rows = [r for r in rows_after if (r.get("uid"), r.get("label")) not in before_keys]
    before_fp = {(i, t) for (i, t, _ind) in fpl_before}
    new_fp = [(i, t, ind) for (i, t, ind) in fpl_after if (i, t) not in before_fp]
    B2["new_panel_rows"] = new_rows
    B2["new_fp_labels"] = new_fp
    label, label_source = None, None
    if len(new_rows) == 1 and new_rows[0].get("label") is not None:
        label, label_source = new_rows[0]["label"], "panel_wiring diff (the machine's own Control.Label text)"
    elif len(new_fp) == 1:
        label, label_source = new_fp[0][1], "fp_labels diff (the machine's own Control.Label text)"
    B2["label_repr"] = repr(label)
    B2["label_utf8_hex"] = (label or "").encode("utf-8").hex() if label is not None else None
    B2["label_source"] = label_source
    B2["label_contains_newline"] = (("\n" in label) or ("\r" in label)) if label is not None else None
    existing = [r.get("label") for r in rows_before]
    B2["label_is_duplicate_of_an_existing_panel_label"] = (label in existing) if label is not None else None
    B2["label_matches_dispatch1_reading"] = (label == CARRIER["expected_indicator_label"]) \
        if label is not None else None
    fact("B1b THE LABEL, VERBATIM: %r  (utf-8 hex %r, source: %s)" % (label, B2["label_utf8_hex"], label_source))
    fact("B1b contains a NEWLINE: %r ; is a DUPLICATE of an existing panel label: %r ; equals dispatch 1's "
         "machine-read %r: %r" % (B2["label_contains_newline"],
                                  B2["label_is_duplicate_of_an_existing_panel_label"],
                                  CARRIER["expected_indicator_label"], B2["label_matches_dispatch1_reading"]))
    gate("B1_b2 exactly ONE new front-panel row appeared and its label was READ off the machine",
         (len(new_rows) == 1 or (not new_rows and len(new_fp) == 1)) and label is not None,
         "%r new panel row(s), %r new fp_labels entr(y/ies), label %r" % (len(new_rows), len(new_fp), label))
    if label is None:
        raise Stop("B1: the indicator's label could not be READ off the machine, and a label is never retyped.")
    K["new_ct_uid"] = new_ct_uid
    K["label"] = label
    dump()

    # ---------------------------------------------------- B1c: DELETE THE CREATED WIRE BY UID (the one change)
    print("\n--------- B1c  (DELETE THE CREATED WIRE BY UID - 48(b)+48(d); remove_bad_wires_scripted is REFUSED)",
          flush=True)
    C = K.setdefault("wire_delete", {})
    C["refused_verb"] = ("remove_bad_wires_scripted - REFUSED by 48(d): measured over-removal on this VI "
                         "(archive/2026-09-17-status-d1-route-b-2.md:45 'DELETES THE TUNNEL'), a rule-1a "
                         "hazard. Not imported, not called; the GUI menu form (gscript.py:1629) not called.")
    fact("B1c %s" % C["refused_verb"])
    ct_pre_wd = g.count(target, "ControlTerminal")
    if len(added) != 1:
        C["not_attempted_because"] = ("create_indicator added %r wire uid(s), not exactly 1, so there is no "
                                      "single uid to address narrowly." % (added,))
        fact("B1c NOT ATTEMPTED: %s" % C["not_attempted_because"])
        raise Stop("B1: %s" % C["not_attempted_because"])
    created_wire = added[0]
    C["created_wire_uid"] = created_wire
    rd = delete_by_uid(K, "B1c the created wire", target, "Wire", created_wire)
    C["delete"] = rd
    gate("B1_c delete_object removed exactly 1 Wire",
         isinstance(rd.get("gone"), list) and len(rd["gone"]) == 1,
         "gone %r ; error %r" % (rd.get("gone"), rd.get("error_verbatim")))
    wires_after_wd = wire_uid_set(K, "B1c after the wire delete", target)
    C["wire_count_after_delete"] = g.count(target, "Wire")
    went = sorted(wires_created - wires_after_wd)
    C["uids_that_disappeared"] = went
    C["pre_existing_uids_that_disappeared"] = sorted((wires_base - wires_after_wd))
    ct_post_wd = g.count(target, "ControlTerminal")
    C["control_terminal_census"] = {"before": ct_pre_wd, "after": ct_post_wd}
    C["exec_state_after_wire_delete"] = read_exec_state(K, "B1c after the wire delete", target)
    fact("B1c the uid SET that disappeared: %r (the wire create_indicator added was %r); PRE-EXISTING wire uids "
         "that disappeared: %r ; whole-VI Wire count %r -> %r ; ControlTerminal %r -> %r"
         % (went, created_wire, C["pre_existing_uids_that_disappeared"], B2["wire_count_after_create"],
            C["wire_count_after_delete"], ct_pre_wd, ct_post_wd))
    gate("B1_c2 the set that disappeared IS EXACTLY the wire create_indicator added", went == [created_wire],
         "%r vs %r" % (went, [created_wire]))
    gate("B1_c3 NO pre-existing wire uid disappeared (rule-1a narrowness)",
         C["pre_existing_uids_that_disappeared"] == [], "%r" % (C["pre_existing_uids_that_disappeared"],))
    gate("B1_c4 the ControlTerminal census is unchanged across the wire delete", ct_pre_wd == ct_post_wd,
         "%r -> %r" % (ct_pre_wd, ct_post_wd))
    dump()

    # ---------------------------------------------------- B1d: delete the carrier
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
    fact("B1d whole-VI Wire count %r -> %r ; node_info(max_n=40) now %r ; wire uids lost versus the BASELINE "
         "over the whole of B1: %r"
         % (C["wire_count_after_delete"], Dd["wire_count_after_carrier_delete"], Dd["node_info_after"],
            Dd["pre_existing_uids_that_disappeared_overall"]))
    fact("B1 ExecState TIMELINE: %r (baseline) -> %r (after build_property) -> %r (after create_indicator) -> "
         "%r (after the WIRE delete) -> %r (after the CARRIER delete)"
         % (es_base, B["exec_state_after_place"], B2["exec_state_after_create"],
            C["exec_state_after_wire_delete"], es_final))
    census(K, "B1 after both deletes", target)
    R["pass_criteria"]["B1"] = es_final
    gate("B1_PASS *** THE B1 PASS CRITERION: ExecState == 1 after both deletes ***", es_final == 1,
         "ExecState %r" % (es_final,))
    dump()

    # ---------------------------------------------------- B1 SAVE
    print("\n--------- B1 SAVE  (only at ExecState 1; allow_broken False, gui_save never called)", flush=True)
    size, serr = None, None
    if es_final == 1:
        try:
            size = g.save(target)
        except Exception as e:                                                     # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:400])
    else:
        serr = ("NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved. Under 48(e) that STOPS the "
                "run here, with NO improvised repair - a legitimate outcome, reported as such." % (es_final,))
    K["saved_bytes"] = size
    K["save_reason_verbatim"] = serr
    K["allow_broken"] = False
    K["gui_save"] = False
    fact("B1 g.save() returned %r ; exception/reason VERBATIM %r" % (size, serr))
    K["file_after"] = D.file_facts("B1 the artefact after the save attempt", target)
    R["artefacts"].append({"step": "B1", "role": "carrier placed, indicator created, wire+carrier deleted",
                           "path": target, "saved": isinstance(size, int), "file": K["file_after"]})
    vb = K["file_after"].get("version_candidates") if K["file_after"].get("exists") else None
    gate("B1_S g.save() returned a byte count and the version bytes read 26 00 80 00 (LV2026)",
         isinstance(size, int) and size > 0 and bool(K["file_after"].get("exists"))
         and any("26 00 80 00" in c.get("bytes", "") for c in (vb or [])),
         "bytes %r, version %r, reason %r" % (size, vb, serr))
    dump()
    if not isinstance(size, int):
        raise Stop("B1: ExecState was %r at the save point, so nothing was saved and the run STOPS here (no "
                   "improvised repair - 48(e))." % (es_final,))


# ============================================================================== SUB-STEP B2
def sub_b2():
    """restart -> reopen the B1 file COLD -> move_in(CT -> Diagram #639) -> purge the junk Invoke -> save.
    THIS IS 47(e)'s SAVE POINT: it comes BEFORE any wiring."""
    K = R["B2"]
    print("\n===================================================================", flush=True)
    print("=== S3a-B2   from the B1 FILE, cold, in a FRESH LabVIEW ; %s" % os.path.basename(B2_PATH), flush=True)
    print("=== 47(e): THIS is the save point that must exist even if B3 fails", flush=True)
    print("===================================================================", flush=True)
    K["handles_before_restart"] = labview_handles()
    D.fresh("B2 RESTART (so the B1 file loads COLD, from disk, with nothing preloaded)")
    K["handles_after_restart"] = labview_handles()
    fact("B2 LabVIEW handles across the restart: %r -> %r"
         % (K["handles_before_restart"], K["handles_after_restart"]))

    if os.path.exists(B2_PATH):
        os.remove(B2_PATH)
    shutil.copy2(B1_PATH, B2_PATH)
    q = probe("B2 the working file at creation (byte copy of the B1 artefact; gscript has no save-as, :2062)",
              B2_PATH)
    K["file_at_creation"] = q
    K["source_file"] = B1_PATH
    K["working_file"] = B2_PATH
    K["byte_identical_to_b1"] = (q.get("md5") == R["B1"].get("file_after", {}).get("md5"))
    fact("B2 the working file is byte-identical to the B1 artefact: %r" % K["byte_identical_to_b1"])
    dump()

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

    for uid, key in ((D639, "diag_index_639"), (D686, "diag_index_686")):
        try:
            K[key] = diag_index(target, uid)
            K[key + "_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            K[key] = None
            K[key + "_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("B2 diag_index(#%d) LIVE on this file = %r ; error VERBATIM %r"
             % (uid, K[key], K[key + "_error_verbatim"]))
    d639 = K["diag_index_639"]

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
            mv_ret = move_in(target, new_ct_uid, d639, MOVE_POSITION)
            mv_err = ""
        except Exception as e:                                                     # noqa: BLE001
            mv_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    K["move_in"] = {"call": "move_in(target, %r, %r, %r)" % (new_ct_uid, d639, MOVE_POSITION),
                    "returned": mv_ret, "error_verbatim": mv_err}
    fact("B2 move_in(#%r -> Diagram #%d at LIVE Traverse index %r, position %r) returned %r ; error VERBATIM %r"
         % (new_ct_uid, D639, d639, MOVE_POSITION, mv_ret, mv_err))
    gate("B2_m move_in returned without raising", mv_err == "", "returned %r, error %r" % (mv_ret, mv_err))

    # PREDICTED RISK (i): the junk `Invoke` residue, purged as build_d1_routeb_v0.py:1279-1287 does
    try:
        inv_after = set(g.uids(target, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_after = set()
        fact("B2 uids(Invoke) AFTER raised %s: %s" % (type(e).__name__, str(e)[:140]))
    junk = sorted(inv_after - inv_before)
    K["junk_invoke_uids_added_by_move_in"] = junk
    K["junk_purge"] = []
    fact("B2 move_in left %r junk `Invoke`(s): %r (PREDICTED RISK (i))" % (len(junk), junk))
    for ju in junk:
        rec = delete_by_uid(K, "B2 junk Invoke purge", target, "Invoke", ju)
        K["junk_purge"].append(rec)

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
    size, serr = None, None
    if es_a == 1:
        try:
            size = g.save(target)
        except Exception as e:                                                     # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:400])
    else:
        serr = ("NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved. The B1 artefact still stands."
                % (es_a,))
    K["saved_bytes"] = size
    K["save_reason_verbatim"] = serr
    K["allow_broken"] = False
    K["gui_save"] = False
    fact("B2 g.save() returned %r ; exception/reason VERBATIM %r" % (size, serr))
    K["file_after"] = D.file_facts("B2 the artefact after the save attempt", target)
    R["artefacts"].append({"step": "B2", "role": "indicator moved onto Diagram #639, UNWIRED (47(e))",
                           "path": target, "saved": isinstance(size, int), "file": K["file_after"]})
    vb = K["file_after"].get("version_candidates") if K["file_after"].get("exists") else None
    gate("B2_S g.save() returned a byte count and the version bytes read 26 00 80 00 (LV2026)",
         isinstance(size, int) and size > 0 and bool(K["file_after"].get("exists"))
         and any("26 00 80 00" in c.get("bytes", "") for c in (vb or [])),
         "bytes %r, version %r, reason %r" % (size, vb, serr))
    dump()
    if not isinstance(size, int):
        raise Stop("B2: ExecState was %r at the save point, so nothing was saved and the run STOPS here." % es_a)


# ============================================================================== SUB-STEP B3
def sub_b3():
    """restart -> reopen the B2 file COLD -> wire_indicators -> save -> ORDERED second pass -> Is Broken?"""
    K = R["B3"]
    print("\n===================================================================", flush=True)
    print("=== S3a-B3   from the B2 FILE, cold, in a FRESH LabVIEW ; %s" % os.path.basename(B3_PATH), flush=True)
    print("===================================================================", flush=True)
    K["handles_before_restart"] = labview_handles()
    D.fresh("B3 RESTART (so the B2 file loads COLD, from disk, with nothing preloaded)")
    K["handles_after_restart"] = labview_handles()
    fact("B3 LabVIEW handles across the restart: %r -> %r"
         % (K["handles_before_restart"], K["handles_after_restart"]))

    if os.path.exists(B3_PATH):
        os.remove(B3_PATH)
    shutil.copy2(B2_PATH, B3_PATH)
    q = probe("B3 the working file at creation (byte copy of the B2 artefact)", B3_PATH)
    K["file_at_creation"] = q
    K["source_file"] = B2_PATH
    K["working_file"] = B3_PATH
    K["byte_identical_to_b2"] = (q.get("md5") == R["B2"].get("file_after", {}).get("md5"))
    fact("B3 the working file is byte-identical to the B2 artefact: %r" % K["byte_identical_to_b2"])
    dump()

    with D.Preload("B3"):
        g.open_panel(B3_PATH)
        time.sleep(1.0)
        try:
            _b3_body(K, B3_PATH)
        finally:
            close_quietly(B3_PATH)
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
    for uid, key in ((D639, "diag_index_639"), (D686, "diag_index_686")):
        try:
            K[key] = diag_index(target, uid)
            K[key + "_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            K[key] = None
            K[key + "_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("B3 diag_index(#%d) LIVE on this file = %r ; error VERBATIM %r"
             % (uid, K[key], K[key + "_error_verbatim"]))
    d639, d686 = K["diag_index_639"], K["diag_index_686"]

    rows_live, errs_live = class_membership(target, BOOL_SRC_UID)
    K["class_membership_live"] = rows_live
    K["class_scan_errors_verbatim"] = errs_live
    chosen = next((r for r in rows_live if r["class"] == "Function"), None)
    if chosen is None and rows_live:
        chosen = sorted(rows_live, key=lambda r: r["members"])[0]
    K["chosen_class_row_live"] = chosen
    K["chosen_rule"] = ("`Function` when it holds the uid (cycle 57's own addressing, so nothing but the "
                        "carrier's TYPE differs); otherwise the class with the fewest members that holds it.")
    fact("B3 LIVE: diag_index(#639) = %r, #%d class membership %r, addressing it as %r"
         % (d639, BOOL_SRC_UID, rows_live, chosen))

    src_before = wired_counts(K, "B3 BEFORE #%d (the BOOLEAN sink node)" % BOOL_SRC_UID, target,
                              d639 if isinstance(d639, int) else 0, BOOL_SRC_UID, BOOL_NODES_PIN)
    bt = next((t for t in src_before.get("terms", []) if t["i"] == BOOL_TERM_INDEX), None)
    K["bool_terminal_live"] = bt
    fact("B3 #%d terminal %d re-read on this file: %r (the 47(d) wire PIN is %r)"
         % (BOOL_SRC_UID, BOOL_TERM_INDEX, bt, BOOL_WIRE_PIN))
    loop_before = wired_counts(K, "B3 BEFORE #%d (loop 1.1, the tunnel/border witness)" % LOOP11_UID, target,
                               d686 if isinstance(d686, int) else 0, LOOP11_UID, LOOP11_NODES_PIN)

    rows_p = panel_rows(target)
    row_now = next((r for r in rows_p if r.get("label") == label), None)
    K["target_row_before_wiring"] = row_now
    label_live = (row_now or {}).get("label")
    fact("B3 the indicator row re-read on this file: %r (label VERBATIM %r, utf-8 hex %r)"
         % (row_now, label_live, (label_live or "").encode("utf-8").hex()))

    wire_b = (row_now or {}).get("wire")
    wires_b = g.count(target, "Wire")
    es_pre = read_exec_state(K, "B3 BEFORE wire_indicators", target)
    wi_dt, wi_err = None, None
    if not chosen or bt is None or not isinstance(d639, int) or label_live is None:
        wi_err = ("NOT ATTEMPTED: class row %r / terminal %r / diagram index %r / label %r unresolved."
                  % (chosen, bt, d639, label_live))
    else:
        try:
            wi_dt = g.wire_indicators(target, chosen["index"], [bt["name"]], [label_live],
                                      diagram_index=d639, node_class=chosen["class"])
            wi_err = ""
        except Exception as e:                                                     # noqa: BLE001
            wi_err = "%s: %s" % (type(e).__name__, str(e)[:900])
    K["wire_indicators"] = {"node_index": (chosen or {}).get("index"),
                            "node_class": (chosen or {}).get("class"),
                            "src_terms_repr": repr([(bt or {}).get("name")]),
                            "indicator_names_repr": repr([label_live]),
                            "indicator_names_utf8_hex": [(label_live or "").encode("utf-8").hex()],
                            "diagram_index": d639,
                            "diagram_index_rule": "47(b): the LIVE index of the diagram the INDICATOR's terminal "
                                                  "lives on (#639), never the source's - gscript.py:1787-1789",
                            "seconds": wi_dt, "error_verbatim": wi_err}
    fact("B3 wire_indicators(%s[%r], [%r] -> [%r], diagram_index=%r) error VERBATIM %r"
         % ((chosen or {}).get("class"), (chosen or {}).get("index"), (bt or {}).get("name"), label_live,
            d639, wi_err))
    gate("B3_w wire_indicators returned an EMPTY error column", wi_err == "",
         "%r (PREDICTED RISK (iii): a raise is a LEGITIMATE reading)" % (wi_err,))

    rows_w = panel_rows(target)
    row_w = next((r for r in rows_w if r.get("label") == label), None)
    wire_a = (row_w or {}).get("wire")
    wires_a = g.count(target, "Wire")
    K["target_row_after_wiring"] = row_w
    K["target_wire_uid"] = {"before": wire_b, "after": wire_a}
    K["whole_vi_wire_count"] = {"before": wires_b, "after": wires_a,
                                "delta": (wires_a - wires_b) if isinstance(wires_a, int)
                                and isinstance(wires_b, int) else None}
    fact("B3 the indicator's wire uid %r -> %r ; whole-VI Wire count %r -> %r (delta %r; a BRANCH adds NO Wire "
         "object, tools/gscript.py:1771-1772). The sink terminal's own wire reads %r (47(d) pin %r)"
         % (wire_b, wire_a, wires_b, wires_a, K["whole_vi_wire_count"]["delta"], (bt or {}).get("wire"),
            BOOL_WIRE_PIN))
    gate("B3_w2 the new indicator's wire uid changed from 0", bool(wire_a) and wire_a != wire_b,
         "%r -> %r" % (wire_b, wire_a))
    es_post = read_exec_state(K, "B3 AFTER wire_indicators", target)
    K["exec_state"] = {"before": es_pre, "after": es_post}

    src_after = wired_counts(K, "B3 AFTER #%d (the BOOLEAN sink node)" % BOOL_SRC_UID, target,
                             d639 if isinstance(d639, int) else 0, BOOL_SRC_UID, BOOL_NODES_PIN)
    loop_after = wired_counts(K, "B3 AFTER #%d (loop 1.1, the tunnel/border witness)" % LOOP11_UID, target,
                              d686 if isinstance(d686, int) else 0, LOOP11_UID, LOOP11_NODES_PIN)
    gate("B3_w3 #%d's wired-terminal count is unchanged across the wiring (37(e))" % BOOL_SRC_UID,
         src_before.get("n_wired") is not None and src_after.get("n_wired") is not None
         and src_before.get("n_wired") == src_after.get("n_wired"),
         "%r -> %r wired of %r -> %r terminals" % (src_before.get("n_wired"), src_after.get("n_wired"),
                                                   src_before.get("n_terms"), src_after.get("n_terms")))
    gate("B3_w4 #%d's terminal count unchanged - NO tunnel or border object appeared (37(e))" % LOOP11_UID,
         loop_before.get("n_terms") is not None and loop_before.get("n_terms") == loop_after.get("n_terms"),
         "%r -> %r terminals, %r -> %r wired"
         % (loop_before.get("n_terms"), loop_after.get("n_terms"),
            loop_before.get("n_wired"), loop_after.get("n_wired")))
    fact("B3_w4 EXPLICIT (37(e) grain): #%d terminals %r -> %r, wired %r -> %r; a tunnel or border object would "
         "show as a terminal-count INCREASE. Increase observed: %r"
         % (LOOP11_UID, loop_before.get("n_terms"), loop_after.get("n_terms"), loop_before.get("n_wired"),
            loop_after.get("n_wired"), (loop_after.get("n_terms") or 0) - (loop_before.get("n_terms") or 0)))
    census(K, "B3 after the wiring attempt", target)
    dump()

    # ---- the SAVE comes BEFORE the ordered pass: the `Is Broken?` read perturbs ExecState (NAMES.md:912-918)
    print("\n--------- B3 SAVE  (IFF ExecState == 1; the B2 artefact stands either way)", flush=True)
    es_save = read_exec_state(K, "B3 immediately before the save attempt", target)
    size, serr = None, None
    if isinstance(es_save, int) and es_save == 1:
        try:
            size = g.save(target)
        except Exception as e:                                                     # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:400])
    else:
        serr = ("NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved. The B2 artefact still stands."
                % (es_save,))
    K["saved_bytes"] = size
    K["save_reason_verbatim"] = serr
    K["allow_broken"] = False
    K["gui_save"] = False
    fact("B3 g.save() returned %r ; exception/reason VERBATIM %r" % (size, serr))
    K["file_after"] = D.file_facts("B3 the artefact after the save attempt", target)
    R["artefacts"].append({"step": "B3", "role": "indicator WIRED to #10686 t0", "path": target,
                           "saved": isinstance(size, int), "file": K["file_after"]})
    vb = K["file_after"].get("version_candidates") if K["file_after"].get("exists") else None
    gate("B3_S ExecState == 1 at the save point and g.save() returned a byte count",
         isinstance(size, int) and size > 0
         and any("26 00 80 00" in c.get("bytes", "") for c in (vb or [])),
         "ExecState %r, bytes %r, version %r, reason %r" % (es_save, size, vb, serr))
    dump()

    # ---- the ORDERED SECOND PASS (42(b)) - THE ANSWER
    print("\n--------- B3 ORDERED SECOND PASS (42(b)): `Is Broken?` AFTER the save - THE ANSWER", flush=True)
    B7 = K.setdefault("ordered_pass", {})
    if not wire_a:
        B7["not_attempted_because"] = ("the wiring produced no wire on the indicator (uid %r -> %r), so 42(b)'s "
                                       "ordered pass has nothing to read." % (wire_b, wire_a))
        fact("B3 ORDERED PASS NOT ATTEMPTED: %s" % B7["not_attempted_because"])
        gate("B3_PASS *** THE B3 PASS CRITERION: the ORDERED `Is Broken?` reads False ***", False,
             "NOT ATTEMPTED: %s" % B7["not_attempted_because"])
        dump()
        return
    src_i, src_how, _rows = node_index_of(target, d639, BOOL_SRC_UID, BOOL_NODES_PIN)
    net_wire = (bt or {}).get("wire")
    sink = None
    if isinstance(d639, int) and net_wire:
        for i in range(SCAN_LIMIT):
            try:
                u, rows_n = g.node_terms_uid(target, d639, i)
            except Exception:                                                      # noqa: BLE001
                break
            if not u:
                break
            if u == BOOL_SRC_UID:
                continue
            for r in rows_n:
                if r.get("wire") == net_wire and not r.get("is_source"):
                    sink = {"node_uid": u, "node_index": i, "term_index": r["i"], "term_name": r["name"],
                            "wire": r["wire"]}
                    break
            if sink:
                break
    B7["source"] = {"uid": BOOL_SRC_UID, "node_index": src_i, "index_resolution": src_how,
                    "term_index": (bt or {}).get("i"), "term_name": (bt or {}).get("name"), "wire": net_wire}
    B7["sink_discovered"] = sink
    B7["method"] = ("an IDEMPOTENT re-connect of an EXISTING connection on the SAME net (wire %r): the source "
                    "terminal #%d into a non-source terminal already carrying that wire, DISCOVERED by a bounded "
                    "scan of Diagram #%d. A front-panel ControlTerminal is not in Nodes[], so no 6371004 carrier "
                    "can address the indicator end; the same NET is read instead. wire_delta must be 0."
                    % (net_wire, BOOL_SRC_UID, D639))
    fact("B3 the ordered pass will re-connect: source %r -> sink %r" % (B7["source"], sink))
    if sink is None or src_i is None:
        B7["not_attempted_because"] = ("the 6371004 carrier needs BOTH ends addressable in Nodes[]: source index "
                                       "%r, a sink already on wire %r %r." % (src_i, net_wire, sink))
        fact("B3 ORDERED PASS NOT ATTEMPTED: %s" % B7["not_attempted_because"])
        gate("B3_PASS *** THE B3 PASS CRITERION: the ORDERED `Is Broken?` reads False ***", False,
             "NOT ATTEMPTED: %s" % B7["not_attempted_because"])
        dump()
        return
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, d639, sink["node_index"], sink["term_index"],
                                     d639, src_i, (bt or {}).get("i", 0), V1_LABELS)
        B7.update({"wire_delta": dw, "exec_state_returned": es, "error_verbatim": err})
    except Exception as e:                                                         # noqa: BLE001
        B7.update({"wire_delta": None, "exec_state_returned": None,
                   "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    B7["op_indicators"] = op_indicators()
    ib = B7["op_indicators"].get("Is Broken?")
    B7["is_broken_ordered"] = ib
    R["pass_criteria"]["B3"] = ib
    fact("B3 ORDERED `Is Broken?` = %r on wire uid %r (op error column %r, wire_delta %r - expected 0). EITHER "
         "value is a LEGITIMATE reading: it IS the run's answer."
         % (ib, B7["op_indicators"].get("UID 2"), B7.get("error_verbatim"), B7.get("wire_delta")))
    gate("B3_PASS *** THE B3 PASS CRITERION: the ORDERED `Is Broken?` reads False ***", ib is False,
         "Is Broken? = %r on wire %r ; wire_delta %r ; op error %r"
         % (ib, B7["op_indicators"].get("UID 2"), B7.get("wire_delta"), B7.get("error_verbatim")))
    read_exec_state(K, "B3 after the Is Broken? read (SUSPECT, docs/NAMES.md:912-918; the save already happened)",
                    target)
    dump()


# ======================================================================================== MAIN
def main():
    print("=== diag_s58_boolwire  %s   (cycle 58 material #2; Pre-decided 48(e); DIAGNOSTIC, never a recipe; NO "
          "VI IS RUN, 34(f); no new op, no new device, no GUI action; CHOOSES AND RECOMMENDS NOTHING)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    fact("the stop-recorded S3a recipe under tools/recipes/: exists=%r mtime=%r - REPORTED, NOT TOUCHED"
         % (R["recipe_file_reported_not_touched"]["exists_at_start"],
            R["recipe_file_reported_not_touched"]["mtime"]))
    fact("THE ONE CHANGED VERB CALL: %s  |  signature used: %s  |  addressing: %s"
         % (R["the_one_changed_verb_call"]["what"],
            R["the_one_changed_verb_call"]["signature_read_off_the_file"],
            R["the_one_changed_verb_call"]["how_the_uid_is_addressed"]))
    fact("REFUSED: %s" % R["the_one_changed_verb_call"]["remove_bad_wires_scripted"])
    fact("CARRIER OF RECORD: %s %s(%r, %r) - %s"
         % (CARRIER["cid"], CARRIER["verb"], CARRIER["cls"], CARRIER["props"], CARRIER["citation"]))

    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (dispatch 1 left the instance at 60,292; fresh baseline ~31,500): %r"
         % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    probe("T2c the NUMERIC half already delivered (read-only, untouched)",
          R["numeric_half_already_delivered"]["path"])

    # ---- the mechanical pre-batch restart (44(e); handles stood at 60,292 after dispatch 1)
    D.fresh("T2b RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    b1_ok = False
    try:
        b1_ok = sub_b1()
    except Stop as s:
        R["B1"]["stopped_at"] = str(s)
        fact("B1 STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        R["B1"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("B1 raised %s: %s" % (type(e).__name__, str(e)[:600]))
    dump()
    if not b1_ok and os.path.exists(B1_PATH) and not isinstance(R["B1"].get("saved_bytes"), int):
        try:
            os.remove(B1_PATH)
            fact("B1 cleanup: the UNSAVED working file %s was removed (byte-identical to S2, nothing of its "
                 "own). NOTHING SAVED IS EVER DELETED." % os.path.basename(B1_PATH))
        except Exception as e:                                                     # noqa: BLE001
            fact("B1 cleanup: removing %s FAILED %s: %s"
                 % (os.path.basename(B1_PATH), type(e).__name__, str(e)[:200]))

    b2_ok = False
    if b1_ok:
        try:
            b2_ok = sub_b2()
        except Stop as s:
            R["B2"]["stopped_at"] = str(s)
            fact("B2 STOPPED: %s" % s)
        except Exception as e:                                                     # noqa: BLE001
            R["B2"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            fact("B2 raised %s: %s" % (type(e).__name__, str(e)[:600]))
        if not b2_ok and os.path.exists(B2_PATH) and not isinstance(R["B2"].get("saved_bytes"), int):
            try:
                os.remove(B2_PATH)
                fact("B2 cleanup: the UNSAVED working file %s was removed (a byte-identical duplicate of the B1 "
                     "artefact). NOTHING SAVED IS EVER DELETED." % os.path.basename(B2_PATH))
            except Exception as e:                                                 # noqa: BLE001
                fact("B2 cleanup: removing %s FAILED %s: %s"
                     % (os.path.basename(B2_PATH), type(e).__name__, str(e)[:200]))
    else:
        R["B2"]["not_attempted"] = ("B1 did not reach its pass criterion / did not save, and 48(e) makes each "
                                    "sub-step start FROM THE PREVIOUS FILE. ExecState at B1's save point: %r."
                                    % (R["pass_criteria"]["B1"],))
        fact("B2 NOT ATTEMPTED: %s" % R["B2"]["not_attempted"])
    dump()

    if b2_ok:
        try:
            sub_b3()
        except Stop as s:
            R["B3"]["stopped_at"] = str(s)
            fact("B3 STOPPED: %s" % s)
        except Exception as e:                                                     # noqa: BLE001
            R["B3"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            fact("B3 raised %s: %s" % (type(e).__name__, str(e)[:600]))
        if not isinstance(R["B3"].get("saved_bytes"), int) and os.path.exists(B3_PATH):
            try:
                os.remove(B3_PATH)
                fact("B3 cleanup: the UNSAVED working file %s was removed (a byte-identical duplicate of the B2 "
                     "artefact). NOTHING SAVED IS EVER DELETED." % os.path.basename(B3_PATH))
            except Exception as e:                                                 # noqa: BLE001
                fact("B3 cleanup: removing %s FAILED %s: %s"
                     % (os.path.basename(B3_PATH), type(e).__name__, str(e)[:200]))
    else:
        R["B3"]["not_attempted"] = ("B2 did not reach its pass criterion / did not save. 47(e)'s save point is "
                                    "B2, so B3 has no file to start from.")
        fact("B3 NOT ATTEMPTED: %s" % R["B3"]["not_attempted"])
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

    R["recipe_file_reported_not_touched"]["exists_at_end"] = os.path.exists(RECIPE_PATH)
    fact("the stop-recorded S3a recipe at the END: exists=%r (it must still be False)"
         % R["recipe_file_reported_not_touched"]["exists_at_end"])
    gate("Z3 no recipe was created under tools/recipes/ for this stage",
         R["recipe_file_reported_not_touched"]["exists_at_end"] is False,
         "%r" % (R["recipe_file_reported_not_touched"]["exists_at_end"],))

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
    fact("B1  ExecState after both deletes = %r ; created wire %r deleted by uid -> gone %r ; saved %r bytes -> %r"
         % (R["pass_criteria"]["B1"], R["B1"].get("wire_delete", {}).get("created_wire_uid"),
            R["B1"].get("wire_delete", {}).get("delete", {}).get("gone"), R["B1"].get("saved_bytes"),
            R["B1"].get("file_after", {}).get("md5")))
    fact("B2  owner_of/ExecState = %r ; saved %r bytes -> %r"
         % (R["pass_criteria"]["B2"], R["B2"].get("saved_bytes"),
            R["B2"].get("file_after", {}).get("md5")))
    fact("B3  Is Broken? = %r ; indicator wire %r -> %r ; saved %r bytes -> %r"
         % (R["pass_criteria"]["B3"], R["B3"].get("target_wire_uid", {}).get("before"),
            R["B3"].get("target_wire_uid", {}).get("after"), R["B3"].get("saved_bytes"),
            R["B3"].get("file_after", {}).get("md5")))
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
