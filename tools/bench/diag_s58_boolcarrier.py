"""diag_s58_boolcarrier - cycle 58 material #1, the FIRST ACT of STATUS `## NEXT` (Pre-decided 47(i) route 1).
A DIAGNOSTIC under tools/bench/, never a recipe. tools/recipes/stage_d1_s3a_focus_ind.py is NOT written and NOT
launched here; its on-disk presence is REPORTED only.

THE ONE QUESTION THIS RUN ANSWERS AND NOTHING ELSE:
  Which EXISTING gscript builder places a node at the TOP-LEVEL diagram whose OUTPUT terminal is BOOLEAN - such
  that an indicator created from that terminal, moved into Diagram #639 and wired to #10686 t0 'x .and. y?',
  reads `Is Broken? = False`?
Why it is the only open item: `Terminal.Create Indicator` 6349C02 takes NO type argument (47(d)), so a created
indicator inherits its CARRIER terminal's type. The carrier used so far is an unwired Index Array whose `index`
terminal is NUMERIC; wiring that to the Boolean 'x .and. y?' read `Is Broken? = True`, while the identical route
to the NUMERIC source #10757 t1 'element' read False (47(d), 35 pass / 0 fail). So the fix is a BOOLEAN-typed
carrier. THIS SCRIPT CHOOSES NO ROUTE AND INTERPRETS NOTHING.

=====================================================================================================
PHASE A - THE CENSUS (files only, written down BEFORE any call; 47(j): no reader in this fleet returns a
terminal's DATA TYPE, so a census can only PREDICT Boolean-ness and the phase-B wire test is the only instrument)

Every node-placing verb in tools/gscript.py that accepts a `diagram_index`, found by reading the file:
  build_invoke(target, cls, method_id, location, diagram_index=0)                            gscript.py:2159
      places an Invoke Node. Its output terminals are the METHOD's outputs + 'reference out' + 'error out'.
      NO method in docs/vi-server-ids.json's `methods` block returns a Boolean (they are Create Constant/
      Control/Indicator, Connect Wire, Delete, Move, Set Method, Set Properties[], Add Property Item After,
      Assign/Disconnect Terminal, Make Current Default - all void or object-returning). RANKED LAST: no
      Boolean-by-construction output terminal is nameable from the registry we own.
  build_property(target, cls, props, location, diagram_index=0)                              gscript.py:2194
      places a Property Node. A READ item's terminal is a SOURCE of THAT PROPERTY's type, so a Boolean-valued
      property gives a Boolean output terminal BY CONSTRUCTION. RANKED FIRST - and one such call is already
      VERIFIED ON THIS MACHINE (see C1).
  queue_node(kind, target, src_cls, src_index, src_name, diagram_index, location, ...)       gscript.py:1122
      places queue primitives; outputs are a queue REFNUM and an ERROR CLUSTER. Not a Boolean terminal.
      (Also: SR_QUEUE_AUTHORISED is False for good, STATUS item 38/39/41.)  NOT A CANDIDATE.
  drop_subvi(target, subvi_path, diagram_index, location)                                    gscript.py:1225
      places a subVI; a Boolean output would be whatever that VI's connector pane carries - i.e. it needs a
      donor VI chosen and its pane read first, and it adds a subVI DEPENDENCY to the deliverable.
      NOT A CANDIDATE this run (cost, and it changes the target's subVI table, which 29(g) makes an acceptance
      reference).
  loop_in(kind, target, diagram_index, location, ...)                                        gscript.py:1155
  exit_while(target, stop_control, diagram_index, ...)                                       gscript.py:1083
  exit_loop(target, node_index, output_names, diagram_index, ...)                            gscript.py:1721
      loop/structure scaffolding. A While loop's CONDITIONAL terminal is Boolean but it is a SINK, and
      `create_indicator` needs a SOURCE.  NOT CANDIDATES.
  (for completeness, the node-placing verbs that take NO diagram_index and are therefore top-level-only:
   build_index_array :2322 - the NUMERIC carrier used so far; build_case :2824; build_clfn :2699;
   while_loop :1191; for_loop :1210; loop_kernel :1804; build_kernel :2082.)

THE RANKED CANDIDATE TABLE (cheapest/most-certain first; all three are `build_property`, which is the only verb
in the fleet with a Boolean-BY-CONSTRUCTION output terminal):
  C1  build_property('VI Server:VI', [('291',False),('292',False)])   VI.Metrics:Front Panel Loaded / Block
      Diagram Loaded.  *** ALREADY VERIFIED ON THIS MACHINE, 2026-09-16 ***
      docs/vi-server-ids.json `_metrics_291_292_VERIFIED_2026-09-16`: "the node comes back with output terminals
      named 'PanelLoaded' and 'DiagramLoaded' and create_indicator labels them 'Metrics:Front Panel Loaded' /
      'Metrics:Block Diagram Loaded' ... Read-only Boolean".
      tools/bench/diag_load_vs_editmode.log:11 reads the terminal table off the machine:
        [(0,'reference',False),(1,'reference out',True),(2,'error in (no error)',False),(3,'error out',True),
         (4,'PanelLoaded',True),(5,'DiagramLoaded',True)]
      and :13-14 record create_indicator succeeding on BOTH Boolean terminals. Predicted Boolean SOURCE: t4
      'PanelLoaded'.  (47(g): this was FOUND by grepping what is already on disk, not commissioned.)
  C2  build_property('VI Server:VI', [('242',False)])                 VI.Automatic Error Handling, Boolean R/W
      docs/vi-server-ids.json "VI.Automatic Error Handling": "242"; the fleet already WRITES it through
      OpSetAutoErr_v0 (gscript.py:2617-2630), so the id resolves for this class. Its READ terminal's short name
      is NOT on disk anywhere - this run reads it off the machine. Predicted Boolean SOURCE: the one SOURCE
      terminal that is neither 'reference out' nor 'error out'.
  C3  build_property('VI Server:Wire', [('6371004',False)])           Wire.Is Broken?, "read-only bool"
      docs/vi-server-ids.json block "Wire.Is Broken? (UNVERIFIED)": class "VI Server:Wire", property 6371004,
      scope "VI Scripting, read-only bool". The PROPERTY is exercised daily inside OpConnectNested_v0/v1 and
      OpConnectFromWire_v0 (docs/d1-route-b-plan.md:342-345), but the CLASS STRING 'VI Server:Wire' is not in
      the file's `class_strings` map and has never been passed to build_property here. Predicted Boolean SOURCE:
      the one SOURCE terminal that is neither 'reference out' nor 'error out'.
  ⚠️ The registry says in writing that being listed is NOT evidence an id works
     (docs/vi-server-ids.json, "Control.Value (633200D) - TRIED AND FAILED 2026-09-12"). That is why C1, the one
     with a measured terminal table AND a measured create_indicator, is first.

THE BOOLEAN-TERMINAL SELECTION RULE, mechanical and fixed before the run: of the new node's terminals READ OFF
THE MACHINE, take the SOURCE terminals, drop any named 'reference out' or 'error out', and take the FIRST one
that remains; for C1 assert additionally that its name is the one the 2026-09-16 log recorded. The whole table
is reported either way. NO TYPE IS ASSUMED - the type is what phase B's `Is Broken?` reads.

=====================================================================================================
PHASE B - THE WIRE TEST, run on each candidate in order, up to 3 (the brief's words). Per candidate, on its OWN
dated scratch copy of claudeDev\\D1_s2_loops.vi, with EVERY index resolved LIVE (34(h), nothing cached):
  B1  place the candidate node at the TOP-LEVEL diagram (diagram_index = the LIVE diag_index(#536)); read
      owner_of (expect ('TopLevelDiagram',536)), node_info (expect 0 -> 1) and the node's full terminal table
      [(index, label, is_source, wire)] off the machine.
  B2  create_indicator(Nodes[i].Terminals[<the Boolean SOURCE terminal>]) -> the new ControlTerminal uid, the
      ControlTerminal census before/after, and the created indicator's label READ OFF THE MACHINE, never
      retyped (utf-8 hex; whether it carries a newline; whether it duplicates an existing panel label).
  B3  delete_object the carrier node -> ExecState.
      ⚠️ **RUN 2 ADDS READINGS ONLY - IT REPAIRS NOTHING AND CHANGES NO ROUTE.** Run 1
      (`tools/bench/diag_s58_boolcarrier_run1.{log,json}`, `BGRUN END rc=1 after 229s`, 51 pass / 9 fail) fired
      PREDICTED RISK (v) on ALL THREE candidates - `ExecState` 0 after the delete (run1.log:79, :158, :237) - so
      no candidate reached a legal save point and the wire test never ran. Run 1 read `ExecState` at `A BEFORE`
      (= 1) and then not again until AFTER the delete (= 0), with THREE mutations in the gap, so it could not
      say WHICH broke the VI; the cause it wrote down was an INFERENCE, and the mandatory review of that
      inference REFUTED it (`archive/peer/2026-09-21-c58-delete-execstate0.md`, claude/hypothesis opus max,
      ANSWERED, $3.6322 - RECORDED, NEITHER ACCEPTED NOR REJECTED, 41(b)). So run 2 adds **B3d**: `ExecState`,
      the whole-VI `Wire` count and the whole-VI `Wire` **uid SET** read after EACH of build_property,
      create_indicator and delete_object - three verbs already in the fleet, no new tooling, NO MUTATION, and
      exactly the per-step `ExecState` the brief's own step list asks for.
      🔴 **NO REPAIR IS ATTEMPTED.** An earlier draft of run 2 called `remove_bad_wires_scripted` after the
      delete; it was REMOVED before launching, because that is a WHOLE-VI mutation whose nearest measurement on
      this machine removed a **LoopTunnel** along with wires (`archive/2026-09-17-status-d1-route-b-2.md:45`) -
      a rule-1a hazard - and deciding to take that risk is a JUDGEMENT act, not a material one. The GUI menu
      route (`gscript.py:1629`) is likewise not called: this run performs no GUI action. Every other line is
      run 1's, unchanged.
  B4  move_in(<ct uid> -> Diagram #639 at its LIVE Traverse index, (120,4000)) -> error column, owner_of
      before/after, ControlTerminal census, panel rows, ExecState; the junk `Invoke` uid it leaves is purged
      IN-RUN (PREDICTED RISK (i)).
  B5  🔴 SAVE HERE - 47(e): the save goes at the last point the VI is measured legal, BEFORE any wiring. Dated
      artefact under claudeDev; md5 + byte size + LV version bytes logged. allow_broken stays False; gui_save is
      never called. ExecState != 1 => NO SAVE, said plainly, and this candidate stops here.
  B6  the wiring copy is a BYTE COPY of B5's artefact under a second dated name (gscript has no save-as verb,
      gscript.py:2062), opened in a RESTARTED LabVIEW so it loads COLD from disk; then
      wire_indicators(... -> #10686 t0 'x .and. y?', wire 10799, diagram_index = the LIVE index of the diagram
      the INDICATOR's terminal lives on, i.e. #639) - 47(b): gscript.py:1787-1789 scopes the indicator lookup,
      never the source. Reported: the error column VERBATIM, the target's wire uid before/after, the whole-VI
      `Wire` count delta, #10686's wired-terminal count before and after, and #637's terminal/wired counts
      before and after (37(e): any tunnel or border object appearing is a FINDING).
  B7  the ORDERED SECOND PASS (42(b)), AFTER the save: an idempotent re-connect of an EXISTING net on the same
      diagram (wire_delta expected 0), then `Wire.Is Broken?` (6371004) read on the new wire uid.
  B8  if ExecState == 1 after the wiring, a second dated artefact is saved and its md5 logged.

PHASE C - one PURE MEASUREMENT, no action: guard_cycle.py is dry-run against a HYPOTHETICAL recipe build of
tools/recipes/stage_d1_s3a_focus_ind.py by feeding it the PreToolUse payload it reads on stdin
(guard_cycle.py:534-541) in a subprocess, and its exit code + stderr are reported VERBATIM. NO DATE IS EDITED,
CYCLE_GUARD_OFF IS NEVER SET, THE GATE IS NOT "FIXED".

PREDICTION CONTRACT (every line is a printed GATE and every gate is the readback of a CALL to the machine,
46(g); phase A and phase C are FACTS, not gates - A reads files and C reads a hook's exit code):
  T1    the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                        (FATAL)
  T1b   claudeDev\\D1_s1_copy.vi md5 == 3e3d23cefd3a334001aa9d6156bf1aee
  T2    claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                              (FATAL)
  <cid>T3   the candidate's scratch is byte-identical to D1_s2_loops.vi at creation
  <cid>A1   diag_index(#639) resolves to an int
  <cid>A2   diag_index(#536) resolves to 0
  <cid>A3   owner_of(#10686) answers ('Diagram', 639)
  <cid>A4   #10686 carries terminal 0, a SOURCE, whose name and wire uid are read off the machine
  <cid>B1   build_property put exactly 1 new Property on the target, owner ('TopLevelDiagram', 536)
  <cid>B1b  node_info(max_n=40) goes 0 entries -> 1 entry
  <cid>B1c  the new node's terminal table holds a SOURCE terminal that is not reference out / error out
  <cid>B2   create_indicator returned a ControlTerminal and the census went n -> n+1
  <cid>B2b  exactly ONE new front-panel row appeared and its label was READ off the machine (never retyped)
  <cid>B3   delete_object removed exactly 1 object
  <cid>B3b  ExecState after the delete == 1                     (run 1 measured 0 on all three - PREDICTED RISK v)
  <cid>B3d  the ExecState 1 -> 0 transition is attributed to ONE named mutation by DIRECT READING (run 2's only
        addition: reads, never a repair)
  <cid>B4   move_in returned without raising
  <cid>B4b  owner_of(new uid) reads ('Diagram', 639) AFTER the move                          (the EFFECT gate)
  <cid>B4c  the ControlTerminal census is unchanged across the move
  <cid>B4d  ExecState after the move (and the junk purge) == 1
  <cid>B5   ExecState == 1 at the save point and g.save() returned a byte count  (a 0 here STOPS this candidate
                                                                                 and is a LEGITIMATE outcome)
  <cid>B5b  the artefact is on disk and its version bytes read 26 00 80 00 (LV2026)
  <cid>B6   the COLD reopen of that artefact reads ExecState 1
  <cid>B6b  wire_indicators returned an EMPTY error column        (a RAISE is a LEGITIMATE reading, 47(d)/RISK iii)
  <cid>B6c  the new indicator's wire uid changed from 0                                      (the EFFECT gate)
  <cid>B6d  #10686's wired-terminal count is unchanged across the wiring                              (37(e))
  <cid>B6e  #637's terminal count is unchanged - NO tunnel or border object appeared                  (37(e))
  <cid>B7   the ORDERED second-pass `Is Broken?` read returned a boolean   (True is a LEGITIMATE reading - it is
                                                                            the answer to the run's question)
  <cid>B8   ExecState == 1 at the second save point and g.save() returned a byte count  (a 0 is LEGITIMATE; the
                                                                                        B5 artefact still stands)
  Z1    ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 unchanged after everything
  Z2    refs opened == closed, 0 live

STOP DISCIPLINE: a step whose own precondition is unmet stops THAT CANDIDATE, records why, and the run moves to
the next candidate. No step is retried; no verb is looped over indices (<= 1 attempt per verb per candidate).
DEADLINE GUARD, fixed before the run: a candidate is STARTED only while elapsed < 16 min of the 25-min bgrun
budget; later candidates are recorded NOT ATTEMPTED with the elapsed time, so the log always reaches its closing
facts instead of being killed at the deadline.

PREDICTED RISKS, written down BEFORE the run so none is an unpredicted result:
  (i)   `move_in` leaves JUNK `Invoke` node(s) - the uid the deleted carrier released (measured twice:
        probe_move_ctlterm_v0.log:135; cycle 57 dispatches 3 and 4). Recorded, then purged exactly as
        tools/recipes/build_d1_routeb_v0.py:1279-1287 does; the set is `after - before`, so nothing pre-existing
        can be touched.
  (ii)  Nodes[] and Traverse indices SHIFT when an object is added to or removed from a diagram (34(h)). Every
        index is re-resolved by uid readback immediately before use - including after the cold reload - and the
        historical pins (46 / 25 / 4 / 102) are a first guess that must survive a uid echo.
  (iii) `wire_indicators` RAISES when the target reads ExecState != 1 after the connection (gscript.py:1794-1797)
        even though the connection WAS made. The text is captured VERBATIM and the candidate continues to B7/B8,
        exactly as cycle 57 dispatch 3 did. For a MISMATCHED carrier this is the EXPECTED reading.
  (iv)  `build_property` RAISES `creator refused - error 1077` when the property id is not a member of the class
        (gscript.py:2221-2223). For C2/C3 that is a real possibility and is a RECORDED outcome, not a failure to
        work around: the candidate stops and the next one starts.
  (v)   Deleting the carrier Property node may leave the created indicator without a source and the VI at
        ExecState 0. Cycle 57 measured the Index Array carrier returning to ExecState 1 after its delete; the
        Property carrier has never been deleted here. B3b reads it rather than assuming it.

BOUNDS: NO VI IS RUN (34(f)). NO NEW OP VI (route 2 of 47(i) is a later judgement call, not this run's). No new
process device (user, 2026-09-18 08:53). NO RECIPE - tools/recipes/stage_d1_s3a_focus_ind.py must still not
exist on disk when this finishes, and that is asserted and reported at both ends. No GUI action. No motor / ASI
/ camera (rig 조립 / ASSEMBLED). Originals are never opened for write; `allow_broken` stays False and `gui_save`
is NEVER called. `Is Broken?` is read ONLY in a separate, ordered second pass and only AFTER the save attempt
(docs/NAMES.md:912-918). NOTHING SAVED IS EVER DELETED. NO ROUTE IS RECOMMENDED - that is judgement's call.

WHAT ALREADY EXISTED (checked before a line of this was written, per the material brief and 47(g)):
  * tools/gscript.py - read end to end for the `diagram_index` verb census above; no new verb was added.
  * docs/vi-server-ids.json - where C1's VERIFIED Boolean property pair was found already on disk.
  * tools/bench/diag_load_vs_editmode.log:11,13-14 - the measured terminal table and the two successful
    create_indicator calls on those Boolean terminals. Nothing about them was re-measured on files.
  * tools/bench/diag_s57_typepair.py - cycle 57 dispatch 4's file; this run reuses its helpers, gate shape,
    scratch protocol and phase-I ordered-pass construction verbatim rather than inventing new ones.
  * tools/recipes/stage_d1_s3a_focus_ind.py - checked on disk; REPORTED, never written, never launched.
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
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
OUT = os.path.join(HERE, "diag_s58_boolcarrier.json")
RECIPE_PATH = os.path.join(ROOT, "tools", "recipes", "stage_d1_s3a_focus_ind.py")
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

D639 = 639                      # the frame-loop BODY diagram (nested); owner WhileLoop #637
D536 = 536                      # the TopLevelDiagram (47(a); cycle 57 re-measured diag_index -> 0)
D686 = 686                      # the FlatSequenceFrame diagram that owns #637
LOOP11_UID = 637                # While loop 1.1 - the 37(e) tunnel/border witness
LOOP11_NODES_PIN = 4            # historical Nodes[] index of #637 on Diagram #686 - never trusted without an echo
BOOL_SRC_UID = 10686            # THE BOOLEAN SINK OF THE QUESTION: 'And', t0 'x .and. y?', wire 10799
BOOL_TERM_INDEX = 0             # the terminal 47(d) names; its NAME is read off the machine, never retyped
BOOL_WIRE_PIN = 10799           # the wire cycle 57 recorded there - a PIN, re-measured every time
BOOL_NODES_PIN = 25             # cycle 56 read #10686 at Nodes[] index 25 of a 73-node walk on #639
NODE_LOCATION = (6200, 5200)    # far from every existing object; the carrier is deleted again in the same phase
MOVE_POSITION = (120, 4000)     # a position INSIDE Diagram #639; overlap is cosmetic, never functional
SCAN_LIMIT = 80                 # the bounded Nodes[] scan used when a pinned index fails its uid echo
START_NEW_CANDIDATE_BEFORE_S = 16 * 60     # the DEADLINE GUARD (bgrun budget is 25 min)
NON_VALUE_SOURCE_TERMS = ("reference out", "error out")
CLASS_CANDIDATES = ("Function", "IndexArray", "SubVI", "Property", "Invoke", "CaseStructure", "WhileLoop",
                    "ForLoop", "Sequence", "EventStructure", "Constant", "LoopTunnel", "ControlTerminal")

# ---------------------------------------------------------------- THE RANKED CANDIDATES (phase A's output)
CANDIDATES = [
    {"cid": "C1", "verb": "build_property", "cls": "VI Server:VI",
     "props": [("291", False), ("292", False)],
     "node_class": "Property",
     "what": "VI.Metrics:Front Panel Loaded (291) + Block Diagram Loaded (292), read-only Boolean",
     "predicted_bool_term_name": "PanelLoaded",
     "citation": "docs/vi-server-ids.json `_metrics_291_292_VERIFIED_2026-09-16` (VERIFIED ON THIS MACHINE); "
                 "tools/bench/diag_load_vs_editmode.log:11 (the terminal table read off the machine) and "
                 ":13-14 (create_indicator succeeded on BOTH Boolean terminals)"},
    {"cid": "C2", "verb": "build_property", "cls": "VI Server:VI",
     "props": [("242", False)],
     "node_class": "Property",
     "what": "VI.Automatic Error Handling (242), Boolean R/W",
     "predicted_bool_term_name": None,
     "citation": "docs/vi-server-ids.json \"VI.Automatic Error Handling\": \"242\"; the fleet already WRITES it "
                 "through OpSetAutoErr_v0 (tools/gscript.py:2617-2630), so the id resolves for this class. Its "
                 "READ terminal's short name is on no file here and is read off the machine."},
    {"cid": "C3", "verb": "build_property", "cls": "VI Server:Wire",
     "props": [("6371004", False)],
     "node_class": "Property",
     "what": "Wire.Is Broken? (6371004), \"VI Scripting, read-only bool\"",
     "predicted_bool_term_name": None,
     "citation": "docs/vi-server-ids.json block \"Wire.Is Broken? (UNVERIFIED)\" (class \"VI Server:Wire\"). The "
                 "PROPERTY is exercised daily inside OpConnectNested_v0/v1 and OpConnectFromWire_v0 "
                 "(docs/d1-route-b-plan.md:342-345); the CLASS STRING has never been passed to build_property."},
]

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "question": "cycle 58 material #1 (47(i) route 1): which EXISTING gscript builder places a node at the "
                 "TOP-LEVEL diagram whose OUTPUT terminal is BOOLEAN, such that an indicator created from it, "
                 "moved into Diagram #639 and wired to #10686 t0 'x .and. y?', reads Is Broken? = False?",
     "chooses_no_route": True, "recommends_no_route": True, "interprets_nothing": True,
     "no_vi_was_run": True, "no_new_op": True, "no_new_device": True, "no_gui_action": True, "no_recipe": True,
     "edits_no_plan_document": True, "edits_no_date": True, "cycle_guard_off_never_set": True,
     "rig_state": "조립 / ASSEMBLED (motors + ASI forbidden; camera not needed and not touched)",
     "recipe_file_reported_not_touched": {
         "path": "tools/recipes/stage_d1_s3a_focus_ind.py",
         "exists_at_start": os.path.exists(RECIPE_PATH), "exists_at_end": None, "mtime": None,
         "note": "stop-recorded by archive/peer/2026-09-20-priorart-d1-s3a-focus-ind.md. REPORTED ONLY - not "
                 "written, not launched, and phase C only DRY-RUNS the gate against it."},
     "phaseA_census": {
         "rule": "every node-placing verb in tools/gscript.py that accepts a `diagram_index`, read off the file; "
                 "ranked by whether it has an output terminal that is Boolean BY CONSTRUCTION. 47(j): no reader "
                 "in this fleet returns a terminal's data type, so this ranking PREDICTS and phase B MEASURES.",
         "verbs": [
             {"verb": "build_property", "site": "tools/gscript.py:2194",
              "signature": "build_property(target, cls, props, location, diagram_index=0)",
              "places": "Property Node",
              "boolean_output_by_construction": "YES when the property READ is Boolean-valued - a read item's "
                                                "terminal is a SOURCE of that property's type",
              "rank": 1},
             {"verb": "build_invoke", "site": "tools/gscript.py:2159",
              "signature": "build_invoke(target, cls, method_id, location, diagram_index=0)",
              "places": "Invoke Node",
              "boolean_output_by_construction": "NO Boolean-returning method is nameable from "
                                                "docs/vi-server-ids.json's `methods` block (all void or "
                                                "object-returning)",
              "rank": 4},
             {"verb": "drop_subvi", "site": "tools/gscript.py:1225",
              "signature": "drop_subvi(target, subvi_path, diagram_index, location)",
              "places": "a subVI node",
              "boolean_output_by_construction": "ONLY if a donor VI with a Boolean output is chosen and its "
                                                "connector pane read first; it also adds a subVI DEPENDENCY to "
                                                "the deliverable (29(g) makes the SubVI table an acceptance "
                                                "reference). NOT A CANDIDATE this run.",
              "rank": 5},
             {"verb": "queue_node", "site": "tools/gscript.py:1122",
              "signature": "queue_node(kind, target, src_cls, src_index, src_name, diagram_index, location, ...)",
              "places": "queue primitives",
              "boolean_output_by_construction": "NO - outputs are a queue REFNUM and an ERROR CLUSTER",
              "rank": 6},
             {"verb": "loop_in", "site": "tools/gscript.py:1155",
              "signature": "loop_in(kind, target, diagram_index, location, ...)",
              "places": "a While/For loop",
              "boolean_output_by_construction": "NO - the conditional terminal IS Boolean but it is a SINK, and "
                                                "create_indicator needs a SOURCE",
              "rank": 7},
             {"verb": "exit_while", "site": "tools/gscript.py:1083",
              "signature": "exit_while(target, stop_control, diagram_index, node_index=0, output_names=(), ...)",
              "places": "loop-exit scaffolding", "boolean_output_by_construction": "NO (same reason)", "rank": 8},
             {"verb": "exit_loop", "site": "tools/gscript.py:1721",
              "signature": "exit_loop(target, node_index, output_names, diagram_index, node_class='SubVI')",
              "places": "loop-exit scaffolding", "boolean_output_by_construction": "NO (same reason)", "rank": 9},
         ],
         "top_level_only_verbs_no_diagram_index": [
             "build_index_array :2322 (the NUMERIC carrier used so far)", "build_case :2824", "build_clfn :2699",
             "while_loop :1191", "for_loop :1210", "loop_kernel :1804", "build_kernel :2082"],
         "candidates": [{k: v for k, v in c.items()} for c in CANDIDATES],
         "boolean_terminal_selection_rule":
             "of the new node's terminals READ OFF THE MACHINE, take the SOURCE terminals, drop any named "
             "'reference out' or 'error out', take the FIRST that remains; for C1 additionally assert its name "
             "equals the one the 2026-09-16 log recorded. NO TYPE IS ASSUMED.",
         "prior_art_grep_note":
             "47(g): the Boolean property pair was FOUND already on disk (docs/vi-server-ids.json + "
             "tools/bench/diag_load_vs_editmode.log) rather than commissioned as a new read."},
     "citations": {"create_route": "Pre-decided 46(a) / 47(a)",
                   "carrier_type_is_inherited": "Pre-decided 47(d) - Terminal.Create Indicator 6349C02 takes no "
                                                "type argument",
                   "no_type_reader_exists": "Pre-decided 47(j)",
                   "wire_indicators_scopes_the_indicator": "Pre-decided 47(b); tools/gscript.py:1787-1789",
                   "save_before_wiring": "Pre-decided 47(e)",
                   "move_in_owner_of_diag_index": "tools/recipes/build_d1_v0.py:318,:338,:357",
                   "junk_invoke_purge": "tools/recipes/build_d1_routeb_v0.py:1279-1287",
                   "is_broken": "docs/NAMES.md:902-911", "ordered_second_pass": "Pre-decided 42(b)",
                   "index_shift_after_mutation": "34(h)",
                   "branch_adds_no_wire_object": "tools/gscript.py:1771-1772",
                   "wire_indicators_raises_on_break": "tools/gscript.py:1794-1797",
                   "build_property_creator_error": "tools/gscript.py:2221-2223",
                   "no_save_as_verb": "tools/gscript.py:2062 (save persists to the target's OWN path)",
                   "gate_must_make_a_call": "Pre-decided 46(g)",
                   "guard_cycle_stdin_contract": "tools/hooks/guard_cycle.py:534-541"},
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "handles": {}, "hash_probe": [], "candidates": {}, "phaseC": {}, "artefacts": []}

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
    # `FAIL`, NOT `**FAIL**` - the documented emitter (37(i)); the bold form is invisible to guard_peer.
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
    """owner_of with the strict identity-echo guard first, then non-strict - the answer either way is REPORTED."""
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
    """The 34(h)-safe Nodes[] index: try the historical PIN and accept it ONLY if the uid echoes back; otherwise
    a BOUNDED scan. Returns (index or None, how it was resolved, the rows at that index)."""
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
    """Which live Traverse class list(s) hold this uid, and at what index in each. Pure measurement; every class
    that RAISES is recorded verbatim (FlatSequence has been refused with error 1092 before)."""
    rows, errs = [], {}
    for cls in CLASS_CANDIDATES:
        try:
            uids = [o["uid"] for o in g.report_all(target, cls)]
        except Exception as e:                                                     # noqa: BLE001
            errs[cls] = "%s: %s" % (type(e).__name__, str(e)[:160])
            continue
        if uid in uids:
            rows.append({"class": cls, "index": uids.index(uid), "members": len(uids)})
    return rows, errs


def close_quietly(target):
    try:
        g.close_panel(target)
    except Exception as e:                                                         # noqa: BLE001
        fact("close_panel(%s) raised %s: %s" % (os.path.basename(target), type(e).__name__, e))


def op_indicators():
    """OpConnectNested_v1's own readouts, re-read AFTER a run (g.op caches the reference)."""
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


def pick_bool_terminal(rows, predicted_name):
    """THE SELECTION RULE, fixed before the run (see the docstring). Returns (row or None, how)."""
    sources = [r for r in rows if r.get("is_source")]
    valued = [r for r in sources if r.get("name") not in NON_VALUE_SOURCE_TERMS]
    if not valued:
        return None, ("no SOURCE terminal outside %r; sources were %r"
                      % (list(NON_VALUE_SOURCE_TERMS), [r.get("name") for r in sources]))
    chosen = valued[0]
    how = ("first SOURCE terminal that is not %r; the candidates were %r"
           % (list(NON_VALUE_SOURCE_TERMS), [r.get("name") for r in valued]))
    if predicted_name is not None:
        how += ("; the 2026-09-16 log predicted %r and the machine read %r -> %s"
                % (predicted_name, chosen.get("name"),
                   "MATCH" if chosen.get("name") == predicted_name else "DIFFERENT (reported, not corrected)"))
    return chosen, how


# ============================================================ STAGE 1 for one candidate: B1..B5, on PLACED
def stage1(K, target, cand):
    """B1 place -> B2 create_indicator -> B3 delete the carrier -> B4 move_in -> B5 SAVE (47(e)).
    Returns the carry dict, or raises Stop with the reason this candidate goes no further."""
    cid = cand["cid"]

    # ------------------------------------------------------------------ resolve LIVE, assume nothing (34(h))
    print("\n--------- %s A  (resolve LIVE; assume nothing, 34(h))" % cid, flush=True)
    census(K, "A before everything", target)
    read_exec_state(K, "A BEFORE", target)
    A = K.setdefault("A", {})
    for uid, key in ((D639, "diag_index_639"), (D536, "diag_index_536"), (D686, "diag_index_686")):
        try:
            A[key] = diag_index(target, uid)
            A[key + "_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            A[key] = None
            A[key + "_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s A diag_index(#%d) = %r ; error VERBATIM %r" % (cid, uid, A[key], A[key + "_error_verbatim"]))
    d639, d536, d686 = A["diag_index_639"], A["diag_index_536"], A["diag_index_686"]
    gate("%s A1 diag_index(#639) resolves to an int" % cid, isinstance(d639, int),
         "%r (the historical 43 / 46 are NOT reused)" % (d639,))
    gate("%s A2 diag_index(#536) resolves to 0" % cid, d536 == 0, "%r" % (d536,))
    if not isinstance(d639, int) or not isinstance(d536, int):
        raise Stop("%s: diag_index(#639)=%r / diag_index(#536)=%r did not resolve, so there is no destination "
                   "diagram and no top-level diagram to place a carrier on." % (cid, d639, d536))

    A["owner_of_10686"] = owner_read(K, "%s A3 owner of the BOOLEAN sink #10686" % cid, BOOL_SRC_UID, target)
    gate("%s A3 owner_of(#10686) answers ('Diagram', 639)" % cid,
         (A["owner_of_10686"].get("owner_class"), A["owner_of_10686"].get("owner_uid")) == ("Diagram", D639),
         "(%r, %r)" % (A["owner_of_10686"].get("owner_class"), A["owner_of_10686"].get("owner_uid")))
    rows_m, errs_m = class_membership(target, BOOL_SRC_UID)
    A["class_membership_10686"] = rows_m
    A["class_scan_errors_verbatim"] = errs_m
    fact("%s A #%d's LIVE Traverse class membership: %r (classes that RAISED: %r)"
         % (cid, BOOL_SRC_UID, rows_m, errs_m))
    bool_terms = wired_counts(K, "%s A4 the BOOLEAN sink #%d" % (cid, BOOL_SRC_UID), target, d639, BOOL_SRC_UID,
                              BOOL_NODES_PIN)
    A["bool_source_terminals"] = bool_terms
    bt = next((t for t in bool_terms.get("terms", []) if t["i"] == BOOL_TERM_INDEX), None)
    A["bool_terminal"] = bt
    fact("%s A4 #%d's FULL terminal list: %r" % (cid, BOOL_SRC_UID, bool_terms.get("terms")))
    fact("%s A4 terminal %d READ off the machine: %r (utf-8 hex %r); the 47(d) wire PIN is %r"
         % (cid, BOOL_TERM_INDEX, bt, (bt or {}).get("name", "").encode("utf-8").hex(), BOOL_WIRE_PIN))
    gate("%s A4 #10686 carries terminal 0, a SOURCE, whose name and wire uid were read off the machine" % cid,
         bool(bt) and bool(bt.get("is_source")) and bool(bt.get("wire")),
         "%r (wire pin %r)" % (bt, BOOL_WIRE_PIN))
    if not bt or not bt.get("is_source"):
        raise Stop("%s: #%d has no SOURCE terminal at index %d on Diagram #%d, so there is nothing to wire to."
                   % (cid, BOOL_SRC_UID, BOOL_TERM_INDEX, D639))

    # ------------------------------------------------------------------ B1: place the candidate carrier
    print("\n--------- %s B1  (place the candidate node at the TOP-LEVEL diagram)" % cid, flush=True)
    B = K.setdefault("B1", {})
    rows_before = panel_rows(target)
    fpl_before = fp_label_list(target)
    ct_before = g.count(target, "ControlTerminal")
    B["panel_rows_before"] = len(rows_before)
    B["fp_labels_before"] = len(fpl_before)
    B["control_terminal_before"] = ct_before
    # the B3d baseline: ExecState + Wire count + Wire uid SET before ANY of this candidate's mutations
    B["exec_state_baseline"] = read_exec_state(K, "%s B1 BASELINE, before any mutation" % cid, target)
    B["wire_count_baseline"] = g.count(target, "Wire")
    try:
        B["wire_uids_baseline"] = sorted(g.uids(target, "Wire"))
    except Exception as e:                                                         # noqa: BLE001
        B["wire_uids_baseline"] = []
        fact("%s B1 uids(Wire) BASELINE raised %s: %s" % (cid, type(e).__name__, str(e)[:140]))
    fact("%s B1 BEFORE: panel_wiring rows %r, fp_labels %r, ControlTerminal census %r"
         % (cid, len(rows_before), len(fpl_before), ct_before))
    try:
        top0 = g.node_info(target, max_n=40)
        B["node_info_before_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        top0 = None
        B["node_info_before_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    B["node_info_before"] = top0
    fact("%s B1 node_info(max_n=40) BEFORE: %r entries -> %r ; error VERBATIM %r"
         % (cid, len(top0) if isinstance(top0, list) else top0, top0, B["node_info_before_error_verbatim"]))

    node_cls = cand["node_class"]
    try:
        pre_uids = set(g.uids(target, node_cls))
    except Exception as e:                                                         # noqa: BLE001
        pre_uids = set()
        fact("%s B1 uids(%s) BEFORE raised %s: %s" % (cid, node_cls, type(e).__name__, str(e)[:140]))
    B["carrier_class_uids_before"] = len(pre_uids)
    new_node, pl_err = None, None
    try:
        new_node = g.build_property(target, cand["cls"], cand["props"], NODE_LOCATION, diagram_index=d536)
        pl_err = ""
    except Exception as e:                                                         # noqa: BLE001
        pl_err = "%s: %s" % (type(e).__name__, str(e)[:600])
    B["call"] = ("build_property(target, %r, %r, %r, diagram_index=%r)"
                 % (cand["cls"], cand["props"], NODE_LOCATION, d536))
    B["new"] = new_node
    B["error_verbatim"] = pl_err
    fact("%s B1 %s -> new %r ; error VERBATIM %r" % (cid, B["call"], new_node, pl_err))
    node_uid = (new_node[0]["uid"] if isinstance(new_node, list) and new_node else None)
    node_owner = owner_read(K, "%s B1 the new carrier's owner" % cid, node_uid, target) if node_uid else {}
    B["carrier_owner"] = node_owner
    gate("%s B1 build_property put 1 new %s on the target, owner ('TopLevelDiagram', 536)" % (cid, node_cls),
         isinstance(new_node, list) and len(new_node) == 1
         and (node_owner.get("owner_class"), node_owner.get("owner_uid")) == ("TopLevelDiagram", D536),
         "new %r, owner (%r, %r), error %r"
         % (new_node, node_owner.get("owner_class"), node_owner.get("owner_uid"), pl_err))
    if node_uid is None:
        raise Stop("%s: the builder placed no node (error VERBATIM %r), so there is no carrier - PREDICTED "
                   "RISK (iv) if this is a creator 1077." % (cid, pl_err))

    try:
        top1 = g.node_info(target, max_n=40)
        B["node_info_after_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        top1 = None
        B["node_info_after_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    B["node_info_after"] = top1
    fact("%s B1 node_info(max_n=40) AFTER (create_indicator's OWN ladder): %r entries -> %r ; error VERBATIM %r"
         % (cid, len(top1) if isinstance(top1, list) else top1, top1, B["node_info_after_error_verbatim"]))
    gate("%s B1b node_info goes 0 entries -> 1 entry" % cid,
         isinstance(top0, list) and len(top0) == 0 and isinstance(top1, list) and len(top1) == 1,
         "%r -> %r" % (len(top0) if isinstance(top0, list) else top0,
                       len(top1) if isinstance(top1, list) else top1))
    node_i = (top1[-1][0] if isinstance(top1, list) and top1 else None)
    B["node_index"] = node_i

    # THE CARRIER'S TERMINAL TABLE, READ OFF THE MACHINE
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
    fact("%s B1 THE CARRIER'S TERMINAL TABLE [(index, label, is_source, wire)], READ OFF THE MACHINE: %r "
         "(uid echo %r; error VERBATIM %r)" % (cid, tt, B.get("node_uid_echo"), tt_err))
    B["exec_state_after_place"] = read_exec_state(K, "%s B1 after build_property placed the carrier" % cid,
                                                  target)
    B["wire_count_after_place"] = g.count(target, "Wire")
    bool_row, how = pick_bool_terminal(tt, cand["predicted_bool_term_name"])
    B["chosen_terminal"] = bool_row
    B["chosen_rule"] = how
    fact("%s B1 the terminal create_indicator will be called on: %r  (rule: %s)" % (cid, bool_row, how))
    gate("%s B1c the terminal table holds a SOURCE terminal that is not reference out / error out" % cid,
         bool(bool_row), "%r (%s)" % (bool_row, how))
    if bool_row is None:
        raise Stop("%s: the carrier exposes no value-carrying SOURCE terminal (%s), so create_indicator has no "
                   "carrier terminal." % (cid, how))

    # ------------------------------------------------------------------ B2: create the indicator
    print("\n--------- %s B2  (create_indicator on that terminal; 6349C02 takes NO type argument, 47(d))" % cid,
          flush=True)
    B2 = K.setdefault("B2", {})
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
    fact("%s B2 create_indicator(Nodes[%r].Terminals[%r] = %r) -> new %r ; error VERBATIM %r"
         % (cid, node_i, bool_row["i"], bool_row["name"], new_ct, ci_err))
    gate("%s B2 create_indicator returned a ControlTerminal and the census went %r -> %r"
         % (cid, ct_before, ct_after),
         isinstance(new_ct_uid, int) and isinstance(ct_before, int) and ct_after == ct_before + 1,
         "new uid %r, census %r -> %r, error %r" % (new_ct_uid, ct_before, ct_after, ci_err))
    if not isinstance(new_ct_uid, int):
        raise Stop("%s: create_indicator returned no ControlTerminal uid (error VERBATIM %r), so there is "
                   "nothing to move." % (cid, ci_err))

    B2["exec_state_after_create"] = read_exec_state(K, "%s B2 after create_indicator" % cid, target)
    B2["wire_count_after_create"] = g.count(target, "Wire")
    try:
        B2["wire_uids_after_create"] = sorted(g.uids(target, "Wire"))
    except Exception as e:                                                         # noqa: BLE001
        B2["wire_uids_after_create"] = []
        fact("%s B2 uids(Wire) AFTER create raised %s: %s" % (cid, type(e).__name__, str(e)[:140]))

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
    fact("%s B2 THE LABEL, VERBATIM: %r  (utf-8 hex %r, source: %s)"
         % (cid, label, B2["label_utf8_hex"], label_source))
    fact("%s B2 contains a NEWLINE: %r ; is a DUPLICATE of an existing panel label: %r"
         % (cid, B2["label_contains_newline"], B2["label_is_duplicate_of_an_existing_panel_label"]))
    fact("%s B2 panel_wiring rows %r -> %r, fp_labels %r -> %r ; the NEW row(s) %r"
         % (cid, len(rows_before), len(rows_after), len(fpl_before), len(fpl_after), new_rows))
    gate("%s B2b exactly ONE new front-panel row appeared and its label was READ off the machine" % cid,
         (len(new_rows) == 1 or (not new_rows and len(new_fp) == 1)) and label is not None,
         "%r new panel row(s), %r new fp_labels entr(y/ies), label %r" % (len(new_rows), len(new_fp), label))
    if label is None:
        raise Stop("%s: the indicator's label could not be READ off the machine, and a label is never retyped - "
                   "wire_indicators would have no byte-exact name to pass." % cid)

    # ------------------------------------------------------------------ B3: delete the carrier
    print("\n--------- %s B3  (delete the carrier node; PREDICTED RISK (v))" % cid, flush=True)
    B3 = K.setdefault("B3", {})
    gone, del_err = None, None
    try:
        cur = [o["uid"] for o in g.report_all(target, node_cls)]
        B3["carrier_traverse_index_at_delete"] = cur.index(node_uid)
        gone = g.delete_object(target, node_cls, cur.index(node_uid))
        del_err = ""
    except Exception as e:                                                         # noqa: BLE001
        del_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    B3["gone"] = sorted(gone) if gone else gone
    B3["error_verbatim"] = del_err
    fact("%s B3 delete_object(%s[%r]) -> gone %r ; error VERBATIM %r"
         % (cid, node_cls, B3.get("carrier_traverse_index_at_delete"), B3["gone"], del_err))
    gate("%s B3 delete_object removed exactly 1 object" % cid, bool(gone) and len(gone) == 1,
         "%r (error %r)" % (B3["gone"], del_err))
    es_del = read_exec_state(K, "%s B3 after delete_object" % cid, target)
    B3["exec_state_after_delete"] = es_del
    gate("%s B3b ExecState after the delete == 1" % cid, es_del == 1, "%r (PREDICTED RISK (v))" % (es_del,))

    # ---- B3d: WHICH of the three mutations takes the VI from ExecState 1 to 0. PURE READING, NO MUTATION.
    # Run 1 read ExecState at `A BEFORE` = 1 and then not again until AFTER the delete = 0, with THREE mutations
    # in the gap (build_property, create_indicator, delete_object), so it could not say which one broke the VI -
    # and the cause it wrote down was an INFERENCE. The brief's step list already asks for ExecState to be
    # reported at each of those steps; run 1 simply under-instrumented it. The snapshots below close that gap
    # with `g.exec_state`, `g.count(target,"Wire")` and `set(g.uids(target,"Wire"))` - three verbs already in
    # the fleet, no new tooling, no mutation of any kind, seconds. NO REPAIR IS ATTEMPTED: in particular
    # `remove_bad_wires_scripted` is NOT called (an earlier draft of this run did call it; that was removed
    # because it is a WHOLE-VI mutation whose nearest measurement on this machine removed a LoopTunnel as well
    # as wires - archive/2026-09-17-status-d1-route-b-2.md:45 - which is a rule-1a hazard, and deciding to take
    # that risk is a JUDGEMENT act, not a material one). Neither is the GUI route at gscript.py:1629.
    B3["what_broke_it"] = {
        "method": "ExecState + whole-VI Wire count + Wire uid SET, read after each of the three mutations; the "
                  "uid SET is taken because a count cannot name which wire went (and cannot see a tunnel).",
        "no_repair_attempted": "remove_bad_wires_scripted NOT called; remove_bad_wires (GUI menu) NOT called; "
                               "nothing was mutated to make the VI legal.",
        "exec_state": {"baseline_before_B1": K.get("B1", {}).get("exec_state_baseline"),
                       "after_B1_place": K.get("B1", {}).get("exec_state_after_place"),
                       "after_B2_create_indicator": K.get("B2", {}).get("exec_state_after_create"),
                       "after_B3_delete": es_del},
        "wire_count": {"baseline_before_B1": K.get("B1", {}).get("wire_count_baseline"),
                       "after_B1_place": K.get("B1", {}).get("wire_count_after_place"),
                       "after_B2_create_indicator": K.get("B2", {}).get("wire_count_after_create"),
                       "after_B3_delete": g.count(target, "Wire")}}
    try:
        u_now = set(g.uids(target, "Wire"))
    except Exception as e:                                                         # noqa: BLE001
        u_now = set()
        fact("%s B3d uids(Wire) AFTER the delete raised %s: %s" % (cid, type(e).__name__, str(e)[:140]))
    u_b2 = set(K.get("B2", {}).get("wire_uids_after_create") or [])
    u_b0 = set(K.get("B1", {}).get("wire_uids_baseline") or [])
    B3["what_broke_it"]["wire_uids"] = {
        "added_by_B2_create_indicator": sorted(u_b2 - u_b0),
        "removed_by_B3_delete": sorted(u_b2 - u_now),
        "still_alive_after_B3_delete_that_B2_added": sorted((u_b2 - u_b0) & u_now),
        "removed_by_B3_that_predate_B2": sorted((u_b0 - u_now))}
    ex = B3["what_broke_it"]["exec_state"]
    wc = B3["what_broke_it"]["wire_count"]
    fact("%s B3d WHICH MUTATION BROKE IT - ExecState %r (baseline) -> %r (after build_property) -> %r (after "
         "create_indicator) -> %r (after delete_object)"
         % (cid, ex["baseline_before_B1"], ex["after_B1_place"], ex["after_B2_create_indicator"],
            ex["after_B3_delete"]))
    fact("%s B3d whole-VI Wire count %r -> %r -> %r -> %r ; wire uids ADDED by create_indicator %r ; REMOVED by "
         "the delete %r ; created-wire uids STILL ALIVE after the delete %r ; PRE-EXISTING wire uids removed by "
         "the delete %r"
         % (cid, wc["baseline_before_B1"], wc["after_B1_place"], wc["after_B2_create_indicator"],
            wc["after_B3_delete"], B3["what_broke_it"]["wire_uids"]["added_by_B2_create_indicator"],
            B3["what_broke_it"]["wire_uids"]["removed_by_B3_delete"],
            B3["what_broke_it"]["wire_uids"]["still_alive_after_B3_delete_that_B2_added"],
            B3["what_broke_it"]["wire_uids"]["removed_by_B3_that_predate_B2"]))
    fact("%s B3d NO REPAIR WAS ATTEMPTED: %s" % (cid, B3["what_broke_it"]["no_repair_attempted"]))
    gate("%s B3d the ExecState 1 -> 0 transition is attributed to ONE named mutation by direct reading" % cid,
         all(isinstance(v, int) for v in (ex["baseline_before_B1"], ex["after_B1_place"],
                                          ex["after_B2_create_indicator"], ex["after_B3_delete"])),
         "%r -> %r -> %r -> %r" % (ex["baseline_before_B1"], ex["after_B1_place"],
                                   ex["after_B2_create_indicator"], ex["after_B3_delete"]))

    # ------------------------------------------------------------------ B4: move_in TOP-LEVEL -> NESTED
    print("\n--------- %s B4  (move_in TOP-LEVEL -> NESTED Diagram #639)" % cid, flush=True)
    B4 = K.setdefault("B4", {})
    B4["dest_diagram_uid"] = D639
    B4["dest_diagram_index_live"] = d639
    B4["position"] = list(MOVE_POSITION)
    B4["owner_before"] = owner_read(K, "%s B4 the ControlTerminal's owner BEFORE the move" % cid, new_ct_uid,
                                    target)
    ct_b = g.count(target, "ControlTerminal")
    rows_b = len(rows_after)
    es_b = read_exec_state(K, "%s B4 BEFORE the move" % cid, target)
    try:
        inv_before = set(g.uids(target, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_before = set()
        fact("%s uids(Invoke) BEFORE raised %s: %s" % (cid, type(e).__name__, str(e)[:140]))
    mv_ret, mv_err = None, None
    try:
        mv_ret = move_in(target, new_ct_uid, d639, MOVE_POSITION)
        mv_err = ""
    except Exception as e:                                                         # noqa: BLE001
        mv_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    B4["move_in"] = {"returned": mv_ret, "error_verbatim": mv_err}
    fact("%s B4 move_in(#%r -> Diagram #%d at Traverse index %r, position %r) returned %r ; error VERBATIM %r"
         % (cid, new_ct_uid, D639, d639, MOVE_POSITION, mv_ret, mv_err))
    gate("%s B4 move_in returned without raising" % cid, mv_err == "",
         "returned %r, error %r" % (mv_ret, mv_err))
    # PREDICTED RISK (i): the junk `Invoke` residue of the op itself, purged as build_d1_routeb_v0.py:1279-1287.
    try:
        inv_after = set(g.uids(target, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_after = set()
        fact("%s uids(Invoke) AFTER raised %s: %s" % (cid, type(e).__name__, str(e)[:140]))
    junk = sorted(inv_after - inv_before)
    B4["junk_invoke_uids_added_by_move_in"] = junk
    B4["junk_purge"] = []
    fact("%s B4 move_in left %r junk `Invoke`(s): %r (PREDICTED RISK (i))" % (cid, len(junk), junk))
    for ju in junk:
        rec = {"uid": ju}
        try:
            cur = [o["uid"] for o in g.report_all(target, "Invoke")]
            rec["gone"] = sorted(g.delete_object(target, "Invoke", cur.index(ju)) or [])
            rec["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            rec["gone"] = None
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        B4["junk_purge"].append(rec)
        fact("%s B4 purged junk Invoke #%r -> gone %r ; error VERBATIM %r"
             % (cid, ju, rec["gone"], rec["error_verbatim"]))
    B4["owner_after"] = owner_read(K, "%s B4 the ControlTerminal's owner AFTER the move" % cid, new_ct_uid,
                                   target)
    ct_a = g.count(target, "ControlTerminal")
    rows_a = panel_rows(target)
    es_a = read_exec_state(K, "%s B4 AFTER the move (and the junk purge)" % cid, target)
    B4["control_terminal_census"] = {"before": ct_b, "after": ct_a}
    B4["panel_row_count"] = {"before": rows_b, "after": len(rows_a)}
    B4["exec_state"] = {"before": es_b, "after": es_a}
    gate("%s B4b owner_of(new uid) reads ('Diagram', 639) AFTER the move" % cid,
         (B4["owner_after"].get("owner_class"), B4["owner_after"].get("owner_uid")) == ("Diagram", D639),
         "(%r, %r) -> (%r, %r)"
         % (B4["owner_before"].get("owner_class"), B4["owner_before"].get("owner_uid"),
            B4["owner_after"].get("owner_class"), B4["owner_after"].get("owner_uid")))
    gate("%s B4c the ControlTerminal census is unchanged across the move" % cid, ct_b == ct_a,
         "%r -> %r" % (ct_b, ct_a))
    gate("%s B4d ExecState after the move (and the junk purge) == 1" % cid, es_a == 1, "%r -> %r" % (es_b, es_a))
    fact("%s B4 panel rows %r -> %r ; the target indicator's row now: %r"
         % (cid, rows_b, len(rows_a), next((r for r in rows_a if r.get("label") == label), None)))
    dump()

    # ------------------------------------------------------------------ B5: SAVE, BEFORE ANY WIRING (47(e))
    print("\n--------- %s B5  (SAVE HERE, BEFORE ANY WIRING - 47(e))" % cid, flush=True)
    B5 = K.setdefault("B5", {})
    es_save = read_exec_state(K, "%s B5 immediately before the save attempt" % cid, target)
    size, serr = None, None
    if isinstance(es_save, int) and es_save == 1:
        try:
            size = g.save(target)          # allow_broken stays False; gui_save is NEVER called
        except Exception as e:                                                     # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:400])
    else:
        serr = ("NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved. Under 47(e) that stops this "
                "candidate here, and it is a LEGITIMATE outcome, not a failure to work around." % (es_save,))
    B5.update({"exec_state_before_save": es_save, "returned_bytes": size,
               "exception_or_reason_verbatim": serr, "allow_broken": False, "gui_save": False})
    fact("%s B5 g.save() returned %r ; exception/reason VERBATIM %r" % (cid, size, serr))
    B5["file_after"] = D.file_facts("%s B5 the PLACED artefact after the save attempt" % cid, target)
    R["artefacts"].append({"candidate": cid, "role": "placed (unwired)", "path": target,
                           "saved": isinstance(size, int), "file": B5["file_after"]})
    gate("%s B5 ExecState == 1 at the save point and g.save() returned a byte count" % cid,
         isinstance(size, int) and size > 0, "ExecState %r, bytes %r, reason %r" % (es_save, size, serr))
    vb = B5["file_after"].get("version_candidates") if B5["file_after"].get("exists") else None
    gate("%s B5b the artefact is on disk and its version bytes read 26 00 80 00 (LV2026)" % cid,
         bool(B5["file_after"].get("exists")) and any("26 00 80 00" in c.get("bytes", "") for c in (vb or [])),
         "%r" % (vb,))
    dump()
    if not isinstance(size, int):
        raise Stop("%s: ExecState was %r at the save point, so nothing was saved and this candidate stops here "
                   "exactly as 47(e) orders." % (cid, es_save))
    return {"new_ct_uid": new_ct_uid, "label": label}


# ============================================================ STAGE 2 for one candidate: B6..B8, on WIRED
def stage2(K, target, cand, new_ct_uid, label):
    cid = cand["cid"]
    B6, B7, B8 = K.setdefault("B6", {}), K.setdefault("B7", {}), K.setdefault("B8", {})

    print("\n--------- %s B6  (COLD reopen, then wire the BOOLEAN sink #%d t%d to the new indicator)"
          % (cid, BOOL_SRC_UID, BOOL_TERM_INDEX), flush=True)
    B6["cold_exec_state"] = read_exec_state(K, "%s B6 COLD open of the wiring copy (fresh instance)" % cid,
                                            target)
    gate("%s B6 the COLD reopen reads ExecState 1" % cid, B6["cold_exec_state"] == 1,
         "%r" % (B6["cold_exec_state"],))
    B6["owner_of_new_ct_cold"] = owner_read(K, "%s B6 the moved ControlTerminal's owner on the COLD open" % cid,
                                            new_ct_uid, target)
    for uid, key in ((D639, "diag_index_639"), (D686, "diag_index_686")):
        try:
            B6[key] = diag_index(target, uid)
            B6[key + "_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            B6[key] = None
            B6[key + "_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s B6 diag_index(#%d) on the COLD open = %r ; error VERBATIM %r"
             % (cid, uid, B6[key], B6[key + "_error_verbatim"]))
    d639, d686 = B6["diag_index_639"], B6["diag_index_686"]

    rows_live, errs_live = class_membership(target, BOOL_SRC_UID)
    B6["class_membership_live"] = rows_live
    B6["class_scan_errors_verbatim"] = errs_live
    chosen = next((r for r in rows_live if r["class"] == "Function"), None)
    if chosen is None and rows_live:
        chosen = sorted(rows_live, key=lambda r: r["members"])[0]
    B6["chosen_class_row_live"] = chosen
    B6["chosen_rule"] = ("`Function` when it holds the uid (cycle 57's own addressing, so nothing but the "
                         "carrier's TYPE differs); otherwise the class with the fewest members that holds it.")
    fact("%s B6 LIVE: diag_index(#639) = %r, #%d class membership %r, addressing it as %r"
         % (cid, d639, BOOL_SRC_UID, rows_live, chosen))

    src_before = wired_counts(K, "%s B6 BEFORE #%d (the BOOLEAN sink node)" % (cid, BOOL_SRC_UID), target,
                              d639 if isinstance(d639, int) else 0, BOOL_SRC_UID, BOOL_NODES_PIN)
    bt = next((t for t in src_before.get("terms", []) if t["i"] == BOOL_TERM_INDEX), None)
    B6["bool_terminal_live"] = bt
    fact("%s B6 #%d terminal %d re-read on this file: %r" % (cid, BOOL_SRC_UID, BOOL_TERM_INDEX, bt))
    loop_before = wired_counts(K, "%s B6 BEFORE #%d (loop 1.1, the tunnel/border witness)" % (cid, LOOP11_UID),
                               target, d686 if isinstance(d686, int) else 0, LOOP11_UID, LOOP11_NODES_PIN)

    rows_p = panel_rows(target)
    row_now = next((r for r in rows_p if r.get("label") == label), None)
    B6["target_row_before_wiring"] = row_now
    label_live = (row_now or {}).get("label")
    fact("%s B6 the indicator row re-read on this file: %r (label VERBATIM %r, utf-8 hex %r)"
         % (cid, row_now, label_live, (label_live or "").encode("utf-8").hex()))

    wire_b = (row_now or {}).get("wire")
    wires_b = g.count(target, "Wire")
    es_pre = read_exec_state(K, "%s B6 BEFORE wire_indicators" % cid, target)
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
    B6["wire_indicators"] = {"node_index": (chosen or {}).get("index"),
                             "node_class": (chosen or {}).get("class"),
                             "src_terms_repr": repr([(bt or {}).get("name")]),
                             "indicator_names_repr": repr([label_live]),
                             "indicator_names_utf8_hex": [(label_live or "").encode("utf-8").hex()],
                             "diagram_index": d639, "seconds": wi_dt, "error_verbatim": wi_err}
    fact("%s B6 wire_indicators(%s[%r], [%r] -> [%r], diagram_index=%r) error VERBATIM %r"
         % (cid, (chosen or {}).get("class"), (chosen or {}).get("index"), (bt or {}).get("name"), label_live,
            d639, wi_err))
    gate("%s B6b wire_indicators returned an EMPTY error column" % cid, wi_err == "",
         "%r (PREDICTED RISK (iii): a raise is a LEGITIMATE reading)" % (wi_err,))

    rows_w = panel_rows(target)
    row_w = next((r for r in rows_w if r.get("label") == label), None)
    wire_a = (row_w or {}).get("wire")
    wires_a = g.count(target, "Wire")
    B6["target_row_after_wiring"] = row_w
    B6["target_wire_uid"] = {"before": wire_b, "after": wire_a}
    B6["whole_vi_wire_count"] = {"before": wires_b, "after": wires_a,
                                 "delta": (wires_a - wires_b) if isinstance(wires_a, int)
                                 and isinstance(wires_b, int) else None}
    fact("%s B6 the target indicator's wire uid %r -> %r ; whole-VI Wire count %r -> %r (delta %r; a BRANCH "
         "adds NO Wire object, tools/gscript.py:1771-1772). The sink terminal's own wire reads %r (47(d) pin %r)"
         % (cid, wire_b, wire_a, wires_b, wires_a, B6["whole_vi_wire_count"]["delta"], (bt or {}).get("wire"),
            BOOL_WIRE_PIN))
    gate("%s B6c the new indicator's wire uid changed from 0" % cid, bool(wire_a) and wire_a != wire_b,
         "%r -> %r" % (wire_b, wire_a))
    es_post = read_exec_state(K, "%s B6 AFTER wire_indicators" % cid, target)
    B6["exec_state"] = {"before": es_pre, "after": es_post}

    src_after = wired_counts(K, "%s B6 AFTER #%d (the BOOLEAN sink node)" % (cid, BOOL_SRC_UID), target,
                             d639 if isinstance(d639, int) else 0, BOOL_SRC_UID, BOOL_NODES_PIN)
    loop_after = wired_counts(K, "%s B6 AFTER #%d (loop 1.1, the tunnel/border witness)" % (cid, LOOP11_UID),
                              target, d686 if isinstance(d686, int) else 0, LOOP11_UID, LOOP11_NODES_PIN)
    gate("%s B6d #%d's wired-terminal count is unchanged across the wiring (37(e))" % (cid, BOOL_SRC_UID),
         src_before.get("n_wired") is not None and src_after.get("n_wired") is not None
         and src_before.get("n_wired") == src_after.get("n_wired"),
         "%r -> %r wired of %r -> %r terminals" % (src_before.get("n_wired"), src_after.get("n_wired"),
                                                   src_before.get("n_terms"), src_after.get("n_terms")))
    gate("%s B6e #%d's terminal count unchanged - NO tunnel or border object appeared (37(e))"
         % (cid, LOOP11_UID),
         loop_before.get("n_terms") is not None and loop_before.get("n_terms") == loop_after.get("n_terms"),
         "%r -> %r terminals, %r -> %r wired"
         % (loop_before.get("n_terms"), loop_after.get("n_terms"),
            loop_before.get("n_wired"), loop_after.get("n_wired")))
    fact("%s B6e EXPLICIT (37(e) grain): #%d terminals %r -> %r, wired %r -> %r; a tunnel or border object "
         "would show as a terminal-count INCREASE. Increase observed: %r"
         % (cid, LOOP11_UID, loop_before.get("n_terms"), loop_after.get("n_terms"), loop_before.get("n_wired"),
            loop_after.get("n_wired"),
            (loop_after.get("n_terms") or 0) - (loop_before.get("n_terms") or 0)))
    census(K, "%s B6 after the wiring attempt" % cid, target)
    dump()

    # ------------------------------------------------------------------ B8 (save) happens BEFORE B7's read
    print("\n--------- %s B8  (save again IFF ExecState == 1; the B5 artefact stands either way)" % cid,
          flush=True)
    es_save = read_exec_state(K, "%s B8 immediately before the second save attempt" % cid, target)
    size, serr = None, None
    if isinstance(es_save, int) and es_save == 1:
        try:
            size = g.save(target)          # allow_broken stays False; gui_save is NEVER called
        except Exception as e:                                                     # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:400])
    else:
        serr = ("NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved. The B5 artefact still stands."
                % (es_save,))
    B8.update({"exec_state_before_save": es_save, "returned_bytes": size,
               "exception_or_reason_verbatim": serr, "allow_broken": False, "gui_save": False})
    fact("%s B8 g.save() returned %r ; exception/reason VERBATIM %r" % (cid, size, serr))
    B8["file_after"] = D.file_facts("%s B8 the WIRED artefact after the save attempt" % cid, target)
    R["artefacts"].append({"candidate": cid, "role": "wired", "path": target,
                           "saved": isinstance(size, int), "file": B8["file_after"]})
    gate("%s B8 ExecState == 1 at the second save point and g.save() returned a byte count" % cid,
         isinstance(size, int) and size > 0, "ExecState %r, bytes %r, reason %r" % (es_save, size, serr))
    dump()

    # ------------------------------------------------------------------ B7: the ORDERED second pass (42(b))
    print("\n--------- %s B7  (ORDERED second pass: `Is Broken?` AFTER the save, 42(b)) - THE ANSWER" % cid,
          flush=True)
    if not wire_a:
        B7["not_attempted_because"] = ("B6 produced no wire on the indicator (uid %r -> %r), so 42(b)'s ordered "
                                       "pass has nothing to read." % (wire_b, wire_a))
        fact("%s B7 NOT ATTEMPTED: %s" % (cid, B7["not_attempted_because"]))
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
    fact("%s B7 the ordered pass will re-connect: source %r -> sink %r" % (cid, B7["source"], sink))
    if sink is None or src_i is None:
        B7["not_attempted_because"] = ("the 6371004 carrier needs BOTH ends addressable in Nodes[]: source index "
                                       "%r, a sink already on wire %r %r." % (src_i, net_wire, sink))
        fact("%s B7 NOT ATTEMPTED: %s" % (cid, B7["not_attempted_because"]))
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
    fact("%s B7 ORDERED `Is Broken?` = %r on wire uid %r (op error column %r, wire_delta %r). EITHER value is a "
         "LEGITIMATE reading - it IS the run's answer for this candidate."
         % (cid, ib, B7["op_indicators"].get("UID 2"), B7.get("error_verbatim"), B7.get("wire_delta")))
    gate("%s B7 the ORDERED second-pass `Is Broken?` read returned a boolean" % cid, isinstance(ib, bool),
         repr(ib))
    read_exec_state(K, "%s B7 after the Is Broken? read (SUSPECT, docs/NAMES.md:912-918; the save already "
                    "happened)" % cid, target)
    dump()


# ============================================================ one candidate, end to end
def run_candidate(cand):
    cid = cand["cid"]
    K = R["candidates"].setdefault(cid, {"cid": cid, "spec": cand})
    placed = os.path.join(g.CLAUDEDEV, "D1_s3a_bool_%s_placed_%s.vi" % (cid, STAMP))
    wired = os.path.join(g.CLAUDEDEV, "D1_s3a_bool_%s_wired_%s.vi" % (cid, STAMP))
    K["artefact_placed"] = placed
    K["artefact_wired"] = wired
    print("\n===================================================================", flush=True)
    print("=== CANDIDATE %s: %s   (%s)" % (cid, cand["what"], cand["verb"]), flush=True)
    print("=== citation: %s" % cand["citation"], flush=True)
    print("===================================================================", flush=True)

    if os.path.exists(placed):
        os.remove(placed)
    shutil.copy2(S2_ARTEFACT, placed)
    p = probe("%s T3 the scratch at creation (copied from D1_s2_loops.vi)" % cid, placed)
    K["scratch_at_creation"] = p
    gate("%s T3 the scratch is byte-identical to D1_s2_loops.vi at creation" % cid, p.get("md5") == S2_MD5,
         "%s (expected %s)" % (p.get("md5", "?"), S2_MD5))
    dump()

    carry, placed_saved = None, False
    try:
        with D.Preload("%s stage 1" % cid):
            g.open_panel(placed)
            time.sleep(1.0)
            try:
                carry = stage1(K, placed, cand)
            finally:
                placed_saved = isinstance(K.get("B5", {}).get("returned_bytes"), int)
                close_quietly(placed)
    except Stop as s:
        K["stopped_at"] = str(s)
        fact("%s STOPPED at a step precondition: %s" % (cid, s))
    except Exception as e:                                                         # noqa: BLE001
        K["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("%s stage 1 raised %s: %s" % (cid, type(e).__name__, str(e)[:600]))
    dump()

    if not (placed_saved and carry):
        fact("%s B6..B8 NOT ATTEMPTED: B5 did not save (ExecState %r), and 47(e) orders the candidate to stop "
             "there." % (cid, K.get("B5", {}).get("exec_state_before_save")))
        if os.path.exists(placed) and not placed_saved:
            try:
                os.remove(placed)
                fact("%s cleanup: the unsaved scratch %s was removed (byte-identical to S2, nothing of its own)"
                     % (cid, os.path.basename(placed)))
            except Exception as e:                                                 # noqa: BLE001
                fact("%s cleanup: removing %s FAILED %s: %s"
                     % (cid, os.path.basename(placed), type(e).__name__, str(e)[:200]))
        dump()
        return

    # the wiring copy is a BYTE COPY, opened in a RESTARTED LabVIEW so it loads COLD from disk
    wired_saved = False
    try:
        K["handles_before_cold_restart"] = labview_handles()
        D.fresh("%s RESTART (so the wiring copy loads COLD, from disk, with nothing preloaded)" % cid)
        K["handles_after_cold_restart"] = labview_handles()
        fact("%s LabVIEW handles across the cold restart: %r -> %r"
             % (cid, K.get("handles_before_cold_restart"), K.get("handles_after_cold_restart")))
        if os.path.exists(wired):
            os.remove(wired)
        shutil.copy2(placed, wired)
        q = probe("%s B6 the wiring copy at creation (copied from the B5 artefact)" % cid, wired)
        K["wiring_copy_at_creation"] = q
        fact("%s B6 the wiring copy is byte-identical to the B5 artefact: %r"
             % (cid, q.get("md5") == K.get("B5", {}).get("file_after", {}).get("md5")))
        with D.Preload("%s stage 2" % cid):
            g.open_panel(wired)
            time.sleep(1.0)
            try:
                stage2(K, wired, cand, carry["new_ct_uid"], carry["label"])
            finally:
                wired_saved = isinstance(K.get("B8", {}).get("returned_bytes"), int)
                close_quietly(wired)
    except Stop as s:
        K["stopped_at"] = str(s)
        fact("%s STOPPED at a step precondition: %s" % (cid, s))
    except Exception as e:                                                         # noqa: BLE001
        K["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("%s stage 2 raised %s: %s" % (cid, type(e).__name__, str(e)[:600]))
    K["wired_saved"] = wired_saved
    if os.path.exists(wired) and not wired_saved:
        try:
            os.remove(wired)
            fact("%s cleanup: the unsaved wiring copy %s was removed (a byte-identical duplicate of the B5 "
                 "artefact, nothing of its own on disk)" % (cid, os.path.basename(wired)))
        except Exception as e:                                                     # noqa: BLE001
            fact("%s cleanup: removing %s FAILED %s: %s"
                 % (cid, os.path.basename(wired), type(e).__name__, str(e)[:200]))
    dump()


# ============================================================ PHASE C: the guard_cycle DRY RUN (pure reading)
def phase_c():
    """Feed guard_cycle.py the PreToolUse payload it reads on stdin (guard_cycle.py:534-541) for a HYPOTHETICAL
    recipe build, and report its exit code and stderr VERBATIM. NO DATE IS EDITED, CYCLE_GUARD_OFF IS NEVER SET,
    THE GATE IS NOT 'FIXED', AND NO RECIPE IS CREATED."""
    C = R["phaseC"]
    print("\n=================== PHASE C  (guard_cycle DRY RUN - pure measurement, nothing is changed)",
          flush=True)
    rel = "tools/" + "recipes/" + "stage_d1_s3a_focus_ind.py"
    cmd = "py -u " + rel
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
    C["hypothetical_command"] = cmd
    C["hook"] = "tools/hooks/guard_cycle.py"
    C["payload_contract"] = "tools/hooks/guard_cycle.py:534-541 reads json on stdin and takes tool_input.command"
    env = dict(os.environ)
    env.pop("CYCLE_GUARD_OFF", None)                 # never set; popped so an inherited one cannot mask a refusal
    try:
        rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "hooks", "guard_cycle.py")],
                            input=payload, capture_output=True, text=True, timeout=300, cwd=ROOT, env=env)
        C["returncode"] = rc.returncode
        C["stdout_verbatim"] = rc.stdout
        C["stderr_verbatim"] = rc.stderr
    except Exception as e:                                                         # noqa: BLE001
        C["returncode"] = None
        C["stdout_verbatim"] = ""
        C["stderr_verbatim"] = "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])
    C["verdict"] = ("REFUSES (exit 2)" if C.get("returncode") == 2 else
                    "ALLOWS (exit 0)" if C.get("returncode") == 0 else
                    "exit %r - neither 0 nor 2" % (C.get("returncode"),))
    fact("C guard_cycle dry run on %r -> exit %r = %s" % (cmd, C.get("returncode"), C["verdict"]))
    for ln in (C.get("stderr_verbatim") or "").rstrip().splitlines():
        print(("      [guard_cycle stderr VERBATIM] " + ln).encode("ascii", "replace").decode("ascii"),
              flush=True)
    for ln in (C.get("stdout_verbatim") or "").rstrip().splitlines():
        print(("      [guard_cycle stdout VERBATIM] " + ln).encode("ascii", "replace").decode("ascii"),
              flush=True)
    C["note"] = ("REPORTED, NOT ACTED ON. No date was rolled forward, CYCLE_GUARD_OFF was never set, the gate "
                 "was not patched, and tools/recipes/stage_d1_s3a_focus_ind.py was not created.")
    fact("C %s" % C["note"])
    dump()


# ======================================================================================== MAIN
def main():
    print("=== diag_s58_boolcarrier  %s   (cycle 58 material #1, 47(i) route 1; DIAGNOSTIC, never a recipe; NO "
          "VI IS RUN, 34(f); no new op, no new device, no GUI action; CHOOSES AND RECOMMENDS NOTHING)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    fact("tools/recipes/stage_d1_s3a_focus_ind.py: exists=%r mtime=%r - REPORTED, NOT TOUCHED"
         % (R["recipe_file_reported_not_touched"]["exists_at_start"],
            R["recipe_file_reported_not_touched"]["mtime"]))

    print("\n=================== PHASE A  (the census - FILES ONLY, written down before any call)", flush=True)
    for v in R["phaseA_census"]["verbs"]:
        fact("A rank %d  %-16s %s  -> places %s ; Boolean output by construction: %s"
             % (v["rank"], v["verb"], v["site"], v["places"], v["boolean_output_by_construction"]))
    fact("A top-level-only node placers (no diagram_index): %r"
         % (R["phaseA_census"]["top_level_only_verbs_no_diagram_index"],))
    for c in CANDIDATES:
        fact("A CANDIDATE %s  %s(%r, %r)  -> %s ; predicted Boolean terminal %r ; citation: %s"
             % (c["cid"], c["verb"], c["cls"], c["props"], c["what"], c["predicted_bool_term_name"],
                c["citation"]))
    fact("A the Boolean-terminal SELECTION RULE: %s" % R["phaseA_census"]["boolean_terminal_selection_rule"])
    fact("A 47(j): no reader in this fleet returns a terminal's DATA TYPE, so phase A PREDICTS and phase B's "
         "`Is Broken?` MEASURES. 47(g): %s" % R["phaseA_census"]["prior_art_grep_note"])
    dump()

    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (cycle 57 close left the instance at 63,533; fresh baseline ~31,500): %r"
         % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    # ---- the mechanical pre-batch restart the brief orders (44(e); standing restart permission, CLAUDE.md 3)
    D.fresh("T2b RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    R["candidate_order"] = [c["cid"] for c in CANDIDATES]
    R["deadline_guard_s"] = START_NEW_CANDIDATE_BEFORE_S
    for cand in CANDIDATES:
        el = time.time() - T_START
        if el >= START_NEW_CANDIDATE_BEFORE_S:
            R["candidates"].setdefault(cand["cid"], {"cid": cand["cid"], "spec": cand})["not_attempted"] = (
                "DEADLINE GUARD: %.0f s elapsed of the %d s budget for starting a new candidate (bgrun limit "
                "25 min). Recorded, not skipped for any other reason." % (el, START_NEW_CANDIDATE_BEFORE_S))
            fact("%s NOT ATTEMPTED: %s" % (cand["cid"],
                                           R["candidates"][cand["cid"]]["not_attempted"]))
            continue
        try:
            run_candidate(cand)
        except Exception as e:                                                     # noqa: BLE001
            R["candidates"].setdefault(cand["cid"], {})["fatal"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            fact("%s raised OUTSIDE its stages %s: %s" % (cand["cid"], type(e).__name__, str(e)[:600]))
        dump()

    phase_c()

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
    fact("tools/recipes/stage_d1_s3a_focus_ind.py at the END: exists=%r (it must still be False)"
         % R["recipe_file_reported_not_touched"]["exists_at_end"])
    gate("Z3 no recipe was created: stage_d1_s3a_focus_ind.py still does not exist on disk",
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
    for cid in R["candidate_order"]:
        K = R["candidates"].get(cid, {})
        fact("ANSWER %s  carrier=%r terminal=%r label=%r  wire %r -> %r  ExecState %r -> %r  Is Broken?=%r  "
             "artefacts placed=%r wired=%r  stopped=%r"
             % (cid, (K.get("spec") or {}).get("what"), (K.get("B2") or {}).get("terminal_name"),
                (K.get("B2") or {}).get("label_repr"),
                (K.get("B6") or {}).get("target_wire_uid", {}).get("before"),
                (K.get("B6") or {}).get("target_wire_uid", {}).get("after"),
                (K.get("B6") or {}).get("exec_state", {}).get("before"),
                (K.get("B6") or {}).get("exec_state", {}).get("after"),
                (K.get("B7") or {}).get("is_broken_ordered"),
                (K.get("B5") or {}).get("returned_bytes"), (K.get("B8") or {}).get("returned_bytes"),
                K.get("stopped_at") or K.get("not_attempted")))
    fact("ARTEFACTS ON DISK: %r" % ([a for a in R["artefacts"] if a.get("saved")],))

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
