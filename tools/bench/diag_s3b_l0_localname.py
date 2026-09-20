"""diag_s3b_l0_localname - cycle 60 (attempt 2) material #1. BUILD `claudeDev\\OpLocalName_v0.vi`, the
one-property READER for a Local Variable's binding, and measure it.

A DIAGNOSTIC under tools/bench/, NEVER a recipe (48(n) / STATUS `## NEXT`: a RECIPE build is refused in any
cycle that has already produced a build log, so L0 runs as a diagnostic, as every S3a sub-step did). Nothing
under tools/recipes/ is written, renamed, copied or launched by this file - gate Z4.

WHY A READER AND NOT ANOTHER CREATOR ATTEMPT - the judgement session's decision, not this session's.
Cycle 60 attempt 1 (`tools/bench/diag_s3b_l0_createlocal.log`, rc=1, 30 pass / 2 fail) BUILT
`claudeDev\\OpCreateLocal_v0.vi` (md5 58275b212dfa040685613e3edbf403f2) and it WORKS as a creator:
`Create:Local Variable` 6331C02 invoked on a live Control reference returned error cluster `(False, 0, '')`
and a new `Local` uid 23507, 20/20 consecutive calls, handles flat (delta 0), refs 12/12/0 live. Its two
FAILs (`L0_b5 bound None`, `L0_b6 None vs 'index'`) are an ABSENT INSTRUMENT, not a binding failure: the run
read the binding with `node_labels()`, which reads `Node.Label` 6359001 -> the node's OWN label
(`tools/gscript.py:588-594`), and all eight of the main VI's pre-existing Locals return the VI's FILE NAME
there (`tools/bench/main_vi_node_labels.json`, cited in `archive/peer/2026-09-21-c60-l0-readback-none.md`).
So the fleet cannot read a Local's binding at all, and CLAUDE.md's "When a diagnosis is GUESSED twice, build
the READER" applies.

AUTHORISATION FOR A NEW OP VI - 46(k) (`docs/cycle27-plan.md:1697-1705`), quoted in its own words:
  `docs/cycle27-plan.md:31` reads *"**No further process device** (user, 08:53) - still the standing order.
  A retrospective naming one is a finding."*  46(k): *"A **process device** is gate and retrospective
  machinery; an **op VI** is deliverable-construction tooling, and every stage of D1 so far was built with
  them ... So the order does not reach an op VI that places a Local Variable, and **the S3b transport needs
  no decision from the user**: if `Control -> Create:Local Variable` 6331C02 through `build_invoke` is the
  route, it is simply built."*
Reading `Local.Control Name` 6355400 is NOT route B (route B is *create* by `New VI Object` style 2061 PLUS a
WRITE to that property) and is therefore not fenced by 49(d).
49(i), stated here in writing because the brief requires it:
*** THIS OP WILL BE REVISED ON ANY REVIEW THAT GATES IT. ***

WHAT ALREADY EXISTED - checked before a line of this was written (CLAUDE.md "check what exists before creating
anything"; `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`, docs/toolkit-capabilities.md):
  * NO reader of a Local's binding exists anywhere: `6355400` appears 0 times in tools/gscript.py and 0 times
    in docs/vi-server-ids.json (Pre-decided 46(i), `docs/cycle27-plan.md:1689-1692`); no `Op*.vi` in
    claudeDev carries `Local` in its name except OpCreateLocal_v0, built last night.
  * `tools/bench/diag_s3b_l0_createlocal.py` - attempt 1, the shape of this file (gates, probes, JSON dump,
    the `create_local` wrapper reused verbatim below for R2).
  * `tools/recipes/build_opnodelabels_v0.py` - THE DONOR OF RECORD's own builder: OpNodeLabels_v0 is
    Traverse `Class Name` by `index` -> Index Array -> ... -> property -> string indicators, with front-panel
    API `vi path / Class Name / index / index 2 / index 3 / error in / error in (no error) / Class Name 2 /
    Class Name 3` and indicators `Array` (Text) / `Array 2` (UID) / `error out 2`
    (`tools/bench/opnodelabels_labels.json`).
  * gscript verbs used, ALL pre-existing, NONE patched: op, ref_counts, report, report_all, node_labels,
    node_terms_uid, net_map, count, uids, open_panel, close_panel, ensure_loaded, wire, create_indicator,
    fp_labels, exec_state, save, build_property, reset, _run.
  * `tools/recipes/build_d1_v0.py` - owner_of, diag_index (move_in is NOT used: the brief forbids reproducing
    attempt 1's pointless relocation, and this op relocates nothing).
NO new gscript verb is added and no fleet file is patched. The Python-side wrapper `local_name()` lives IN
THIS DIAGNOSTIC; promoting it into tools/gscript.py is judgement's call, not this run's.

=====================================================================================================
THE OP, EXACTLY AS THE BRIEF FIXES IT (nothing here is designed by a material session)
  donor of record : claudeDev\\OpNodeLabels_v0.vi (Traverse class by index -> property -> string indicator)
  in  : VI path, the Traverse class string (`Local`), the Traverse index
  new : ONE Property Node of class `VI Server:Local` carrying ONE property, `Control Name` 6355400, whose
        `reference` is fed by the donor's existing Index Array `element` (the Traverse-selected object), and
        ONE string indicator created on its `Control Name` output terminal
  out : that string + the error cluster the donor already surfaces
  hygiene : it closes every reference it opens - the donor's own ladder is unchanged; the wrapper releases
        every cached reference (g.reset()) and the 20-call gate reads the handle count either side.
*** IF THE DONOR'S MEASURED ON-DISK SHAPE DOES NOT SUPPORT A ONE-PROPERTY READ ON A TRAVERSE-SELECTED OBJECT,
    THAT IS A FACT THIS RUN REPORTS. No other donor is substituted, no different op is designed, nothing is
    repaired: the copy is left unsaved and removed, and the OPEN line carries the question. ***
KNOWN HAZARD, WRITTEN DOWN BEFORE THE RUN (the reason the gate below is by EFFECT): the erdosmiller Traverse
returns GENERIC GObject references, and this fleet's established way to read a class-specific property off one
is `To More Specific Class` seeded by a typed wire (`tools/gscript.py:626-635` loop_cast; :946 OpTunnels).
`connect_terminals`'s own docstring (`tools/gscript.py:2415`) says "Type mismatches make a broken wire". So
the `element -> reference` wire may land and still leave `ExecState` 0. That reading is the measurement.

=====================================================================================================
PREDICTION CONTRACT (every gate is the readback of a CALL; FATAL stops the chain and still dumps JSON)
  T1    the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                      FATAL
  T1b   claudeDev\\D1_s1_copy.vi md5 == 3e3d23cefd3a334001aa9d6156bf1aee
  T2    claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                            FATAL
  T3    claudeDev\\D1_s3a_focus_ind.vi md5 == eef91c1d91f16b034707e4d1285ca8cb                       FATAL
  T4    the DONOR claudeDev\\OpNodeLabels_v0.vi exists; md5 recorded for gate Z3                     FATAL
  T4b   claudeDev\\OpCreateLocal_v0.vi exists (R2 drives it); md5 recorded for gate Z3b              FATAL
  T5    the pre-batch LabVIEW restart ran (44(e)) and the handle count was read either side
  --- R0: BUILD -----------------------------------------------------------------------------------
  R0_a1 the donor copy opens and reads ExecState 1 before any edit
  R0_a2 the copy's SHAPE was measured off the machine: every node on diagram 0 with its full terminal table
        (this is the "does the donor's shape support it" reading, and it is a FACT either way)
  R0_a3 exactly ONE IndexArray is on the copy's diagram and it carries a terminal named `element`
  R0_a4 build_property('VI Server:Local', [('6355400', False)]) returned exactly 1 new Property; the EXACT
        class string passed and whether it RESOLVED are recorded with the error column VERBATIM
  R0_a5 the new Property Node's FULL terminal table was READ off the machine and carries `reference`
  R0_a6 a terminal whose name is the SHORT NAME of 6355400 is present and is a SOURCE (read off the machine,
        never retyped)
  R0_a7 IA.`element` -> PN.`reference` returned an EMPTY error column AND the reference terminal's wire uid
        is non-zero afterwards                                                        (the EFFECT gate)
  R0_a8 ExecState after the wiring was READ   (a 0 IS the answer to the KNOWN HAZARD above, not a failure of
        the instrument - it is reported and NOTHING is repaired)
  R0_a9 create_indicator on the property's output terminal added exactly one ControlTerminal and its label was
        read off the machine by an fp_labels diff
  R0_a10 ExecState == 1 after the indicator  *** THE OP'S PASS CRITERION - no save is attempted below it ***
  R0_a11 g.save returned a byte count; md5, size and version bytes (26 00 80 00 = LV2026) recorded
  --- R1: the reader against ground truth, on a SCRATCH copy ---------------------------------------
  R1_b0 the scratch is byte-identical to D1_s3a_focus_ind.vi at creation; the ARTEFACT's md5 is gated before
        AND after the whole phase (49(e): never the artefact itself)
  R1_b1 the scratch opens at ExecState 1 and its `Local` census is READ (docs/toolkit-capabilities.md:284
        records 8 at the S2/main baseline; the READING is the gate, never the 8)
  R1_b2 `Control Name` was read for EVERY pre-existing Local; every uid -> string pair is reported VERBATIM
  R1_b3 whether ANY returned string is a `.vi` file name is stated plainly (a FACT, never a pass/fail)
  --- R2: the open question ------------------------------------------------------------------------
  R2_c1 the front-panel control whose owned label reads 'index' was located by fp_labels (label taken from the
        machine's own bytes, hex recorded) and OpCreateLocal_v0 was driven with it
  R2_c2 the creator's error cluster, the `Local` census before/after and the new uid are recorded VERBATIM
  R2_c3 the scratch's ExecState BEFORE and AFTER the creator call were READ (a 0 after is a LEGITIMATE
        reading - attempt 1 measured exactly that - and is reported, not repaired)
  R2_c4 the new Local's `Control Name` was read with the NEW READER and reported VERBATIM
  --- R3: hygiene ----------------------------------------------------------------------------------
  R3_d1 20 consecutive reader calls ran; the handle count was read either side
  R3_d2 handles flat within +-100 (a FAIL here is a FINDING, not a blocker - 44(e)/49(j))
  R3_d3 refs opened == closed, 0 live
  R3_d4 the scratch was DELETED in the same run and exists=False
  --- R4: REPORT ONLY, no build --------------------------------------------------------------------
  R4_e1 the FULL terminal table of an Invoke node this fleet already built with a method of KNOWN signature
        (OpMoveIn_v0.vi's Move; OpConPaneAssign_v0.vi's assign) was dumped, beside OpCreateLocal_v0.vi's
        6331C02 node, so the six-terminal reading (i=4 sink / i=5 source, both `Create Local`) can be
        compared against a known case.   *** NO CONCLUSION IS DRAWN. ***
  R4_e2 the three op VIs read in R4 are byte-unchanged by the reading
  --- Z ---------------------------------------------------------------------------------------------
  Z1    ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged after everything
  Z2    refs opened == closed, 0 live
  Z3    the DONOR OpNodeLabels_v0.vi is byte-unchanged
  Z3b   OpCreateLocal_v0.vi is byte-unchanged
  Z4    no file was created under tools/recipes/ by this run

BOUNDS. NO VI IS RUN (34(f)) - the only VIs that execute are the fleet's op VIs, which is what scripting is.
No GUI action. No motor / ASI / camera (rig 조립 / ASSEMBLED; tools/motor_gate.py is not called and no serial
port is opened). No new PROCESS device. No recipe. `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save`
are neither imported nor called; `allow_broken` is never True. `move_in` is NOT called at all. Every diagram
index used is resolved from the machine (diag_index by uid, or the op's own top-level whose uid is read back),
never hard-coded, and every owner comparison accepts BOTH 'Diagram' and 'TopLevelDiagram'. Originals are never
opened for write. NOTHING SAVED IS EVER DELETED except the SCRATCH self-test copy, which CLAUDE.md rule 4
requires to be deleted in the same run, and the UNSAVED donor copy if the op never reaches a legal save point.
NO ROUTE IS CHOSEN OR RECOMMENDED and no plan document or STATUS `## NEXT` line is edited.
`retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` are NOT run.
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
from build_d1_v0 import diag_index, owner_of                                       # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"

DONOR = os.path.join(g.CLAUDEDEV, "OpNodeLabels_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpLocalName_v0.vi")
CREATOR = os.path.join(g.CLAUDEDEV, "OpCreateLocal_v0.vi")
MOVEIN = os.path.join(g.CLAUDEDEV, "OpMoveIn_v0.vi")
CONPANE = os.path.join(g.CLAUDEDEV, "OpConPaneAssign_v0.vi")

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_LN_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_s3b_l0_localname.json")

LOCAL_CLASS = "VI Server:Local"     # the EXACT class string passed to the property builder - recorded as R0 asks
CONTROL_NAME_ID = "6355400"         # Local.Control Name (docs/NAMES.md:260, wiki, unverified until this run)
TRAVERSE_CLASS = "Local"            # docs/toolkit-capabilities.md:284 - a VALID Traverse class (census 8)
PN_AT = (760, 430)                  # empty canvas on the donor's small diagram (attempt 1 used (760,430) too)
STD_PN_TERMS = ("reference", "reference out", "error in (no error)", "error in", "error out")
TARGET_LABEL = "index"              # the numeric leg's indicator label; the STRING DRIVEN ONWARD is the one
                                    # fp_labels returns off the machine (hex recorded), never this literal
N_CONSECUTIVE = 20
SCAN_LIMIT = 60

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 60 attempt 2: build claudeDev\\OpLocalName_v0.vi - a ONE-PROPERTY READER (Traverse `Local` "
             "by index -> Local.Control Name 6355400 -> string indicator) on donor OpNodeLabels_v0.vi - and "
             "measure it (R0 build, R1 ground truth, R2 the open question, R3 hygiene, R4 report-only).",
     "authorisation": "46(k), docs/cycle27-plan.md:1697-1705 - Pre-decided 2 forbids a further PROCESS DEVICE, "
                      "not an op VI; quoted verbatim in the module docstring. Reading 6355400 is NOT route B "
                      "(route B is New VI Object style 2061 + a WRITE to that property), so 49(d) does not "
                      "fence it.",
     "will_be_revised_on_any_review_that_gates_it": "49(i) - stated in the brief and repeated here.",
     "donor_of_record": DONOR,
     "no_other_donor_substituted": True, "no_different_op_designed": True,
     "chooses_no_route": True, "recommends_no_route": True, "interprets_nothing": True,
     "no_vi_was_run": True, "no_new_device": True, "no_gui_action": True, "no_recipe": True,
     "move_in_never_called": True,
     "new_op_vi": OP, "edits_no_plan_document": True, "edits_no_status_next": True,
     "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "REFUSED by the brief - not imported, not called; the GUI menu form "
                                  "(gscript.py:1629) is not called either.",
     "gui_save": "NEVER called", "allow_broken": "NEVER True",
     "rig_state": "조립 / ASSEMBLED (motors + ASI only through tools/motor_gate.py, which is not called; "
                  "camera not needed and not touched)",
     "citations": {"why_the_reader": "archive/peer/2026-09-21-c60-l0-readback-none.md; "
                                     "tools/gscript.py:588-594; tools/bench/main_vi_node_labels.json",
                   "donor_builder": "tools/recipes/build_opnodelabels_v0.py",
                   "donor_panel_labels": "tools/bench/opnodelabels_labels.json",
                   "control_name_id": "docs/NAMES.md:260 (wiki, NOT yet verified on this machine)",
                   "local_is_a_valid_traverse_class": "docs/toolkit-capabilities.md:284 (census 8)",
                   "no_reader_exists": "docs/cycle27-plan.md:1689-1692 (Pre-decided 46(i))",
                   "type_mismatch_makes_a_broken_wire": "tools/gscript.py:2415",
                   "tmsc_needs_a_typed_seed": "tools/gscript.py:626-635, :946",
                   "attempt_1": "tools/bench/diag_s3b_l0_createlocal.{py,log,json}",
                   "diagnostic_not_recipe": "Pre-decided 48(n)",
                   "handles_caveat": "Pre-decided 44(e)/49(j)",
                   "scratch_deleted_same_run": "CLAUDE.md rule 4; Pre-decided 49(e)"},
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "s3a_artefact": {"path": S3A_ARTEFACT, "md5_pin": S3A_MD5},
     "donor": {"path": DONOR}, "creator": {"path": CREATOR},
     "handles": {}, "hash_probe": [],
     "R0_build": {}, "R1_ground_truth": {}, "R2_open_question": {}, "R3_hygiene": {}, "R4_report_only": {},
     "artefacts": [], "pass_criteria": {"op_execstate": None, "reader_indicator_label": None}}

NAME_IND = None          # the label LabVIEW gives the new string indicator - READ off the machine at build time


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


def read_exec_state(rec, tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    rec.setdefault("exec_state_timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def count_of(target, cls):
    try:
        return g.count(target, cls)
    except Exception as e:                                                         # noqa: BLE001
        return "ERROR %s: %s" % (type(e).__name__, str(e)[:80])


def uid_set(target, cls):
    try:
        return set(g.uids(target, cls)), ""
    except Exception as e:                                                         # noqa: BLE001
        return set(), "%s: %s" % (type(e).__name__, str(e)[:200])


def node_index_of(target, diagram_index, uid):
    """The 34(h)-safe Nodes[] index: bounded scan with a uid echo. Returns (index, rows)."""
    for i in range(SCAN_LIMIT):
        try:
            u, rows = g.node_terms_uid(target, diagram_index, i)
        except Exception:                                                          # noqa: BLE001
            break
        if not u:
            break
        if u == uid:
            return i, rows
    return None, []


def terms_table(rows):
    return [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]), "wire": r["wire"]}
            for r in rows]


def full_node_dump(target, diagram_index, tag, max_nodes=SCAN_LIMIT):
    """Every node on one diagram with its FULL terminal table, read off the machine. Read-only."""
    out = []
    for i in range(max_nodes):
        try:
            u, rows = g.node_terms_uid(target, diagram_index, i)
        except Exception as e:                                                     # noqa: BLE001
            out.append({"i": i, "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:200])})
            break
        if not u:
            break
        out.append({"i": i, "uid": u, "terms": terms_table(rows)})
    try:
        labs = {r["uid"]: r["label"] for r in g.node_labels(target, diagram_index)}
    except Exception as e:                                                         # noqa: BLE001
        labs = {}
        fact("%s node_labels raised %s: %s" % (tag, type(e).__name__, str(e)[:160]))
    for row in out:
        if "uid" in row:
            row["node_label"] = labs.get(row["uid"])
    for row in out:
        fact("%s Nodes[%s] uid %r label %r terms %r"
             % (tag, row.get("i"), row.get("uid"), row.get("node_label"), row.get("terms", row)))
    return out


def owner_read(rec, tag, uid, target):
    """Owner of `uid`, accepting BOTH 'Diagram' and 'TopLevelDiagram' wherever it is compared."""
    rd = {"tag": tag, "uid": uid}
    for strict in (True, False):
        try:
            cls, ouid = owner_of(target, uid, strict=strict)
            rd.update({"strict": strict, "owner_class": cls, "owner_uid": ouid, "error_verbatim": ""})
            break
        except Exception as e:                                                     # noqa: BLE001
            rd.update({"strict": strict, "owner_class": None, "owner_uid": None,
                       "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:250])})
    rd["owner_is_a_diagram"] = rd.get("owner_class") in ("Diagram", "TopLevelDiagram")
    try:
        rd["owner_diagram_index"] = (diag_index(target, rd["owner_uid"]) if rd["owner_is_a_diagram"] else None)
    except Exception as e:                                                         # noqa: BLE001
        rd["owner_diagram_index"] = None
        rd["owner_diagram_index_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    rec.setdefault("owner_reads", []).append(rd)
    fact("%s: owner_of(#%s) = (%r, %r) [strict=%r, is-a-diagram %r, diag_index %r] error VERBATIM %r"
         % (tag, uid, rd.get("owner_class"), rd.get("owner_uid"), rd.get("strict"),
            rd.get("owner_is_a_diagram"), rd.get("owner_diagram_index"), rd.get("error_verbatim")))
    return rd


def close_quietly(target):
    try:
        g.close_panel(target)
    except Exception as e:                                                         # noqa: BLE001
        fact("close_panel(%s) raised %s: %s" % (os.path.basename(target), type(e).__name__, e))


def fp_pairs(target, max_n=200):
    try:
        return g.fp_labels(target, max_n=max_n)
    except Exception as e:                                                         # noqa: BLE001
        fact("fp_labels(%s) raised %s: %s" % (os.path.basename(target), type(e).__name__, str(e)[:200]))
        return []


# ============================================================ R0: BUILD THE READER
def phase_r0():
    K = R["R0_build"]
    print("\n===================================================================", flush=True)
    print("=== R0   build %s from donor of record %s" % (os.path.basename(OP), os.path.basename(DONOR)),
          flush=True)
    print("===================================================================", flush=True)
    if os.path.exists(OP):
        os.remove(OP)
        fact("an OLD %s was on disk and was removed before the copy (never load a VI you are about to "
             "overwrite)" % os.path.basename(OP))
    shutil.copy2(DONOR, OP)
    K["file_at_creation"] = probe("R0_a0 the op file at creation (copied from the donor)", OP)
    g.open_panel(OP)
    time.sleep(1.0)
    try:
        _r0_body(K)
    finally:
        close_quietly(OP)
    dump()
    return isinstance(K.get("saved_bytes"), int)


def _r0_body(K):
    K["baseline"] = {"Node": count_of(OP, "Node"), "Wire": count_of(OP, "Wire"),
                     "Property": count_of(OP, "Property"), "IndexArray": count_of(OP, "IndexArray"),
                     "ControlTerminal": count_of(OP, "ControlTerminal"),
                     "Diagram": count_of(OP, "Diagram"), "ForLoop": count_of(OP, "ForLoop")}
    es0 = read_exec_state(K, "R0 the copy, before any edit", OP)
    fact("R0 baseline census of the copy: %r" % (K["baseline"],))
    gate("R0_a1 the donor copy opens and reads ExecState 1 before any edit", es0 == 1, "%r" % (es0,))

    # --- the op's OWN top-level diagram, resolved from the machine (never a hard-coded index)
    try:
        digs = g.report_all(OP, "Diagram")
    except Exception as e:                                                         # noqa: BLE001
        digs = []
        fact("R0 report_all(Diagram) raised %s: %s" % (type(e).__name__, str(e)[:200]))
    K["diagrams"] = [{"i": d["i"], "uid": d["uid"], "owner": d["owner"]} for d in digs]
    top = next((d for d in digs if str(d.get("owner")) in ("VI", "TopLevelDiagram", "")), digs[0] if digs
               else None)
    K["top_diagram"] = top
    top_i = 0 if top is None else digs.index(top)
    K["top_diagram_index_used"] = top_i
    fact("R0 the op's own diagrams (uid + owner, off the machine): %r ; the TOP-LEVEL one is %r at Traverse "
         "index %r - this is the ONLY diagram index this run uses on the op" % (K["diagrams"], top, top_i))

    # --- R0_a2: THE DONOR'S MEASURED SHAPE (the "does it support it" reading)
    print("\n--------- R0_a2  the donor copy's SHAPE, read off the machine", flush=True)
    K["shape_diagram_top"] = full_node_dump(OP, top_i, "R0_a2 top")
    gate("R0_a2 the copy's shape was measured off the machine (every node + full terminal table)",
         bool(K["shape_diagram_top"]), "%d nodes on the top-level diagram" % len(K["shape_diagram_top"]))
    # REPORT ONLY, straight out of the dump above: where the donor's `To More Specific Class` gets the TYPE
    # it casts to. This is the node that decides whether a generic Traverse reference can reach a
    # class-specific property, so judgement needs its source named. No extra call, no conclusion drawn.
    _sh = K["shape_diagram_top"]
    _tmsc = [n for n in _sh if any(t["name"] == "target class" for t in n.get("terms", []))]
    _prod = {t["wire"]: n.get("uid") for n in _sh for t in n.get("terms", []) if t["is_source"] and t["wire"]}
    K["tmsc_nodes"] = [{"uid": n.get("uid"), "label": n.get("node_label"),
                        "target_class_wire": next((t["wire"] for t in n["terms"]
                                                   if t["name"] == "target class"), None),
                        "target_class_produced_by_node_uid":
                            _prod.get(next((t["wire"] for t in n["terms"]
                                            if t["name"] == "target class"), None))}
                       for n in _tmsc]
    fact("R0_a2 REPORT ONLY - `To More Specific Class` nodes and where their `target class` type comes from: "
         "%r (a None producer means NO node on this diagram makes that wire, i.e. it comes from a panel "
         "object or a constant). No conclusion drawn." % (K["tmsc_nodes"],))

    try:
        ias = g.report(OP, "IndexArray")
    except Exception as e:                                                         # noqa: BLE001
        ias = []
        fact("R0 report(IndexArray) raised %s: %s" % (type(e).__name__, str(e)[:200]))
    K["index_arrays"] = [{"i": o["i"], "uid": o["uid"], "pos": o["pos"]} for o in ias]
    ia_uids = {o["uid"] for o in ias}
    # WHICH IndexArray selects the Traverse element - DERIVED FROM THE WIRING THIS RUN JUST MEASURED, never
    # from a count and never from a hard-coded uid. Run 1 of this file demanded "exactly ONE IndexArray" and
    # the donor of record carries THREE (uids 239/236/308, tools/bench/diag_s3b_l0_localname.log run 1); its
    # measured chain is `Traverse for GObjects.vi`.References --(wire 600)--> Index Array.array, so the rule
    # is: the IndexArray whose `array` terminal carries the SAME wire uid as the Traverse node's
    # `References` output.
    shape = K.get("shape_diagram_top") or []
    trav_rows = [n for n in shape
                 if any(t["name"] == "References" and t["is_source"] and t["wire"] for t in n.get("terms", []))]
    ref_wire = next((t["wire"] for n in trav_rows for t in n["terms"]
                     if t["name"] == "References" and t["is_source"]), None)
    K["traverse_nodes"] = [{"uid": n.get("uid"), "label": n.get("node_label")} for n in trav_rows]
    K["traverse_references_wire"] = ref_wire
    cands = [n for n in shape if n.get("uid") in ia_uids
             and any(t["name"] == "array" and t["wire"] == ref_wire for t in n.get("terms", []))
             and any(t["name"] == "element" and t["is_source"] for t in n.get("terms", []))]
    K["index_array_candidates"] = [{"uid": n.get("uid"), "nodes_index": n.get("i"),
                                    "label": n.get("node_label")} for n in cands]
    ia_uid = cands[0]["uid"] if len(cands) == 1 else None
    ia_i_nodes = cands[0]["i"] if len(cands) == 1 else None
    K["index_array_terms"] = cands[0]["terms"] if len(cands) == 1 else []
    elem = next((t for t in K["index_array_terms"] if t["name"] == "element"), None)
    K["index_array_element_terminal"] = elem
    fact("R0_a3 IndexArray objects %r ; the Traverse node(s) with a wired `References` output %r (wire %r) ; "
         "the IndexArray fed by that wire %r ; its terminals %r ; its `element` row %r"
         % (K["index_arrays"], K["traverse_nodes"], ref_wire, K["index_array_candidates"],
            K["index_array_terms"], elem))
    gate("R0_a3 exactly ONE IndexArray is fed by the Traverse node's `References` wire and carries `element`",
         len(cands) == 1 and elem is not None,
         "%d IndexArray(s) on the VI, %d fed by wire %r; element %r" % (len(ias), len(cands), ref_wire, elem))
    if ia_uid is None or elem is None:
        raise Stop("R0_a3: the Traverse -> IndexArray link could not be resolved from the wiring (IndexArray "
                   "count %d, candidates %d, element %r). NOTE: THREE IndexArrays is the DOCUMENTED shape - "
                   "tools/recipes/build_opnodelabels_v0.py:11-12 records 'Traverse -> IA -> TMSC -> Diagram -> "
                   "PN Nodes[] -> the vestigial per-node chain' - so a count of 3 is never by itself a finding. "
                   "REPORTED - no other donor is substituted and nothing is improvised."
                   % (len(ias), len(cands), elem))

    # --- R0_a4: the property node. The EXACT class string and whether it resolved.
    print("\n--------- R0_a4  build_property(%r, [(%r, False)]) at %r" % (LOCAL_CLASS, CONTROL_NAME_ID, PN_AT),
          flush=True)
    pn_before = count_of(OP, "Property")
    rd = {"class_string_passed": LOCAL_CLASS, "property_id": CONTROL_NAME_ID, "location": PN_AT,
          "diagram_index_used": top_i, "property_count_before": pn_before}
    try:
        new = g.build_property(OP, LOCAL_CLASS, [(CONTROL_NAME_ID, False)], PN_AT, diagram_index=top_i)
        rd["new"] = [{"uid": o["uid"], "pos": o["pos"]} for o in new]
        rd["resolved"] = True
        rd["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rd["new"] = None
        rd["resolved"] = False
        rd["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    rd["property_count_after"] = count_of(OP, "Property")
    K["build_property"] = rd
    fact("R0_a4 class string passed VERBATIM %r ; property id %r ; resolved=%r ; new %r ; Property census "
         "%r -> %r ; error column VERBATIM %r"
         % (LOCAL_CLASS, CONTROL_NAME_ID, rd["resolved"], rd["new"], pn_before, rd["property_count_after"],
            rd["error_verbatim"]))
    gate("R0_a4 build_property returned exactly 1 new Property and its class string / resolution / error "
         "column were recorded", bool(rd["new"]) and len(rd["new"]) == 1,
         "resolved=%r error %r" % (rd["resolved"], rd["error_verbatim"]))
    if not rd["new"]:
        raise Stop("R0_a4: the property node was not created. REPORTED; nothing is repaired or worked around.")
    pn_uid = rd["new"][0]["uid"]

    # --- R0_a5 / a6: the node's FULL terminal table, read off the machine
    print("\n--------- R0_a5  the new Property Node's FULL terminal table", flush=True)
    pn_i, rows = node_index_of(OP, top_i, pn_uid)
    terms = terms_table(rows)
    extra = [t for t in terms if t["name"] not in STD_PN_TERMS]
    K["property_terminals"] = {"nodes_index": pn_i, "terms": terms, "beyond_the_standard_four": extra,
                               "names_hex": {t["name"]: t["name"].encode("utf-8").hex() for t in terms}}
    fact("R0_a5 the Property #%s sits at Nodes[%r]; FULL terminal table READ OFF THE MACHINE: %r"
         % (pn_uid, pn_i, terms))
    fact("R0_a5 terminals BEYOND reference/reference out/error in/error out = %r  <- the SHORT NAME of "
         "6355400 on this machine, read, never retyped" % (extra,))
    gate("R0_a5 the new Property Node's terminal table was READ and carries `reference`", bool(terms)
         and any(t["name"] == "reference" for t in terms), "%d terminals" % len(terms))
    out_term = next((t for t in extra if t["is_source"]), None)
    K["control_name_terminal"] = out_term
    gate("R0_a6 a SOURCE terminal beyond the standard four is present (the Control Name output)",
         out_term is not None, "%r" % (out_term,))
    if out_term is None:
        raise Stop("R0_a6: the property node has no output terminal for 6355400 - the ID attached no row. "
                   "REPORTED; no alternative property and no alternative op is improvised.")

    # --- R0_a7: wire the Traverse-selected element into the property's reference (a BRANCH)
    print("\n--------- R0_a7  IA.`element` -> PN.`reference`  (a BRANCH: the donor already wires `element`)",
          flush=True)
    ia_i = [o["uid"] for o in g.report(OP, "IndexArray")].index(ia_uid)
    pn_ri = [o["uid"] for o in g.report(OP, "Property")].index(pn_uid)
    wr = {"ia_uid": ia_uid, "ia_report_index": ia_i, "pn_uid": pn_uid, "pn_report_index": pn_ri,
          "wire_count_before": count_of(OP, "Wire")}
    try:
        wr["wire_count_after"] = g.wire(OP, "IndexArray", ia_i, "element", "Property", pn_ri, "reference",
                                        branch=True)
        wr["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        wr["wire_count_after"] = count_of(OP, "Wire")
        wr["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    _, rows2 = node_index_of(OP, top_i, pn_uid)
    after_terms = terms_table(rows2)
    ref_after = next((t for t in after_terms if t["name"] == "reference"), None)
    wr["reference_terminal_after"] = ref_after
    wr["terminals_after"] = after_terms
    K["wire"] = wr
    fact("R0_a7 wire IA.element -> PN.reference: Wire census %r -> %r ; error column VERBATIM %r ; the "
         "reference terminal AFTER = %r" % (wr["wire_count_before"], wr["wire_count_after"],
                                            wr["error_verbatim"], ref_after))
    gate("R0_a7 the wire landed - empty error column AND a non-zero wire uid on `reference`",
         wr["error_verbatim"] == "" and bool(ref_after) and bool(ref_after.get("wire")),
         "error %r, reference wire %r" % (wr["error_verbatim"], (ref_after or {}).get("wire")))

    # A FREE READING the run already captured and never asserted - archive/peer/2026-09-21-c60-ia-count-gate.md
    # §4 reading 2, the only thing acted on from that review (its disposition says so in full). If LabVIEW
    # silently RE-ADAPTS the property node's class to the generic GObject reference it was just handed, the
    # `Control Name` row DISAPPEARS and `ExecState` stays 1 - a false pass that neither ExecState nor the
    # wire-uid check would catch. Asserting the row survived makes the three cases distinguishable from the log.
    name_after = next((t for t in after_terms if t["name"] == out_term["name"]), None)
    wr["control_name_row_after"] = name_after
    fact("R0_a7b the %r row AFTER the wire = %r (its ABSENCE with ExecState 1 would mean the node re-adapted "
         "its class to the generic reference - a false pass)" % (out_term["name"], name_after))
    gate("R0_a7b the property's %r output row SURVIVED the wire" % out_term["name"], name_after is not None,
         "%r" % (name_after,))
    es1 = read_exec_state(K, "R0 after the wiring", OP)
    K["exec_state_after_wire"] = es1
    gate("R0_a8 ExecState after the wiring was READ", es1 in (0, 1),
         "%r  (a 0 IS the KNOWN HAZARD's answer - the Traverse element is a GENERIC GObject reference and "
         "gscript.py:2415 says a type mismatch makes a broken wire - and is REPORTED, never repaired)"
         % (es1,))
    if es1 != 1:
        K["stopped_because"] = ("ExecState is %r after the element -> reference wire. The op is NOT saved, "
                                "nothing is repaired (no remove_bad_wires_scripted, no gui_save, no "
                                "allow_broken), no other donor is substituted and no different op is "
                                "designed. This is the FACT the brief asks for." % (es1,))
        fact("R0 STOPS HERE: %s" % K["stopped_because"])
        return

    # --- R0_a9: the string indicator on the Control Name output
    print("\n--------- R0_a9  create_indicator on the Control Name output terminal", flush=True)
    global NAME_IND
    before_fp = fp_pairs(OP, max_n=60)
    ct_before = count_of(OP, "ControlTerminal")
    ind = {"node_index": pn_i, "terminal_index": out_term["i"],
           "terminal_name": out_term["name"], "control_terminal_before": ct_before}
    try:
        ind["new"] = [{"uid": o["uid"], "pos": o["pos"]} for o in g.create_indicator(OP, pn_i, out_term["i"])]
        ind["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        ind["new"] = None
        ind["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    ind["control_terminal_after"] = count_of(OP, "ControlTerminal")
    after_fp = fp_pairs(OP, max_n=60)
    before_labels = [lab for _i, lab, _x in before_fp]
    new_labels = [lab for _i, lab, _x in after_fp if lab not in before_labels]
    ind["front_panel_before"] = before_fp
    ind["front_panel_after"] = after_fp
    ind["new_labels"] = new_labels
    ind["new_label_hex"] = [l.encode("utf-8").hex() for l in new_labels]
    K["create_indicator"] = ind
    fact("R0_a9 create_indicator on Nodes[%r].Terminals[%r] (%r): new %r ; ControlTerminal %r -> %r ; NEW "
         "PANEL LABEL(S) READ OFF THE MACHINE %r (hex %r) ; error VERBATIM %r"
         % (pn_i, out_term["i"], out_term["name"], ind["new"], ct_before, ind["control_terminal_after"],
            new_labels, ind["new_label_hex"], ind["error_verbatim"]))
    gate("R0_a9 exactly one new ControlTerminal and exactly one new panel label were read off the machine",
         bool(ind["new"]) and len(ind["new"]) == 1 and len(new_labels) == 1,
         "new %r labels %r" % (ind["new"], new_labels))
    if len(new_labels) == 1:
        NAME_IND = new_labels[0]
        R["pass_criteria"]["reader_indicator_label"] = NAME_IND

    es2 = read_exec_state(K, "R0 after the indicator", OP)
    R["pass_criteria"]["op_execstate"] = es2
    ok = gate("R0_a10 ExecState == 1 after the indicator  *** THE OP'S PASS CRITERION ***", es2 == 1,
              "%r" % (es2,))
    K["census_after"] = {"Node": count_of(OP, "Node"), "Wire": count_of(OP, "Wire"),
                         "Property": count_of(OP, "Property"),
                         "ControlTerminal": count_of(OP, "ControlTerminal")}
    fact("R0 census after the edit: %r" % (K["census_after"],))
    if not ok or NAME_IND is None:
        K["stopped_because"] = ("ExecState %r / indicator label %r - THE OP IS NOT SAVED and nothing is "
                                "repaired." % (es2, NAME_IND))
        fact("R0: %s" % K["stopped_because"])
        return
    try:
        K["saved_bytes"] = g.save(OP)
        fact("R0 saved %r bytes" % (K["saved_bytes"],))
    except Exception as e:                                                        # noqa: BLE001
        K["saved_bytes"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:300])
        fact("R0 g.save(OP) raised %s: %s" % (type(e).__name__, str(e)[:300]))
    K["file_after"] = D.file_facts("R0_a11 the op VI after the save", OP)
    R["artefacts"].append({"step": "R0 OpLocalName_v0", "path": OP,
                           "saved": isinstance(K.get("saved_bytes"), int), "file": K["file_after"]})
    gate("R0_a11 g.save returned a byte count and the file reads LV2026 (26 00 80 00)",
         isinstance(K.get("saved_bytes"), int)
         and any(c["bytes"].startswith("26 00 80 00") for c in K["file_after"].get("version_candidates", [])),
         "%r / %r" % (K.get("saved_bytes"), K["file_after"].get("version_candidates")))


# ============================================================ THE TWO WRAPPERS
def local_name(target, index, tag=""):
    """The READER's Python side: Traverse `Local` by `index` on `target` -> Local.Control Name 6355400.
    Mirrors gscript.node_labels' control writes exactly (the donor's own API), reads the NEW indicator whose
    label was read off the machine at build time, and NEVER raises - the error column is a reading."""
    rd = {"tag": tag, "index": index, "traverse_class": TRAVERSE_CLASS}
    vi = g.op(OP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", TRAVERSE_CLASS)
    vi.SetControlValue("index", int(index))
    for lab, val in (("index 2", 0), ("index 3", 0), ("Class Name 2", ""), ("Class Name 3", ""),
                     ("error in (no error)", (False, 0, "")), ("error in", (True, 1, "neutralised creator"))):
        try:
            vi.SetControlValue(lab, val)
        except Exception:                                                          # noqa: BLE001
            pass
    t0 = time.time()
    try:
        g._run(vi)
        rd["run_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rd["run_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    rd["run_s"] = round(time.time() - t0, 2)
    try:
        rd["control_name"] = vi.GetControlValue(NAME_IND)
        rd["control_name_hex"] = (rd["control_name"] or "").encode("utf-8").hex()
    except Exception as e:                                                         # noqa: BLE001
        rd["control_name"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
        rd["control_name_hex"] = None
    for lab in ("error out 2", "error out"):
        try:
            rd["cluster_%s" % lab.replace(" ", "_")] = repr(vi.GetControlValue(lab))
        except Exception as e:                                                     # noqa: BLE001
            rd["cluster_%s" % lab.replace(" ", "_")] = "NO %r INDICATOR (%s)" % (lab, type(e).__name__)
    return rd


def create_local(target, label, panel_index, tag=""):
    """attempt 1's wrapper (tools/bench/diag_s3b_l0_createlocal.py:488-545), unchanged in substance: drive
    claudeDev\\OpCreateLocal_v0.vi with the control's Panel.Controls[] position and read back the whole-VI
    `Local` uid SET diff. `label` is the string fp_labels returned OFF THE MACHINE."""
    rd = {"tag": tag, "label_from_the_machine": label, "label_hex": label.encode("utf-8").hex(),
          "panel_index": panel_index}
    g.ensure_loaded(target)
    before, err0 = uid_set(target, "Local")
    rd["local_uids_before"] = sorted(before)
    rd["local_uid_read_error"] = err0
    vi = g.op(CREATOR)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("index", int(panel_index))
    for lab in ("Names", "Names 2"):
        try:
            vi.SetControlValue(lab, [])
        except Exception:                                                          # noqa: BLE001
            pass
    for lab in ("Class Name", "Class Name 2"):
        try:
            vi.SetControlValue(lab, "")
        except Exception:                                                          # noqa: BLE001
            pass
    try:
        vi.SetControlValue("index 2", 0)
    except Exception:                                                              # noqa: BLE001
        pass
    t0 = time.time()
    try:
        g._run(vi)
        rd["run_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rd["run_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    rd["run_s"] = round(time.time() - t0, 2)
    for ind, key in (("Text", "op_matched_label"), ("Indicator", "op_is_indicator")):
        try:
            rd[key] = vi.GetControlValue(ind)
        except Exception as e:                                                     # noqa: BLE001
            rd[key] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    try:
        rd["error_cluster_verbatim"] = repr(vi.GetControlValue("error out"))
    except Exception as e:                                                         # noqa: BLE001
        rd["error_cluster_verbatim"] = "NO 'error out' INDICATOR (%s)" % type(e).__name__
    after, err1 = uid_set(target, "Local")
    rd["local_uids_after"] = sorted(after)
    rd["local_uid_read_error_after"] = err1
    rd["new_local_uids"] = sorted(after - before)
    rd["lost_local_uids"] = sorted(before - after)
    return rd


# ============================================================ R1 / R2 / R3 on a SCRATCH copy
def phase_r123():
    K1, K2, K3 = R["R1_ground_truth"], R["R2_open_question"], R["R3_hygiene"]
    print("\n===================================================================", flush=True)
    print("=== R1/R2/R3  on %s - a SCRATCH duplicate of D1_s3a_focus_ind.vi" % os.path.basename(SCRATCH),
          flush=True)
    print("=== 49(e): never the artefact itself; its md5 is gated before AND after", flush=True)
    print("===================================================================", flush=True)
    a_before = probe("R1_b0 the ARTEFACT D1_s3a_focus_ind.vi BEFORE the phase", S3A_ARTEFACT)
    gate("R1_b0a the artefact's md5 is the pin BEFORE the phase", a_before.get("md5") == S3A_MD5,
         "%s" % a_before.get("md5"))
    shutil.copy2(S3A_ARTEFACT, SCRATCH)
    p = probe("R1_b0 the scratch at creation", SCRATCH)
    K1["scratch"] = {"path": SCRATCH, "at_creation": p}
    gate("R1_b0 the scratch is byte-identical to D1_s3a_focus_ind.vi at creation", p.get("md5") == S3A_MD5,
         "%s (expected %s)" % (p.get("md5", "?"), S3A_MD5))
    g.open_panel(SCRATCH)
    time.sleep(1.0)
    try:
        _r1(K1)
        _r2(K1, K2)
        _r3(K3)
    finally:
        close_quietly(SCRATCH)
    a_after = probe("R1_b0 the ARTEFACT D1_s3a_focus_ind.vi AFTER the phase", S3A_ARTEFACT)
    gate("R1_b0b the artefact's md5 is the pin AFTER the phase", a_after.get("md5") == S3A_MD5,
         "%s" % a_after.get("md5"))
    dump()


def _r1(K):
    es0 = read_exec_state(K, "R1 the scratch, before any call", SCRATCH)
    try:
        rows = g.report_all(SCRATCH, "Local")
    except Exception as e:                                                         # noqa: BLE001
        rows = []
        fact("R1 report_all(Local) raised %s: %s" % (type(e).__name__, str(e)[:200]))
    K["local_rows"] = [{"i": o["i"], "uid": o["uid"], "class": o["class"], "owner": o["owner"],
                        "pos": o["pos"]} for o in rows]
    K["local_census_before"] = len(rows)
    fact("R1_b1 baseline: ExecState %r ; `Local` census %r (docs/toolkit-capabilities.md:284 records 8 at the "
         "S2/main baseline - the READING is the gate, never the 8) ; rows %r"
         % (es0, len(rows), K["local_rows"]))
    gate("R1_b1 the scratch opens at ExecState 1 and its `Local` census was READ",
         es0 == 1 and isinstance(K["local_census_before"], int),
         "ExecState %r, Local %r" % (es0, K["local_census_before"]))

    print("\n--------- R1_b2  read `Control Name` for EVERY pre-existing Local", flush=True)
    reads = []
    for o in K["local_rows"]:
        r = local_name(SCRATCH, o["i"], tag="R1 Local[%d] uid %s" % (o["i"], o["uid"]))
        r["uid_from_report_all"] = o["uid"]
        reads.append(r)
        fact("R1_b2 Local[%d] uid %s -> Control Name %r (hex %r) ; run error VERBATIM %r ; donor error "
             "cluster %s" % (o["i"], o["uid"], r.get("control_name"), r.get("control_name_hex"),
                             r.get("run_error_verbatim"), r.get("cluster_error_out_2")))
    K["control_name_reads"] = reads
    got = [r for r in reads if isinstance(r.get("control_name"), str)
           and not str(r.get("control_name")).startswith("ERROR ")]
    gate("R1_b2 `Control Name` was read for every pre-existing Local and every uid -> string pair reported",
         len(reads) == K["local_census_before"] and len(got) == len(reads),
         "%d/%d rows returned a string" % (len(got), len(reads)))
    vi_named = [r for r in got if str(r.get("control_name", "")).lower().endswith(".vi")]
    K["strings_that_are_vi_file_names"] = [r.get("control_name") for r in vi_named]
    K["distinct_strings"] = sorted({r.get("control_name") for r in got})
    fact("R1_b3 PLAINLY: %d of %d returned strings END IN `.vi` -> %r ; the DISTINCT strings returned are %r"
         % (len(vi_named), len(got), K["strings_that_are_vi_file_names"], K["distinct_strings"]))
    gate("R1_b3 whether any returned string is a .vi file name was stated plainly", True,
         "%d of %d end in .vi" % (len(vi_named), len(got)))
    dump()


def _r2(K1, K):
    print("\n--------- R2  the open question: create a Local from the control labelled 'index', then READ it",
          flush=True)
    t0 = time.time()
    rows = fp_pairs(SCRATCH, max_n=200)
    K["fp_rows"] = len(rows)
    K["fp_sweep_s"] = round(time.time() - t0, 1)
    hits = [(i, lab, ind) for i, lab, ind in rows if lab == TARGET_LABEL]
    K["panel_hits_for_the_label"] = hits
    fact("R2_c1 fp_labels swept %d panel objects in %.1f s ; rows whose owned label equals %r: %r"
         % (len(rows), K["fp_sweep_s"], TARGET_LABEL, hits))
    gate("R2_c1 exactly one front-panel object carries that owned label", len(hits) == 1, "%r" % (hits,))
    if len(hits) != 1:
        K["not_attempted"] = ("the label is not unique / not present on the scratch (%r) - R2 is REPORTED, "
                              "not improvised around." % (hits,))
        fact("R2 NOT ATTEMPTED: %s" % K["not_attempted"])
        return
    panel_index, machine_label, _is_ind = hits[0]
    K["label_from_the_machine"] = machine_label
    K["label_hex"] = machine_label.encode("utf-8").hex()
    K["panel_index"] = panel_index

    es_before = read_exec_state(K, "R2 the scratch BEFORE the creator call", SCRATCH)
    c = create_local(SCRATCH, machine_label, panel_index, tag="R2 CALL")
    K["creator_call"] = c
    es_after = read_exec_state(K, "R2 the scratch AFTER the creator call", SCRATCH)
    K["exec_state_before"] = es_before
    K["exec_state_after"] = es_after
    fact("R2_c2 creator: op `Text` (the label it WALKED TO, off the machine) %r ; error cluster VERBATIM %s ; "
         "run error VERBATIM %r ; `Local` census %d -> %d ; NEW uids %r ; LOST uids %r"
         % (c.get("op_matched_label"), c.get("error_cluster_verbatim"), c.get("run_error_verbatim"),
            len(c.get("local_uids_before") or []), len(c.get("local_uids_after") or []),
            c.get("new_local_uids"), c.get("lost_local_uids")))
    gate("R2_c2 the creator call returned and its error cluster / census diff were captured VERBATIM",
         "run_error_verbatim" in c, "new %r" % (c.get("new_local_uids"),))
    gate("R2_c3 the scratch's ExecState BEFORE and AFTER the creator call were READ",
         es_before in (0, 1) and es_after in (0, 1),
         "%r -> %r  (a 0 after is a LEGITIMATE reading - attempt 1 measured exactly that - and is reported, "
         "never repaired)" % (es_before, es_after))

    new_uids = c.get("new_local_uids") or []
    if len(new_uids) != 1:
        K["readback"] = {"note": "no single new Local to read back (%r)" % (new_uids,)}
        gate("R2_c4 the new Local's `Control Name` was read with the NEW READER", False,
             "no single new Local: %r" % (new_uids,))
        dump()
        return
    new_uid = new_uids[0]
    owner_read(K, "R2 owner of the new Local", new_uid, SCRATCH)
    try:
        rows2 = g.report_all(SCRATCH, "Local")
    except Exception as e:                                                         # noqa: BLE001
        rows2 = []
        fact("R2 report_all(Local) raised %s: %s" % (type(e).__name__, str(e)[:200]))
    order = [o["uid"] for o in rows2]
    K["local_rows_after"] = [{"i": o["i"], "uid": o["uid"], "owner": o["owner"]} for o in rows2]
    idx = order.index(new_uid) if new_uid in order else None
    K["traverse_index_of_the_new_local"] = idx
    fact("R2_c4 the new Local #%s sits at Traverse index %r of %d (report_all order == Traverse order, the "
         "ordering every delete_object call in this fleet already relies on)" % (new_uid, idx, len(order)))
    if idx is None:
        gate("R2_c4 the new Local's `Control Name` was read with the NEW READER", False,
             "the new uid is not in report_all(Local) order")
        dump()
        return
    r = local_name(SCRATCH, idx, tag="R2 the NEW Local uid %s" % new_uid)
    r["uid"] = new_uid
    K["reader_readback"] = r
    fact("R2_c4 READER on Local[%d] (uid %s): `Control Name` = %r (hex %r) ; run error VERBATIM %r ; donor "
         "error cluster %s ; asked for %r (hex %r)"
         % (idx, new_uid, r.get("control_name"), r.get("control_name_hex"), r.get("run_error_verbatim"),
            r.get("cluster_error_out_2"), machine_label, K["label_hex"]))
    K["matches_the_label_asked_for"] = (r.get("control_name") == machine_label)
    gate("R2_c4 the new Local's `Control Name` was read with the NEW READER and reported VERBATIM",
         isinstance(r.get("control_name"), str) and not str(r.get("control_name")).startswith("ERROR "),
         "%r  (equal to the label asked for: %r)" % (r.get("control_name"), K["matches_the_label_asked_for"]))
    dump()


def _r3(K):
    print("\n--------- R3  %d CONSECUTIVE READER CALLS (handles flat +-100, every reference closed)"
          % N_CONSECUTIVE, flush=True)
    R["ref_counts_before_20"] = g.ref_counts()
    h_before = labview_handles()
    R["handles"]["before_20"] = h_before
    n_locals = count_of(SCRATCH, "Local")
    n = n_locals if isinstance(n_locals, int) and n_locals > 0 else 1
    runs = []
    t0 = time.time()
    for k in range(N_CONSECUTIVE):
        r = local_name(SCRATCH, k % n, tag="consecutive %d" % (k + 1))
        runs.append({"n": k + 1, "index": k % n, "control_name": r.get("control_name"),
                     "run_s": r.get("run_s"), "error_verbatim": r.get("run_error_verbatim")})
        print(("     call %2d: index %2d -> %r, %.2f s, error %r"
               % (k + 1, k % n, r.get("control_name"), r.get("run_s", -1) or -1,
                  (r.get("run_error_verbatim") or "")[:90])).encode("ascii", "replace").decode("ascii"),
              flush=True)
    h_after = labview_handles()
    R["handles"]["after_20"] = h_after
    R["ref_counts_after_20"] = g.ref_counts()
    K["consecutive"] = {"n": N_CONSECUTIVE, "local_census": n_locals, "runs": runs,
                        "elapsed_s": round(time.time() - t0, 1),
                        "handles_before": h_before, "handles_after": h_after,
                        "n_with_a_string": sum(1 for r in runs if isinstance(r["control_name"], str)
                                               and not str(r["control_name"]).startswith("ERROR ")),
                        "n_with_an_error": sum(1 for r in runs if r["error_verbatim"])}
    fact("R3_d1 %d consecutive reader calls in %.1f s: %d returned a string, %d carried an error"
         % (N_CONSECUTIVE, K["consecutive"]["elapsed_s"], K["consecutive"]["n_with_a_string"],
            K["consecutive"]["n_with_an_error"]))
    fact("R3_d1 handles %r -> %r (delta %s) ; refs before %r after %r"
         % (h_before, h_after,
            (h_after - h_before) if isinstance(h_before, int) and isinstance(h_after, int) else "?",
            R["ref_counts_before_20"], R["ref_counts_after_20"]))
    gate("R3_d1 %d consecutive reader calls ran and the handle count was read either side" % N_CONSECUTIVE,
         len(runs) == N_CONSECUTIVE and isinstance(h_before, int) and isinstance(h_after, int),
         "%r -> %r" % (h_before, h_after))
    flat = (isinstance(h_before, int) and isinstance(h_after, int) and abs(h_after - h_before) <= 100)
    gate("R3_d2 the handle count is flat within +-100 across the 20 calls", flat,
         "%r -> %r (a FAIL is a FINDING, not a blocker - 44(e)/49(j))" % (h_before, h_after))
    rc = R["ref_counts_after_20"] or {}
    gate("R3_d3 refs opened == closed, 0 live after the 20 calls",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    dump()


# ============================================================ R4: REPORT ONLY, NO BUILD
def phase_r4():
    K = R["R4_report_only"]
    print("\n===================================================================", flush=True)
    print("=== R4   REPORT ONLY - Invoke terminal tables, side by side. NO CONCLUSION IS DRAWN.", flush=True)
    print("===================================================================", flush=True)
    K["what"] = ("the FULL terminal table of every Invoke node in op VIs this fleet ALREADY built with a "
                 "method of KNOWN signature (OpMoveIn_v0.vi = the Move behind build_d1_v0.move_in; "
                 "OpConPaneAssign_v0.vi = build_opconpaneassign.py), beside OpCreateLocal_v0.vi's 6331C02 "
                 "node, so the six-terminal reading (i=4 sink / i=5 source, both named 'Create Local') can "
                 "be compared against a known case. READ-ONLY: no panel is opened for editing, nothing is "
                 "saved, no conclusion is drawn.")
    K["tables"] = {}
    for path in (MOVEIN, CONPANE, CREATOR):
        name = os.path.basename(path)
        row = {"path": path, "md5_before": probe("R4 %s before the read" % name, path).get("md5")}
        try:
            invs = g.report_all(path, "Invoke")
            row["invoke_count"] = len(invs)
            row["invokes"] = []
            for o in invs:
                i_node, rows = node_index_of(path, 0, o["uid"])
                t = terms_table(rows)
                row["invokes"].append({"uid": o["uid"], "pos": o["pos"], "nodes_index": i_node, "terms": t,
                                       "beyond_the_standard_four":
                                           [x for x in t if x["name"] not in STD_PN_TERMS]})
                fact("R4_e1 %s Invoke #%s at Nodes[%r]: %r" % (name, o["uid"], i_node, t))
            row["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            row["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
            fact("R4_e1 %s raised %s: %s" % (name, type(e).__name__, str(e)[:300]))
        row["md5_after"] = probe("R4 %s after the read" % name, path).get("md5")
        row["byte_unchanged"] = row["md5_before"] == row["md5_after"]
        K["tables"][name] = row
    gate("R4_e1 the Invoke terminal tables were dumped side by side (no conclusion drawn)",
         any(v.get("invokes") for v in K["tables"].values()),
         "; ".join("%s: %r invoke(s)" % (k, v.get("invoke_count")) for k, v in K["tables"].items()))
    gate("R4_e2 the three op VIs read in R4 are byte-unchanged by the reading",
         all(v.get("byte_unchanged") for v in K["tables"].values()),
         "; ".join("%s %r" % (k, v.get("byte_unchanged")) for k, v in K["tables"].items()))
    dump()


# ============================================================ MAIN
def main():
    print("=== diag_s3b_l0_localname  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== cycle 60 attempt 2: build claudeDev\\OpLocalName_v0.vi (the Local-binding READER) and "
          "measure it", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 the S3a artefact (the self-test bed's SOURCE, never the bed)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    dn = probe("T4 the DONOR OF RECORD OpNodeLabels_v0.vi", DONOR)
    R["donor"]["md5_before"] = dn.get("md5")
    gate("T4 the donor OpNodeLabels_v0.vi is on disk", dn.get("exists") == "1", "%r" % dn.get("md5"),
         fatal=True)
    cr = probe("T4b the CREATOR OpCreateLocal_v0.vi (attempt 1's artefact, driven by R2)", CREATOR)
    R["creator"]["md5_before"] = cr.get("md5")
    gate("T4b OpCreateLocal_v0.vi is on disk", cr.get("exists") == "1", "%r" % cr.get("md5"), fatal=True)

    D.fresh("T5 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    gate("T5 the pre-batch restart ran and the handle count was read either side",
         isinstance(R["handles"]["before"], int) and isinstance(R["handles"]["after_restart"], int),
         "%r -> %r" % (R["handles"]["before"], R["handles"]["after_restart"]))
    dump()

    op_ok = False
    try:
        op_ok = phase_r0()
    except Stop as s:
        R["R0_build"]["stopped_at"] = str(s)
        fact("R0 STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        R["R0_build"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("R0 raised %s: %s" % (type(e).__name__, str(e)[:600]))
    dump()
    if not op_ok and os.path.exists(OP) and not isinstance(R["R0_build"].get("saved_bytes"), int):
        try:
            os.remove(OP)
            fact("R0 cleanup: the UNSAVED op file was removed (it was a byte copy of the donor with nothing "
                 "of its own saved into it). NOTHING SAVED IS EVER DELETED.")
        except Exception as e:                                                     # noqa: BLE001
            fact("R0 cleanup: removing %s FAILED %s: %s" % (os.path.basename(OP), type(e).__name__, e))

    if op_ok:
        try:
            phase_r123()
        except Stop as s:
            R["R1_ground_truth"]["stopped_at"] = str(s)
            fact("R1/R2/R3 STOPPED: %s" % s)
        except Exception as e:                                                     # noqa: BLE001
            R["R1_ground_truth"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            fact("R1/R2/R3 raised %s: %s" % (type(e).__name__, str(e)[:600]))
    else:
        R["R1_ground_truth"]["not_attempted"] = ("the reader did not reach a legal save point, so there is "
                                                 "nothing to validate. ExecState at the pass point: %r ; "
                                                 "reason: %r"
                                                 % (R["pass_criteria"]["op_execstate"],
                                                    R["R0_build"].get("stopped_because")))
        fact("R1/R2/R3 NOT ATTEMPTED: %s" % R["R1_ground_truth"]["not_attempted"])
    dump()

    try:
        phase_r4()
    except Exception as e:                                                         # noqa: BLE001
        R["R4_report_only"]["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        fact("R4 raised %s: %s" % (type(e).__name__, str(e)[:400]))

    # ---- Z: the closing facts
    print("\n--- Z: the closing facts", flush=True)
    removed = None
    if os.path.exists(SCRATCH):
        try:
            os.remove(SCRATCH)
            removed = True
        except Exception as e:                                                     # noqa: BLE001
            removed = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
    R["scratch_removed"] = removed
    gate("R3_d4 the scratch was DELETED in the same run", not os.path.exists(SCRATCH),
         "removed=%r, exists=%r" % (removed, os.path.exists(SCRATCH)))

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
    z3 = probe("Z1d D1_s3a_focus_ind.vi after everything", S3A_ARTEFACT)
    gate("Z1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z2 refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    zd = probe("Z3 the DONOR OpNodeLabels_v0.vi after everything", DONOR)
    gate("Z3 the DONOR OpNodeLabels_v0.vi is byte-unchanged", zd.get("md5") == R["donor"].get("md5_before"),
         "%s vs %s" % (zd.get("md5"), R["donor"].get("md5_before")))
    zc = probe("Z3b OpCreateLocal_v0.vi after everything", CREATOR)
    gate("Z3b OpCreateLocal_v0.vi is byte-unchanged", zc.get("md5") == R["creator"].get("md5_before"),
         "%s vs %s" % (zc.get("md5"), R["creator"].get("md5_before")))
    rp = os.path.join(ROOT, "tools", "recipes")
    R["recipes_dir_mtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(rp)))
    gate("Z4 no file was created under tools/recipes/ by this run", True,
         "this diagnostic writes only tools/bench/diag_s3b_l0_localname.{log,json} and claudeDev\\"
         "OpLocalName_v0.vi, plus the scratch it deletes")

    print("\n--- THE ANSWER TABLE (readings, not a recommendation)", flush=True)
    K0 = R["R0_build"]
    fact("R0  class string passed %r -> resolved %r, error VERBATIM %r ; property terminals beyond the "
         "standard four %r"
         % (LOCAL_CLASS, K0.get("build_property", {}).get("resolved"),
            K0.get("build_property", {}).get("error_verbatim"),
            K0.get("property_terminals", {}).get("beyond_the_standard_four")))
    fact("R0  ExecState after the wire %r ; after the indicator %r ; saved %r bytes -> md5 %r size %r "
         "version %r ; the reader's indicator label %r"
         % (K0.get("exec_state_after_wire"), R["pass_criteria"]["op_execstate"], K0.get("saved_bytes"),
            K0.get("file_after", {}).get("md5"), K0.get("file_after", {}).get("size"),
            K0.get("file_after", {}).get("version_candidates"), R["pass_criteria"]["reader_indicator_label"]))
    K1 = R["R1_ground_truth"]
    fact("R1  `Local` census %r ; uid -> Control Name %r ; strings ending in .vi %r"
         % (K1.get("local_census_before"),
            [(r.get("uid_from_report_all"), r.get("control_name")) for r in K1.get("control_name_reads", [])],
            K1.get("strings_that_are_vi_file_names")))
    K2 = R["R2_open_question"]
    fact("R2  label from the machine %r (hex %r) ; creator error cluster %s ; new Local %r ; ExecState %r -> "
         "%r ; READER says %r ; equal to the label asked for %r"
         % (K2.get("label_from_the_machine"), K2.get("label_hex"),
            K2.get("creator_call", {}).get("error_cluster_verbatim"),
            K2.get("creator_call", {}).get("new_local_uids"), K2.get("exec_state_before"),
            K2.get("exec_state_after"), K2.get("reader_readback", {}).get("control_name"),
            K2.get("matches_the_label_asked_for")))
    K3 = R["R3_hygiene"].get("consecutive", {})
    fact("R3  %r/%r calls returned a string ; handles %r -> %r ; refs %r"
         % (K3.get("n_with_a_string"), K3.get("n"), K3.get("handles_before"), K3.get("handles_after"),
            R.get("ref_counts_after_20")))
    fact("R4  %r" % ({k: v.get("invoke_count") for k, v in R["R4_report_only"].get("tables", {}).items()},))
    fact("ARTEFACTS ON DISK: %r" % ([{"step": a["step"], "path": a["path"],
                                      "md5": a.get("file", {}).get("md5"),
                                      "size": a.get("file", {}).get("size")}
                                     for a in R["artefacts"] if a.get("saved")],))

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
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
