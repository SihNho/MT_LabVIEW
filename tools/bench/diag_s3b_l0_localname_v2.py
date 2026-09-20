"""diag_s3b_l0_localname_v2 - cycle 60 (attempt 2) material #2. BUILD `claudeDev\\OpLocalName_v0.vi`, the
one-property READER for a Local Variable's binding, THIS TIME WITH THE `To More Specific Class` CAST the
donor's own diagram already uses - and measure it.

A DIAGNOSTIC under tools/bench/, NEVER a recipe (48(n) / STATUS `## NEXT`: a RECIPE build is refused in any
cycle that has already produced a build log). Nothing under tools/recipes/ is written, renamed, copied or
launched by this file - gate Z4 lists that directory before and after.

THE JUDGEMENT DECISION THIS FILE EXECUTES (cycle 60, 2026-09-21) - not designed by this session:
  Material #1 measured the block exactly and it is ONE CAST WIDE. `build_property('VI Server:Local',
  [('6355400', False)])` RESOLVES (short name `CtrlName`, terminal i=4 SOURCE, Property census 7 -> 8;
  tools/bench/diag_s3b_l0_localname_run2.log:50-56) but feeding its `reference` straight from
  `Traverse for GObjects.vi` -> `Index Array .element` yields `ExecState` 0, because Traverse hands out a
  GENERIC GObject and `Control Name` is a `Local` property two classes down (Generic -> GObject -> Node ->
  Local). The donor `OpNodeLabels_v0.vi` ALREADY SOLVES THIS: it carries `To More Specific Class` #683
  between the Index Array and its property chain, seeded by wire 772, which NO node on that diagram produces
  (run 2 log :29-45).
  DECISION: build the reader with a TMSC cast to `Local`, FOLLOWING THE DONOR'S OWN MEASURED SEED MECHANISM.

AUTHORISATION FOR A NEW OP VI - 46(k) (`docs/cycle27-plan.md:1697-1705`), quoted in its own words:
  `docs/cycle27-plan.md:31` reads *"**No further process device** (user, 08:53) - still the standing order.
  A retrospective naming one is a finding."*  46(k): *"A **process device** is gate and retrospective
  machinery; an **op VI** is deliverable-construction tooling, and every stage of D1 so far was built with
  them ... So the order does not reach an op VI that places a Local Variable, and **the S3b transport needs
  no decision from the user**: if `Control -> Create:Local Variable` 6331C02 through `build_invoke` is the
  route, it is simply built."*
Reading `Local.Control Name` 6355400 is NOT route B (route B is *create* by `New VI Object` style 2061 PLUS a
WRITE to that property), so 49(d) does not fence it.
49(i), stated here in writing because the brief requires it:
*** THIS OP WILL BE REVISED ON ANY REVIEW THAT GATES IT. ***

WHAT ALREADY EXISTED - checked before a line of this was written (CLAUDE.md "check what exists before creating
anything": `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`, docs/toolkit-capabilities.md):
  * A CAST VERB DOES EXIST, and it is NOT usable for `Local` as it stands: `gscript.loop_cast(target, index,
    class_name)` at tools/gscript.py:626 (the peer named a "loop_cast pattern"; the NAME was verified against
    the file, not taken on trust). Its docstring: *"Cast-free seed: the op's TMSC 'target class' is fed by a
    ForLoop-refnum CONTROL created from erdosmiller Create For Loop.vi's typed output (NI: TMSC accepts any
    wire of the target type)"*, and it dispatches ONLY to claudeDev\\OpLoopCast_v0.vi / OpWhileCast_v0.vi,
    raising for any other class_name (`:645-646`). There is no `Local` op, so the VERB cannot read a Local.
  * ITS BUILDER IS THE MECHANISM OF RECORD: tools/recipes/build_oploopcast_v0.py:4-8 - *"To More Specific
    Class needs a 'target class' of the wanted type; we cannot make a class-specifier constant
    (docs/toolkit-capabilities.md 'the one missing seed'). But 'target class' is a refnum INPUT: any refnum
    WIRE of the wanted class types it. ... `Terminal.Create Control` makes a control OF THE TERMINAL'S TYPE -
    so: drop the VI, create a control from that output, delete the VI (the control stays), wire the control
    into 'target class'."*  Its steps 6/7 are *"delete wire W (Wire index by uid)"* then
    *"wire_control([L] -> TMSC 'target class')"*. THAT IS THE MECHANISM REPRODUCED BELOW, with ONE difference
    that S1 measures and reports rather than assumes: the Local-TYPED terminal is taken from the property
    node this op is adding anyway (`VI Server:Local`.`reference` is a Local refnum SINK), so no extra donor,
    no extra node and no erdosmiller creator is introduced.
  * The peer's Invoke-seeded variant (OpCreateLocal_v0.vi's Invoke terminal i=5) is NOT built, NOT prototyped
    and NOT probed - the brief forbids it. No donor is switched. No third route is invented.
  * tools/bench/diag_s3b_l0_localname.py - material #1, the shape of this file (gates, probes, JSON dump, the
    `local_name` and `create_local` wrappers, reused in substance).
  * gscript verbs used, ALL pre-existing, NONE patched: op, ref_counts, report, report_all, node_labels,
    node_terms_uid, panel_wiring, count, uids, open_panel, close_panel, ensure_loaded, wire, wire_control,
    create_control, create_indicator, delete_object, fp_labels, exec_state, save, build_property, reset, _run.
NO new gscript verb is added and no fleet file is patched. The Python-side wrapper `local_name()` lives IN
THIS DIAGNOSTIC; promoting it into tools/gscript.py is judgement's call, not this run's.

=====================================================================================================
THE OP, AS THE BRIEF FIXES IT
  donor of record : claudeDev\\OpNodeLabels_v0.vi   (UNCHANGED as a file - gate Z3)
  chain           : Open VI Reference -> Traverse `Local` -> Index Array `.element` -> TMSC seeded to `Local`
                    -> Property `CtrlName` 6355400 (read) -> string indicator, plus the error cluster
  hygiene         : every reference the op opens is closed by the donor's own ladder; the Python side calls
                    g.reset() and the 20-call gate reads the handle count either side.
*** IF THE DONOR'S SEED MECHANISM CANNOT BE REPRODUCED FOR CLASS `Local`, THAT IS A FACT THIS RUN REPORTS
    WITH AN OPEN LINE. No donor is switched, no Invoke-seeded variant is built, no third route is invented,
    nothing is repaired: the copy is left unsaved and removed. ***

=====================================================================================================
PREDICTION CONTRACT (every gate is the readback of a CALL; FATAL stops the chain and still dumps JSON)
  T1    the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                      FATAL
  T1b   claudeDev\\D1_s1_copy.vi md5 == 3e3d23cefd3a334001aa9d6156bf1aee
  T2    claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                            FATAL
  T3    claudeDev\\D1_s3a_focus_ind.vi md5 == eef91c1d91f16b034707e4d1285ca8cb                       FATAL
  T4    the DONOR claudeDev\\OpNodeLabels_v0.vi exists, md5 376ff125...                              FATAL
  T4b   claudeDev\\OpCreateLocal_v0.vi exists, md5 58275b21... (S4 drives it)                        FATAL
  T5    the pre-batch LabVIEW restart ran (44(e)) and the handle count was read either side
  --- S1: MEASURE THE DONOR'S SEED (read-only on the copy) -----------------------------------------
  S1_a1 the copy opens at ExecState 1 and its whole top-level diagram was dumped (node + terminal table)
  S1_a2 exactly ONE `To More Specific Class` node is present; its `target class` wire uid and its
        `specific class reference` wire uid are read off the machine
  S1_a3 NO node on that diagram produces the `target class` wire (the run 2 reading, re-measured)
  S1_a4 the OBJECT that does carry it is searched for OFF THE MACHINE: panel_wiring rows (every top-level
        front-panel object + its terminal's wire uid), the Wire row itself (owner + position), and the
        Constant / ControlTerminal / Terminal censuses. WHATEVER IS FOUND IS REPORTED VERBATIM; a gate
        passes when the search RAN, never on a particular answer.
  S1_a5 the fleet's existing cast verb was checked against the FILE: gscript.loop_cast exists, its op VIs on
        disk are listed, and whether any of them can cast to `Local` is stated plainly
  --- S2: BUILD THE READER WITH THE CAST -----------------------------------------------------------
  S2_b1 build_property('VI Server:Local', [('6355400', False)]) returned exactly 1 new Property; the class
        string, the resolution and the error column are recorded VERBATIM
  S2_b2 the new node's FULL terminal table was READ; `reference` (SINK) and the 6355400 SOURCE row are found
        by reading, never by retyping
  S2_b3 create_control on that `reference` SINK returned exactly one new ControlTerminal - THE Local-TYPED
        SEED - and the label LabVIEW gave it was read off the machine
  S2_b4 whether create_control was born WIRED to `reference` was READ; if it was, that wire was deleted BY
        UID (delete_object(target,'Wire',<index by uid>,verify=True), the only form there is)
  S2_b5 the TMSC's old `target class` wire was deleted BY UID; the gone-set equals exactly that uid
  S2_b6 wire_control([seed] -> TMSC `target class`) returned, and the TMSC's `target class` row carries a
        NON-ZERO wire afterwards                                                        (the EFFECT gate)
  S2_b7 the TMSC output wire's single downstream SINK was identified by reading, that wire was deleted by
        uid, and the orphaned sink was given a control of its OWN type (create_control), so the donor's
        vestigial chain stays legal
  S2_b8 TMSC `specific class reference` -> the new Property's `reference`: empty error column AND a non-zero
        wire uid on `reference` afterwards; the 6355400 row SURVIVED the wire (the false-pass separator)
  S2_b9 create_indicator on the 6355400 output added exactly one ControlTerminal and exactly one panel label,
        read off the machine by an fp_labels diff
  S2_b10 ExecState == 1        *** THE OP'S PASS CRITERION - no save is attempted below it ***
  S2_b11 g.save returned a byte count; md5, size and version bytes (26 00 80 00 = LV2026) recorded
  --- S3: the reader against GROUND TRUTH, on a SCRATCH copy ---------------------------------------
  S3_c0 the scratch is byte-identical to D1_s3a_focus_ind.vi at creation; the ARTEFACT's md5 is gated before
        AND after the whole phase (49(e): never the artefact itself)
  S3_c1 the scratch opens at ExecState 1 and its `Local` census is READ (docs/toolkit-capabilities.md:284
        records 8 at the S2/main baseline; the READING is the gate, never the 8)
  S3_c2 `Control Name` was read for EVERY pre-existing Local; every uid -> string pair is reported VERBATIM
  S3_c3 whether ANY returned string is a `.vi` file name is stated plainly (a FACT, never a pass/fail)
  --- S4: the open question ------------------------------------------------------------------------
  S4_d1 the front-panel control whose owned label reads 'index' was located by fp_labels (label taken from
        the machine's own bytes, hex recorded) and OpCreateLocal_v0 was driven with it
  S4_d2 the creator's error cluster, the `Local` census before/after and the new uid are recorded VERBATIM
  S4_d3 the scratch's ExecState BEFORE and AFTER the creator call were READ (a 0 after is a LEGITIMATE
        reading - attempt 1 measured exactly that - and is reported, not repaired)
  S4_d4 the new Local's `Control Name` was read with the NEW READER and reported VERBATIM
  --- S5: hygiene ----------------------------------------------------------------------------------
  S5_e1 20 consecutive reader calls ran; the handle count was read either side
  S5_e2 handles flat within +-100 (a FAIL here is a FINDING, not a blocker - 44(e)/49(j))
  S5_e3 refs opened == closed, 0 live
  S5_e4 the scratch was DELETED in the same run and exists=False
  --- Z ---------------------------------------------------------------------------------------------
  Z1    ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged after everything
  Z2    refs opened == closed, 0 live
  Z3    the DONOR OpNodeLabels_v0.vi is byte-unchanged
  Z3b   OpCreateLocal_v0.vi is byte-unchanged
  Z4    tools/recipes/ holds exactly the same file list after the run as before it

BOUNDS. NO VI IS RUN (34(f)) - the only VIs that execute are the fleet's op VIs, which is what scripting is.
No GUI action. No motor / ASI / camera (rig 조립 / ASSEMBLED; tools/motor_gate.py is not called and no serial
port is opened). No new PROCESS device. No recipe. No new gscript verb. `remove_bad_wires_scripted` /
`remove_bad_wires` / `gui_save` are neither imported nor called; `allow_broken` is never True. `move_in` is
NOT called at all. Every diagram index used is resolved from the machine, never hard-coded, and every owner
comparison accepts BOTH 'Diagram' and 'TopLevelDiagram'. Originals are never opened for write. NOTHING SAVED
IS EVER DELETED except the SCRATCH self-test copy, deleted in the same run, and the UNSAVED op copy if the
build never reaches a legal save point. NO ROUTE IS CHOSEN OR RECOMMENDED and no plan document or STATUS
`## NEXT` line is edited. `retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` /
`prior_art_review.py` are NOT run.
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
DONOR_MD5 = "376ff12569008ebac25a524e0887030b"
OP = os.path.join(g.CLAUDEDEV, "OpLocalName_v0.vi")
CREATOR = os.path.join(g.CLAUDEDEV, "OpCreateLocal_v0.vi")
CREATOR_MD5 = "58275b212dfa040685613e3edbf403f2"
CAST_OPS = [os.path.join(g.CLAUDEDEV, n) for n in ("OpLoopCast_v0.vi", "OpLoopCast_v1.vi",
                                                   "OpWhileCast_v0.vi", "OpLocalCast_v0.vi")]

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_LN2_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_s3b_l0_localname_v2.json")

LOCAL_CLASS = "VI Server:Local"     # the EXACT class string passed to the property builder - recorded as asked
CONTROL_NAME_ID = "6355400"         # Local.Control Name (docs/NAMES.md:260; RESOLVED on this machine, run 2)
TRAVERSE_CLASS = "Local"            # docs/toolkit-capabilities.md:284 - a VALID Traverse class (census 8)
PN_AT = (760, 430)                  # empty canvas on the donor's small diagram (material #1 used the same)
STD_PN_TERMS = ("reference", "reference out", "error in (no error)", "error in", "error out")
T_CAST_IN = "target class"          # build_oploopcast_v0.py:13 - the TMSC input the seed types
T_CAST_OUT = "specific class reference"   # build_oploopcast_v0.py:46 T_CAST_OUT, verbatim
TARGET_LABEL = "index"              # the numeric leg's indicator label; the STRING DRIVEN ONWARD is the one
                                    # fp_labels returns off the machine (hex recorded), never this literal
N_CONSECUTIVE = 20
SCAN_LIMIT = 60

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 60 attempt 2, material #2: build claudeDev\\OpLocalName_v0.vi WITH a To More Specific "
             "Class cast to `Local`, following the donor's OWN measured seed mechanism, and measure it "
             "(S1 measure the seed, S2 build, S3 ground truth, S4 the open question, S5 hygiene).",
     "judgement_decision_executed": "cycle 60: build the reader with a TMSC cast to Local, following the "
                                    "DONOR'S OWN measured seed mechanism. Not re-opened, not substituted.",
     "authorisation": "46(k), docs/cycle27-plan.md:1697-1705 - Pre-decided 2 forbids a further PROCESS "
                      "DEVICE, not an op VI; quoted verbatim in the module docstring.",
     "will_be_revised_on_any_review_that_gates_it": "49(i) - stated in the brief and repeated here.",
     "donor_of_record": DONOR,
     "no_other_donor_substituted": True, "no_invoke_seeded_variant_built": True,
     "no_third_route_invented": True,
     "chooses_no_route": True, "recommends_no_route": True, "interprets_nothing": True,
     "no_vi_was_run": True, "no_new_device": True, "no_gui_action": True, "no_recipe": True,
     "no_new_gscript_verb": True, "move_in_never_called": True,
     "new_op_vi": OP, "edits_no_plan_document": True, "edits_no_status_next": True,
     "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "REFUSED by the brief - not imported, not called; the GUI menu form "
                                  "(gscript.py:1629) is not called either.",
     "gui_save": "NEVER called", "allow_broken": "NEVER True",
     "rig_state": "조립 / ASSEMBLED (motors + ASI only through tools/motor_gate.py, which is not called; "
                  "camera not needed and not touched)",
     "citations": {"the_block": "tools/bench/diag_s3b_l0_localname_run2.log:29-56",
                   "seed_mechanism_of_record": "tools/recipes/build_oploopcast_v0.py:4-8, steps 6-7",
                   "cast_verb_that_exists": "tools/gscript.py:626-666 (loop_cast; ForLoop/WhileLoop only)",
                   "the_one_missing_seed": "docs/toolkit-capabilities.md (class-specifier constant)",
                   "control_name_id": "docs/NAMES.md:260; RESOLVED on this machine run 2 :50-52",
                   "local_is_a_valid_traverse_class": "docs/toolkit-capabilities.md:284 (census 8)",
                   "wire_delete_is_by_index_only": "docs/toolkit-capabilities.md:274; gscript.py:2240",
                   "create_control_wires_the_terminal": "tools/gscript.py:2360-2366",
                   "diagnostic_not_recipe": "Pre-decided 48(n)",
                   "handles_caveat": "Pre-decided 44(e)/49(j)",
                   "scratch_deleted_same_run": "CLAUDE.md rule 4; Pre-decided 49(e)"},
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "s3a_artefact": {"path": S3A_ARTEFACT, "md5_pin": S3A_MD5},
     "donor": {"path": DONOR, "md5_pin": DONOR_MD5}, "creator": {"path": CREATOR, "md5_pin": CREATOR_MD5},
     "handles": {}, "hash_probe": [],
     "S1_seed": {}, "S2_build": {}, "S3_ground_truth": {}, "S4_open_question": {}, "S5_hygiene": {},
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


def report_uids(target, cls):
    """report_all order (the order every delete_object index in this fleet is resolved against)."""
    try:
        return [o["uid"] for o in g.report_all(target, cls)], ""
    except Exception as e:                                                         # noqa: BLE001
        return [], "%s: %s" % (type(e).__name__, str(e)[:200])


def terms_table(rows):
    return [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]), "wire": r["wire"]}
            for r in rows]


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


def terms_of(target, diagram_index, uid):
    _i, rows = node_index_of(target, diagram_index, uid)
    return terms_table(rows)


def full_node_dump(target, diagram_index, tag, max_nodes=SCAN_LIMIT, quiet=False):
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
    if not quiet:
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


def delete_wire_by_uid(rec, tag, target, wire_uid):
    """The ONLY form there is: resolve the uid to its report_all index, delete, and assert the gone-set."""
    rd = {"tag": tag, "wire_uid": wire_uid}
    order, err = report_uids(target, "Wire")
    rd["report_all_error"] = err
    rd["wire_count_before"] = len(order)
    if wire_uid not in order:
        rd["index"] = None
        rd["error_verbatim"] = "uid %r is not in report_all(Wire) (%d members)" % (wire_uid, len(order))
        rd["gone"] = None
    else:
        rd["index"] = order.index(wire_uid)
        try:
            rd["gone"] = sorted(g.delete_object(target, "Wire", rd["index"], verify=True))
            rd["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            rd["gone"] = None
            rd["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    after, _ = report_uids(target, "Wire")
    rd["wire_count_after"] = len(after)
    rd["pre_existing_uids_that_vanished_beyond_the_target"] = sorted(
        (set(order) - set(after)) - {wire_uid})
    rec.setdefault("wire_deletes", []).append(rd)
    fact("%s delete_object(Wire[%r]) for uid %r: gone %r ; Wire census %r -> %r ; OTHER uids that vanished "
         "%r ; error VERBATIM %r" % (tag, rd.get("index"), wire_uid, rd.get("gone"),
                                     rd["wire_count_before"], rd["wire_count_after"],
                                     rd["pre_existing_uids_that_vanished_beyond_the_target"],
                                     rd["error_verbatim"]))
    return rd


# ============================================================ S1: MEASURE THE DONOR'S SEED
def phase_s1():
    """Read-only on the freshly made copy. NOTHING is edited in this phase."""
    K = R["S1_seed"]
    print("\n===================================================================", flush=True)
    print("=== S1   MEASURE the donor's cast seed, off the machine, before anything is built", flush=True)
    print("===================================================================", flush=True)
    if os.path.exists(OP):
        os.remove(OP)
        fact("an OLD %s was on disk and was removed before the copy (never load a VI you are about to "
             "overwrite)" % os.path.basename(OP))
    shutil.copy2(DONOR, OP)
    K["file_at_creation"] = probe("S1_a0 the op file at creation (a byte copy of the donor)", OP)
    g.open_panel(OP)
    time.sleep(1.0)

    K["baseline"] = {c: count_of(OP, c) for c in
                     ("Node", "Wire", "Property", "IndexArray", "ControlTerminal", "Diagram", "ForLoop",
                      "Constant", "Terminal", "Function", "SubVI")}
    es0 = read_exec_state(K, "S1 the copy, before any edit", OP)
    fact("S1 baseline census of the copy: %r" % (K["baseline"],))

    try:
        digs = g.report_all(OP, "Diagram")
    except Exception as e:                                                         # noqa: BLE001
        digs = []
        fact("S1 report_all(Diagram) raised %s: %s" % (type(e).__name__, str(e)[:200]))
    K["diagrams"] = [{"i": d["i"], "uid": d["uid"], "owner": d["owner"]} for d in digs]
    top = next((d for d in digs if str(d.get("owner")) in ("VI", "TopLevelDiagram", "")), digs[0] if digs
               else None)
    top_i = 0 if top is None else digs.index(top)
    K["top_diagram"] = top
    K["top_diagram_index_used"] = top_i
    fact("S1 the op's own diagrams (uid + owner, off the machine): %r ; the TOP-LEVEL one is %r at Traverse "
         "index %r - the ONLY diagram index this run uses on the op" % (K["diagrams"], top, top_i))

    print("\n--------- S1_a1  the whole top-level diagram, node by node", flush=True)
    shape = full_node_dump(OP, top_i, "S1_a1")
    K["shape_diagram_top"] = shape
    gate("S1_a1 the copy opens at ExecState 1 and its whole top-level diagram was dumped",
         es0 == 1 and bool(shape), "ExecState %r, %d nodes" % (es0, len(shape)))

    # --- S1_a2: the TMSC node, found by its terminal names (never by a uid and never by a label string)
    tmsc = [n for n in shape if any(t["name"] == T_CAST_IN for t in n.get("terms", []))
            and any(t["name"] == T_CAST_OUT for t in n.get("terms", []))]
    K["tmsc_nodes"] = [{"uid": n.get("uid"), "nodes_index": n.get("i"), "label": n.get("node_label"),
                        "terms": n.get("terms")} for n in tmsc]
    seed_wire = cast_out_wire = None
    if len(tmsc) == 1:
        seed_wire = next((t["wire"] for t in tmsc[0]["terms"] if t["name"] == T_CAST_IN), None)
        cast_out_wire = next((t["wire"] for t in tmsc[0]["terms"] if t["name"] == T_CAST_OUT), None)
    K["tmsc_target_class_wire"] = seed_wire
    K["tmsc_specific_class_reference_wire"] = cast_out_wire
    fact("S1_a2 `To More Specific Class` nodes (found by the terminal names %r / %r, never by a uid): %r ; "
         "its `%s` wire = %r ; its `%s` wire = %r"
         % (T_CAST_IN, T_CAST_OUT, K["tmsc_nodes"], T_CAST_IN, seed_wire, T_CAST_OUT, cast_out_wire))
    gate("S1_a2 exactly ONE TMSC node is present and both its cast wires were read off the machine",
         len(tmsc) == 1 and bool(seed_wire) and bool(cast_out_wire),
         "%d TMSC node(s); target class wire %r, output wire %r" % (len(tmsc), seed_wire, cast_out_wire))
    if len(tmsc) != 1 or not seed_wire:
        raise Stop("S1_a2: the donor's cast node could not be resolved from the terminal names. REPORTED; "
                   "no donor is switched and nothing is improvised.")

    # --- S1_a3: does ANY node on this diagram produce the seed wire?
    producers = [{"uid": n.get("uid"), "nodes_index": n.get("i"), "label": n.get("node_label"),
                  "terminal": t["name"]}
                 for n in shape for t in n.get("terms", []) if t["is_source"] and t["wire"] == seed_wire]
    K["seed_wire_producers_among_nodes"] = producers
    fact("S1_a3 nodes on this diagram with a SOURCE terminal carrying wire %r: %r  (an empty list means the "
         "seed is NOT produced by any node - it comes from a panel object or a constant)"
         % (seed_wire, producers))
    gate("S1_a3 the producer search among Nodes[] ran and its result is reported", True,
         "%d node producer(s) of wire %r" % (len(producers), seed_wire))

    # --- S1_a4: WHAT DOES carry it. Panel objects first (panel_wiring gives every one with its wire uid).
    print("\n--------- S1_a4  which OBJECT carries the seed wire - panel rows, the Wire row, the censuses",
          flush=True)
    try:
        pw = g.panel_wiring(OP)
        K["panel_wiring_error"] = ""
    except Exception as e:                                                        # noqa: BLE001
        pw = []
        K["panel_wiring_error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        fact("S1_a4 panel_wiring raised %s" % K["panel_wiring_error"])
    K["panel_wiring"] = pw
    for row in pw:
        fact("S1_a4 panel row: label %r (hex %s) indicator=%r uid=%r is_source=%r wire=%r term_err=%r "
             "wire_err=%r" % (row.get("label"), (row.get("label") or "").encode("utf-8").hex(),
                              row.get("indicator"), row.get("uid"), row.get("is_source"), row.get("wire"),
                              row.get("term_err"), row.get("wire_err")))
    seed_panel = [row for row in pw if row.get("wire") == seed_wire]
    K["panel_objects_carrying_the_seed_wire"] = seed_panel
    try:
        wires = g.report_all(OP, "Wire")
    except Exception as e:                                                        # noqa: BLE001
        wires = []
        fact("S1_a4 report_all(Wire) raised %s: %s" % (type(e).__name__, str(e)[:200]))
    K["seed_wire_row"] = next(({"i": w["i"], "uid": w["uid"], "class": w["class"], "owner": w["owner"],
                                "pos": w["pos"]} for w in wires if w["uid"] == seed_wire), None)
    for cls in ("Constant", "ControlTerminal", "Terminal", "SubVI", "Function"):
        try:
            rows = g.report_all(OP, cls)
            K.setdefault("censuses", {})[cls] = [{"i": o["i"], "uid": o["uid"], "class": o["class"],
                                                  "owner": o["owner"], "pos": o["pos"]} for o in rows]
        except Exception as e:                                                    # noqa: BLE001
            K.setdefault("censuses", {})[cls] = "ERROR %s: %s" % (type(e).__name__, str(e)[:160])
    fact("S1_a4 THE SEED, as far as this fleet can read it: panel object(s) whose terminal carries wire %r "
         "= %r ; the Wire object's own row (class/owner/pos) = %r ; Constant census %r ; ControlTerminal "
         "census %r"
         % (seed_wire, seed_panel, K["seed_wire_row"],
            len(K["censuses"].get("Constant", [])) if isinstance(K["censuses"].get("Constant"), list)
            else K["censuses"].get("Constant"),
            len(K["censuses"].get("ControlTerminal", []))
            if isinstance(K["censuses"].get("ControlTerminal"), list)
            else K["censuses"].get("ControlTerminal")))
    fact("S1_a4 Constant rows VERBATIM: %r" % (K["censuses"].get("Constant"),))
    fact("S1_a4 WHAT CANNOT BE READ, stated plainly: the refnum CLASS a seed object holds is not readable by "
         "any verb in this fleet - `Constant.Value` 634AC00 is registered but has NO op "
         "(docs/toolkit-capabilities.md), and a refnum control's type is not exposed by fp_labels / "
         "panel_wiring. What IS read above is the object, its class, its owner and its wire.")
    gate("S1_a4 the search for the object carrying the seed wire RAN and every reading is reported verbatim",
         K.get("seed_wire_row") is not None or bool(seed_panel) or bool(pw),
         "panel hits %d, Wire row %r" % (len(seed_panel), K.get("seed_wire_row")))

    # --- S1_a5: what the fleet already has, checked against the FILE (never against the peer's word)
    K["cast_verb"] = {"name": "loop_cast", "where": "tools/gscript.py:626",
                      "dispatches_only_to": ["OpLoopCast_v0.vi / OpLoopCast_v1.vi (ForLoop)",
                                             "OpWhileCast_v0.vi (WhileLoop)"],
                      "raises_for_any_other_class": "tools/gscript.py:645-646",
                      "op_files_on_disk": {os.path.basename(p): os.path.exists(p) for p in CAST_OPS},
                      "can_cast_to_Local": False,
                      "why_not": "there is no Local cast op; loop_cast's table has exactly two entries and "
                                 "it raises RuntimeError for any other class_name."}
    fact("S1_a5 the fleet's EXISTING cast verb, checked against the file: %r" % (K["cast_verb"],))
    gate("S1_a5 the existing cast verb was checked against tools/gscript.py and its op files on disk",
         hasattr(g, "loop_cast"),
         "loop_cast present=%r; op files %r" % (hasattr(g, "loop_cast"),
                                                K["cast_verb"]["op_files_on_disk"]))
    dump()
    return {"top_i": top_i, "tmsc": tmsc[0], "seed_wire": seed_wire, "cast_out_wire": cast_out_wire,
            "shape": shape}


# ============================================================ S2: BUILD THE READER WITH THE CAST
def phase_s2(S):
    K = R["S2_build"]
    print("\n===================================================================", flush=True)
    print("=== S2   build %s - TMSC seeded to `Local`, the donor's own mechanism" % os.path.basename(OP),
          flush=True)
    print("===================================================================", flush=True)
    try:
        _s2_body(K, S)
    finally:
        close_quietly(OP)
    dump()
    return isinstance(K.get("saved_bytes"), int)


def _s2_body(K, S):
    top_i = S["top_i"]
    tmsc_uid = S["tmsc"]["uid"]
    seed_wire = S["seed_wire"]
    cast_out_wire = S["cast_out_wire"]
    shape = S["shape"]

    # --- S2_b1: the property node
    print("\n--------- S2_b1  build_property(%r, [(%r, False)]) at %r" % (LOCAL_CLASS, CONTROL_NAME_ID, PN_AT),
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
    fact("S2_b1 class string passed VERBATIM %r ; property id %r ; resolved=%r ; new %r ; Property census "
         "%r -> %r ; error column VERBATIM %r"
         % (LOCAL_CLASS, CONTROL_NAME_ID, rd["resolved"], rd["new"], pn_before, rd["property_count_after"],
            rd["error_verbatim"]))
    gate("S2_b1 build_property returned exactly 1 new Property", bool(rd["new"]) and len(rd["new"]) == 1,
         "resolved=%r error %r" % (rd["resolved"], rd["error_verbatim"]))
    if not rd["new"]:
        raise Stop("S2_b1: the property node was not created. REPORTED; nothing is repaired.")
    pn_uid = rd["new"][0]["uid"]
    read_exec_state(K, "S2 after build_property", OP)

    # --- S2_b2: its terminal table, read off the machine
    pn_i, rows = node_index_of(OP, top_i, pn_uid)
    terms = terms_table(rows)
    ref_term = next((t for t in terms if t["name"] == "reference" and not t["is_source"]), None)
    extra = [t for t in terms if t["name"] not in STD_PN_TERMS]
    out_term = next((t for t in extra if t["is_source"]), None)
    K["property_terminals"] = {"nodes_index": pn_i, "terms": terms, "beyond_the_standard_four": extra,
                               "reference_sink": ref_term, "control_name_source": out_term,
                               "names_hex": {t["name"]: t["name"].encode("utf-8").hex() for t in terms}}
    fact("S2_b2 the Property #%s sits at Nodes[%r]; FULL terminal table READ OFF THE MACHINE: %r ; the "
         "`reference` SINK row %r ; the 6355400 SOURCE row %r (its name is the SHORT NAME on this machine, "
         "read, never retyped)" % (pn_uid, pn_i, terms, ref_term, out_term))
    gate("S2_b2 the new node's `reference` SINK and its 6355400 SOURCE row were both READ",
         ref_term is not None and out_term is not None, "%r / %r" % (ref_term, out_term))
    if ref_term is None or out_term is None:
        raise Stop("S2_b2: the property node lacks a `reference` sink or the 6355400 output row. REPORTED; "
                   "no alternative property and no alternative op is improvised.")

    # --- S2_b3: THE SEED. `Terminal.Create Control` makes a control OF THE TERMINAL'S TYPE
    #     (build_oploopcast_v0.py:4-8). The Local-typed terminal used here is the `reference` SINK of the
    #     property node this op needs anyway - no extra donor, no erdosmiller creator, no Invoke.
    print("\n--------- S2_b3  create_control on the `reference` SINK = the Local-TYPED seed", flush=True)
    ct_before = count_of(OP, "ControlTerminal")
    sd = {"node_index": pn_i, "terminal_index": ref_term["i"], "terminal_name": ref_term["name"],
          "control_terminal_before": ct_before}
    try:
        new_ct, seed_label = g.create_control(OP, pn_i, ref_term["i"])
        sd["new"] = [{"uid": o["uid"], "pos": o["pos"]} for o in new_ct]
        sd["label_from_the_machine"] = seed_label
        sd["label_hex"] = (seed_label or "").encode("utf-8").hex()
        sd["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        sd["new"] = None
        sd["label_from_the_machine"] = None
        sd["label_hex"] = None
        sd["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    sd["control_terminal_after"] = count_of(OP, "ControlTerminal")
    K["seed_control"] = sd
    es_seed = read_exec_state(K, "S2 after create_control (the seed)", OP)
    fact("S2_b3 create_control(Nodes[%r].Terminals[%r] = %r): new %r ; label READ OFF THE MACHINE %r (hex "
         "%r) ; ControlTerminal %r -> %r ; ExecState %r ; error VERBATIM %r"
         % (pn_i, ref_term["i"], ref_term["name"], sd["new"], sd["label_from_the_machine"], sd["label_hex"],
            ct_before, sd["control_terminal_after"], es_seed, sd["error_verbatim"]))
    ok_seed = gate("S2_b3 create_control returned exactly one new ControlTerminal - the Local-TYPED seed - "
                   "and its label was read off the machine",
                   bool(sd["new"]) and len(sd["new"]) == 1 and bool(sd["label_from_the_machine"]),
                   "new %r label %r" % (sd["new"], sd["label_from_the_machine"]))
    if not ok_seed:
        K["stopped_because"] = ("the donor's seed mechanism could NOT be reproduced for class `Local`: "
                                "`Terminal.Create Control` on the `VI Server:Local` property node's "
                                "`reference` sink produced %r (error VERBATIM %r). THIS IS THE FACT THE "
                                "BRIEF ASKS FOR. No donor is switched, no Invoke-seeded variant is built, "
                                "no third route is invented, nothing is repaired."
                                % (sd["new"], sd["error_verbatim"]))
        fact("S2 STOPS HERE: %s" % K["stopped_because"])
        return
    seed_label = sd["label_from_the_machine"]

    # --- S2_b4: was the seed born WIRED into `reference`? (gscript.py:2360-2366 says create_control wires it)
    terms_after_seed = terms_of(OP, top_i, pn_uid)
    ref_after_seed = next((t for t in terms_after_seed if t["name"] == ref_term["name"]), None)
    K["reference_after_the_seed"] = ref_after_seed
    fact("S2_b4 the property's `reference` row right after create_control = %r  (a non-zero wire means the "
         "seed was born WIRED, which gscript.py:2360-2366 predicts)" % (ref_after_seed,))
    born_wire = (ref_after_seed or {}).get("wire") or 0
    if born_wire:
        delete_wire_by_uid(K, "S2_b4 the seed's birth wire", OP, born_wire)
        terms_after_seed = terms_of(OP, top_i, pn_uid)
        ref_after_seed = next((t for t in terms_after_seed if t["name"] == ref_term["name"]), None)
        K["reference_after_deleting_the_birth_wire"] = ref_after_seed
        fact("S2_b4 the property's `reference` row after deleting the birth wire = %r" % (ref_after_seed,))
    ct_still = count_of(OP, "ControlTerminal")
    gate("S2_b4 the birth wire (if any) was deleted BY UID and the seed control survived it",
         (ref_after_seed or {}).get("wire", 0) == 0
         and isinstance(ct_still, int) and ct_still == sd["control_terminal_after"],
         "reference row %r ; ControlTerminal %r (was %r)" % (ref_after_seed, ct_still,
                                                             sd["control_terminal_after"]))
    read_exec_state(K, "S2 after the birth-wire delete", OP)

    # --- S2_b5: delete the TMSC's OLD seed wire
    print("\n--------- S2_b5  delete the TMSC's old `%s` wire (uid %r), by uid" % (T_CAST_IN, seed_wire),
          flush=True)
    d5 = delete_wire_by_uid(K, "S2_b5 the TMSC's old seed wire", OP, seed_wire)
    tmsc_terms = terms_of(OP, top_i, tmsc_uid)
    K["tmsc_terms_after_the_seed_delete"] = tmsc_terms
    fact("S2_b5 the TMSC's terminal table after the delete: %r" % (tmsc_terms,))
    gate("S2_b5 the TMSC's old seed wire was deleted and the gone-set is exactly that uid",
         d5.get("gone") == [seed_wire]
         and not d5.get("pre_existing_uids_that_vanished_beyond_the_target"),
         "gone %r, collateral %r" % (d5.get("gone"),
                                     d5.get("pre_existing_uids_that_vanished_beyond_the_target")))
    read_exec_state(K, "S2 after the old seed wire was deleted", OP)
    if d5.get("gone") != [seed_wire]:
        K["stopped_because"] = ("the TMSC's old seed wire could not be deleted (%r). REPORTED; nothing is "
                                "repaired." % (d5.get("error_verbatim"),))
        fact("S2 STOPS HERE: %s" % K["stopped_because"])
        return

    # --- S2_b6: wire the Local-typed seed into `target class` (build_oploopcast_v0.py step 7)
    print("\n--------- S2_b6  wire_control([%r] -> TMSC `%s`)" % (seed_label, T_CAST_IN), flush=True)
    fn_order, fn_err = report_uids(OP, "Function")
    wr6 = {"seed_label": seed_label, "function_report_error": fn_err,
           "tmsc_function_index": fn_order.index(tmsc_uid) if tmsc_uid in fn_order else None,
           "wire_count_before": count_of(OP, "Wire")}
    if wr6["tmsc_function_index"] is None:
        wr6["error_verbatim"] = ("the TMSC uid %r is not in report_all(Function) (%d members) - the wiring "
                                 "destination cannot be addressed by this fleet's class/index form"
                                 % (tmsc_uid, len(fn_order)))
    else:
        try:
            wr6["wire_count_after"] = g.wire_control(OP, [seed_label], "Function",
                                                     wr6["tmsc_function_index"], [T_CAST_IN],
                                                     src_diagram_index=top_i)
            wr6["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            wr6["wire_count_after"] = count_of(OP, "Wire")
            wr6["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    tmsc_terms = terms_of(OP, top_i, tmsc_uid)
    wr6["tmsc_terms_after"] = tmsc_terms
    seed_row = next((t for t in tmsc_terms if t["name"] == T_CAST_IN), None)
    wr6["target_class_row_after"] = seed_row
    K["seed_wiring"] = wr6
    es6 = read_exec_state(K, "S2 after the seed was wired into `target class`", OP)
    fact("S2_b6 wire_control([%r] -> Function[%r].`%s`): Wire census %r -> %r ; the `%s` row AFTER = %r ; "
         "ExecState %r ; error VERBATIM %r"
         % (seed_label, wr6["tmsc_function_index"], T_CAST_IN, wr6["wire_count_before"],
            wr6.get("wire_count_after"), T_CAST_IN, seed_row, es6, wr6["error_verbatim"]))
    ok6 = gate("S2_b6 the seed landed - the TMSC's `%s` row carries a NON-ZERO wire" % T_CAST_IN,
               wr6["error_verbatim"] == "" and bool(seed_row) and bool(seed_row.get("wire")),
               "error %r, row %r" % (wr6["error_verbatim"], seed_row))
    if not ok6:
        K["stopped_because"] = ("the donor's seed mechanism could NOT be reproduced for class `Local`: the "
                                "Local-typed control would not wire into the TMSC's `%s` (error VERBATIM "
                                "%r, row %r). THIS IS THE FACT THE BRIEF ASKS FOR. No donor is switched, no "
                                "Invoke-seeded variant is built, no third route is invented."
                                % (T_CAST_IN, wr6["error_verbatim"], seed_row))
        fact("S2 STOPS HERE: %s" % K["stopped_because"])
        return

    # --- S2_b7: the donor's vestigial chain. The TMSC output now carries a `Local` reference; its existing
    #     downstream sink reads a Diagram property, so it is detached and given a control of its OWN type.
    print("\n--------- S2_b7  detach the donor's vestigial chain from the (now Local-typed) cast output",
          flush=True)
    sinks = [{"uid": n.get("uid"), "nodes_index": n.get("i"), "label": n.get("node_label"),
              "terminal": t["name"], "terminal_index": t["i"]}
             for n in shape for t in n.get("terms", [])
             if (not t["is_source"]) and t["wire"] == cast_out_wire]
    K["cast_output_sinks"] = sinks
    fact("S2_b7 the sinks fed by the cast output wire %r, read off the S1 dump: %r" % (cast_out_wire, sinks))
    gate("S2_b7a exactly ONE downstream sink is fed by the cast output wire", len(sinks) == 1,
         "%r" % (sinks,))
    if len(sinks) != 1:
        K["stopped_because"] = ("the cast output feeds %d sinks, not 1 - the donor's chain cannot be "
                                "detached by the one measured step this brief allows. REPORTED; nothing is "
                                "improvised." % len(sinks))
        fact("S2 STOPS HERE: %s" % K["stopped_because"])
        return
    sink = sinks[0]
    d7 = delete_wire_by_uid(K, "S2_b7 the cast output wire", OP, cast_out_wire)
    if d7.get("gone") != [cast_out_wire]:
        K["stopped_because"] = ("the cast output wire could not be deleted (%r). REPORTED."
                                % (d7.get("error_verbatim"),))
        fact("S2 STOPS HERE: %s" % K["stopped_because"])
        return
    sink_i, _rows = node_index_of(OP, top_i, sink["uid"])
    cd = {"sink": sink, "nodes_index_now": sink_i, "control_terminal_before": count_of(OP, "ControlTerminal")}
    try:
        new_ct2, lab2 = g.create_control(OP, sink_i, sink["terminal_index"])
        cd["new"] = [{"uid": o["uid"], "pos": o["pos"]} for o in new_ct2]
        cd["label_from_the_machine"] = lab2
        cd["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        cd["new"] = None
        cd["label_from_the_machine"] = None
        cd["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    cd["control_terminal_after"] = count_of(OP, "ControlTerminal")
    K["vestigial_chain_control"] = cd
    es7 = read_exec_state(K, "S2 after the vestigial chain got its own control", OP)
    fact("S2_b7 the orphaned sink %r got create_control(Nodes[%r].Terminals[%r]): new %r ; label READ OFF "
         "THE MACHINE %r ; ControlTerminal %r -> %r ; ExecState %r ; error VERBATIM %r"
         % (sink, sink_i, sink["terminal_index"], cd["new"], cd["label_from_the_machine"],
            cd["control_terminal_before"], cd["control_terminal_after"], es7, cd["error_verbatim"]))
    gate("S2_b7b the orphaned downstream sink was given a control of its own type",
         bool(cd["new"]) and len(cd["new"]) == 1, "new %r error %r" % (cd["new"], cd["error_verbatim"]))

    # --- S2_b8: the cast output -> the new property's `reference`
    print("\n--------- S2_b8  TMSC `%s` -> Property `reference`" % T_CAST_OUT, flush=True)
    pn_order, pn_err = report_uids(OP, "Property")
    w8 = {"property_report_error": pn_err,
          "tmsc_function_index": wr6["tmsc_function_index"],
          "pn_report_index": pn_order.index(pn_uid) if pn_uid in pn_order else None,
          "wire_count_before": count_of(OP, "Wire")}
    if w8["pn_report_index"] is None:
        w8["error_verbatim"] = "the new Property uid %r is not in report_all(Property)" % (pn_uid,)
    else:
        try:
            w8["wire_count_after"] = g.wire(OP, "Function", w8["tmsc_function_index"], T_CAST_OUT,
                                            "Property", w8["pn_report_index"], ref_term["name"])
            w8["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            w8["wire_count_after"] = count_of(OP, "Wire")
            w8["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    terms8 = terms_of(OP, top_i, pn_uid)
    ref8 = next((t for t in terms8 if t["name"] == ref_term["name"]), None)
    name8 = next((t for t in terms8 if t["name"] == out_term["name"]), None)
    w8["reference_row_after"] = ref8
    w8["control_name_row_after"] = name8
    w8["terminals_after"] = terms8
    K["cast_to_property_wire"] = w8
    es8 = read_exec_state(K, "S2 after the cast output was wired into `reference`", OP)
    fact("S2_b8 wire Function[%r].`%s` -> Property[%r].`%s`: Wire census %r -> %r ; `reference` row AFTER "
         "%r ; the %r row AFTER %r ; ExecState %r ; error VERBATIM %r"
         % (w8["tmsc_function_index"], T_CAST_OUT, w8["pn_report_index"], ref_term["name"],
            w8["wire_count_before"], w8.get("wire_count_after"), ref8, out_term["name"], name8, es8,
            w8["error_verbatim"]))
    gate("S2_b8 the wire landed - empty error column AND a non-zero wire uid on `reference`",
         w8["error_verbatim"] == "" and bool(ref8) and bool(ref8.get("wire")),
         "error %r, reference wire %r" % (w8["error_verbatim"], (ref8 or {}).get("wire")))
    gate("S2_b8b the property's %r output row SURVIVED the wire (the false-pass separator: its ABSENCE with "
         "ExecState 1 would mean the node re-adapted its class)" % out_term["name"], name8 is not None,
         "%r" % (name8,))
    if not (ref8 and ref8.get("wire")) or name8 is None:
        K["stopped_because"] = ("the cast output would not feed the `VI Server:Local` property node "
                                "(reference row %r, %r row %r, error VERBATIM %r). REPORTED; nothing is "
                                "repaired and no other route is tried."
                                % (ref8, out_term["name"], name8, w8["error_verbatim"]))
        fact("S2 STOPS HERE: %s" % K["stopped_because"])
        return
    if es8 != 1:
        K["exec_state_after_cast_wire"] = es8
        fact("S2_b8 NOTE, reported not interpreted: ExecState is %r here. The run continues to the indicator "
             "because the indicator is the node's only unwired output; the PASS CRITERION is S2_b10." % es8)

    # --- S2_b9: the string indicator on the 6355400 output
    print("\n--------- S2_b9  create_indicator on the %r output terminal" % out_term["name"], flush=True)
    global NAME_IND
    before_fp = fp_pairs(OP, max_n=80)
    ct_b = count_of(OP, "ControlTerminal")
    ind = {"node_index": pn_i, "terminal_index": out_term["i"], "terminal_name": out_term["name"],
           "control_terminal_before": ct_b}
    pn_i_now, _r = node_index_of(OP, top_i, pn_uid)
    ind["nodes_index_now"] = pn_i_now
    try:
        ind["new"] = [{"uid": o["uid"], "pos": o["pos"]}
                      for o in g.create_indicator(OP, pn_i_now, out_term["i"])]
        ind["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        ind["new"] = None
        ind["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    ind["control_terminal_after"] = count_of(OP, "ControlTerminal")
    after_fp = fp_pairs(OP, max_n=80)
    before_labels = [lab for _i, lab, _x in before_fp]
    new_labels = [lab for _i, lab, _x in after_fp if lab not in before_labels]
    ind["front_panel_before"] = before_fp
    ind["front_panel_after"] = after_fp
    ind["new_labels"] = new_labels
    ind["new_label_hex"] = [l.encode("utf-8").hex() for l in new_labels]
    K["create_indicator"] = ind
    fact("S2_b9 create_indicator on Nodes[%r].Terminals[%r] (%r): new %r ; ControlTerminal %r -> %r ; NEW "
         "PANEL LABEL(S) READ OFF THE MACHINE %r (hex %r) ; error VERBATIM %r"
         % (pn_i_now, out_term["i"], out_term["name"], ind["new"], ct_b, ind["control_terminal_after"],
            new_labels, ind["new_label_hex"], ind["error_verbatim"]))
    gate("S2_b9 exactly one new ControlTerminal and exactly one new panel label were read off the machine",
         bool(ind["new"]) and len(ind["new"]) == 1 and len(new_labels) == 1,
         "new %r labels %r" % (ind["new"], new_labels))
    if len(new_labels) == 1:
        NAME_IND = new_labels[0]
        R["pass_criteria"]["reader_indicator_label"] = NAME_IND

    es9 = read_exec_state(K, "S2 after the indicator", OP)
    R["pass_criteria"]["op_execstate"] = es9
    ok = gate("S2_b10 ExecState == 1 after the indicator  *** THE OP'S PASS CRITERION ***", es9 == 1,
              "%r" % (es9,))
    K["census_after"] = {c: count_of(OP, c) for c in ("Node", "Wire", "Property", "ControlTerminal")}
    fact("S2 census after the edit: %r" % (K["census_after"],))
    if not ok or NAME_IND is None:
        K["stopped_because"] = ("ExecState %r / indicator label %r - THE OP IS NOT SAVED and nothing is "
                                "repaired (no remove_bad_wires_scripted, no gui_save, no allow_broken)."
                                % (es9, NAME_IND))
        fact("S2: %s" % K["stopped_because"])
        return
    try:
        K["saved_bytes"] = g.save(OP)
        fact("S2 saved %r bytes" % (K["saved_bytes"],))
    except Exception as e:                                                        # noqa: BLE001
        K["saved_bytes"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:300])
        fact("S2 g.save(OP) raised %s: %s" % (type(e).__name__, str(e)[:300]))
    K["file_after"] = D.file_facts("S2_b11 the op VI after the save", OP)
    R["artefacts"].append({"step": "S2 OpLocalName_v0", "path": OP,
                           "saved": isinstance(K.get("saved_bytes"), int), "file": K["file_after"]})
    gate("S2_b11 g.save returned a byte count and the file reads LV2026 (26 00 80 00)",
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
    """material #1's wrapper (tools/bench/diag_s3b_l0_localname.py:695-743), unchanged in substance: drive
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


# ============================================================ S3 / S4 / S5 on a SCRATCH copy
def phase_s345():
    K1, K2, K3 = R["S3_ground_truth"], R["S4_open_question"], R["S5_hygiene"]
    print("\n===================================================================", flush=True)
    print("=== S3/S4/S5  on %s - a SCRATCH duplicate of D1_s3a_focus_ind.vi" % os.path.basename(SCRATCH),
          flush=True)
    print("=== 49(e): never the artefact itself; its md5 is gated before AND after", flush=True)
    print("===================================================================", flush=True)
    a_before = probe("S3_c0 the ARTEFACT D1_s3a_focus_ind.vi BEFORE the phase", S3A_ARTEFACT)
    gate("S3_c0a the artefact's md5 is the pin BEFORE the phase", a_before.get("md5") == S3A_MD5,
         "%s" % a_before.get("md5"))
    shutil.copy2(S3A_ARTEFACT, SCRATCH)
    p = probe("S3_c0 the scratch at creation", SCRATCH)
    K1["scratch"] = {"path": SCRATCH, "at_creation": p}
    gate("S3_c0 the scratch is byte-identical to D1_s3a_focus_ind.vi at creation", p.get("md5") == S3A_MD5,
         "%s (expected %s)" % (p.get("md5", "?"), S3A_MD5))
    g.open_panel(SCRATCH)
    time.sleep(1.0)
    try:
        _s3(K1)
        _s4(K1, K2)
        _s5(K3)
    finally:
        close_quietly(SCRATCH)
    a_after = probe("S3_c0 the ARTEFACT D1_s3a_focus_ind.vi AFTER the phase", S3A_ARTEFACT)
    gate("S3_c0b the artefact's md5 is the pin AFTER the phase", a_after.get("md5") == S3A_MD5,
         "%s" % a_after.get("md5"))
    dump()


def _s3(K):
    es0 = read_exec_state(K, "S3 the scratch, before any call", SCRATCH)
    try:
        rows = g.report_all(SCRATCH, "Local")
    except Exception as e:                                                         # noqa: BLE001
        rows = []
        fact("S3 report_all(Local) raised %s: %s" % (type(e).__name__, str(e)[:200]))
    K["local_rows"] = [{"i": o["i"], "uid": o["uid"], "class": o["class"], "owner": o["owner"],
                        "pos": o["pos"]} for o in rows]
    K["local_census_before"] = len(rows)
    fact("S3_c1 baseline: ExecState %r ; `Local` census %r (docs/toolkit-capabilities.md:284 records 8 at "
         "the S2/main baseline - the READING is the gate, never the 8) ; rows %r"
         % (es0, len(rows), K["local_rows"]))
    gate("S3_c1 the scratch opens at ExecState 1 and its `Local` census was READ",
         es0 == 1 and isinstance(K["local_census_before"], int),
         "ExecState %r, Local %r" % (es0, K["local_census_before"]))

    print("\n--------- S3_c2  read `Control Name` for EVERY pre-existing Local", flush=True)
    reads = []
    for o in K["local_rows"]:
        r = local_name(SCRATCH, o["i"], tag="S3 Local[%d] uid %s" % (o["i"], o["uid"]))
        r["uid_from_report_all"] = o["uid"]
        reads.append(r)
        fact("S3_c2 Local[%d] uid %s -> Control Name %r (hex %r) ; run error VERBATIM %r ; donor error "
             "cluster %s" % (o["i"], o["uid"], r.get("control_name"), r.get("control_name_hex"),
                             r.get("run_error_verbatim"), r.get("cluster_error_out_2")))
    K["control_name_reads"] = reads
    got = [r for r in reads if isinstance(r.get("control_name"), str)
           and not str(r.get("control_name")).startswith("ERROR ")]
    gate("S3_c2 `Control Name` was read for every pre-existing Local and every uid -> string pair reported",
         len(reads) == K["local_census_before"] and len(got) == len(reads),
         "%d/%d rows returned a string" % (len(got), len(reads)))
    vi_named = [r for r in got if str(r.get("control_name", "")).lower().endswith(".vi")]
    K["strings_that_are_vi_file_names"] = [r.get("control_name") for r in vi_named]
    K["distinct_strings"] = sorted({r.get("control_name") for r in got})
    fact("S3_c3 PLAINLY: %d of %d returned strings END IN `.vi` -> %r ; the DISTINCT strings returned are %r"
         % (len(vi_named), len(got), K["strings_that_are_vi_file_names"], K["distinct_strings"]))
    gate("S3_c3 whether any returned string is a .vi file name was stated plainly", True,
         "%d of %d end in .vi" % (len(vi_named), len(got)))
    dump()


def _s4(K1, K):
    print("\n--------- S4  the open question: create a Local from the control labelled 'index', then READ it",
          flush=True)
    t0 = time.time()
    rows = fp_pairs(SCRATCH, max_n=200)
    K["fp_rows"] = len(rows)
    K["fp_sweep_s"] = round(time.time() - t0, 1)
    hits = [(i, lab, ind) for i, lab, ind in rows if lab == TARGET_LABEL]
    K["panel_hits_for_the_label"] = hits
    fact("S4_d1 fp_labels swept %d panel objects in %.1f s ; rows whose owned label equals %r: %r"
         % (len(rows), K["fp_sweep_s"], TARGET_LABEL, hits))
    gate("S4_d1 exactly one front-panel object carries that owned label", len(hits) == 1, "%r" % (hits,))
    if len(hits) != 1:
        K["not_attempted"] = ("the label is not unique / not present on the scratch (%r) - S4 is REPORTED, "
                              "not improvised around." % (hits,))
        fact("S4 NOT ATTEMPTED: %s" % K["not_attempted"])
        return
    panel_index, machine_label, _is_ind = hits[0]
    K["label_from_the_machine"] = machine_label
    K["label_hex"] = machine_label.encode("utf-8").hex()
    K["panel_index"] = panel_index

    es_before = read_exec_state(K, "S4 the scratch BEFORE the creator call", SCRATCH)
    c = create_local(SCRATCH, machine_label, panel_index, tag="S4 CALL")
    K["creator_call"] = c
    es_after = read_exec_state(K, "S4 the scratch AFTER the creator call", SCRATCH)
    K["exec_state_before"] = es_before
    K["exec_state_after"] = es_after
    fact("S4_d2 creator: op `Text` (the label it WALKED TO, off the machine) %r ; error cluster VERBATIM %s "
         "; run error VERBATIM %r ; `Local` census %d -> %d ; NEW uids %r ; LOST uids %r"
         % (c.get("op_matched_label"), c.get("error_cluster_verbatim"), c.get("run_error_verbatim"),
            len(c.get("local_uids_before") or []), len(c.get("local_uids_after") or []),
            c.get("new_local_uids"), c.get("lost_local_uids")))
    gate("S4_d2 the creator call returned and its error cluster / census diff were captured VERBATIM",
         "run_error_verbatim" in c, "new %r" % (c.get("new_local_uids"),))
    gate("S4_d3 the scratch's ExecState BEFORE and AFTER the creator call were READ",
         es_before in (0, 1) and es_after in (0, 1),
         "%r -> %r  (a 0 after is a LEGITIMATE reading - attempt 1 measured exactly that - and is reported, "
         "never repaired)" % (es_before, es_after))

    new_uids = c.get("new_local_uids") or []
    if len(new_uids) != 1:
        K["readback"] = {"note": "no single new Local to read back (%r)" % (new_uids,)}
        gate("S4_d4 the new Local's `Control Name` was read with the NEW READER", False,
             "no single new Local: %r" % (new_uids,))
        dump()
        return
    new_uid = new_uids[0]
    owner_read(K, "S4 owner of the new Local", new_uid, SCRATCH)
    try:
        rows2 = g.report_all(SCRATCH, "Local")
    except Exception as e:                                                         # noqa: BLE001
        rows2 = []
        fact("S4 report_all(Local) raised %s: %s" % (type(e).__name__, str(e)[:200]))
    order = [o["uid"] for o in rows2]
    K["local_rows_after"] = [{"i": o["i"], "uid": o["uid"], "owner": o["owner"]} for o in rows2]
    idx = order.index(new_uid) if new_uid in order else None
    K["traverse_index_of_the_new_local"] = idx
    fact("S4_d4 the new Local #%s sits at Traverse index %r of %d (report_all order == Traverse order, the "
         "ordering every delete_object call in this fleet already relies on)" % (new_uid, idx, len(order)))
    if idx is None:
        gate("S4_d4 the new Local's `Control Name` was read with the NEW READER", False,
             "the new uid is not in report_all(Local) order")
        dump()
        return
    r = local_name(SCRATCH, idx, tag="S4 the NEW Local uid %s" % new_uid)
    r["uid"] = new_uid
    K["reader_readback"] = r
    fact("S4_d4 READER on Local[%d] (uid %s): `Control Name` = %r (hex %r) ; run error VERBATIM %r ; donor "
         "error cluster %s ; asked for %r (hex %r)"
         % (idx, new_uid, r.get("control_name"), r.get("control_name_hex"), r.get("run_error_verbatim"),
            r.get("cluster_error_out_2"), machine_label, K["label_hex"]))
    K["matches_the_label_asked_for"] = (r.get("control_name") == machine_label)
    gate("S4_d4 the new Local's `Control Name` was read with the NEW READER and reported VERBATIM",
         isinstance(r.get("control_name"), str) and not str(r.get("control_name")).startswith("ERROR "),
         "%r  (equal to the label asked for: %r)" % (r.get("control_name"), K["matches_the_label_asked_for"]))
    dump()


def _s5(K):
    print("\n--------- S5  %d CONSECUTIVE READER CALLS (handles flat +-100, every reference closed)"
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
    fact("S5_e1 %d consecutive reader calls in %.1f s: %d returned a string, %d carried an error"
         % (N_CONSECUTIVE, K["consecutive"]["elapsed_s"], K["consecutive"]["n_with_a_string"],
            K["consecutive"]["n_with_an_error"]))
    fact("S5_e1 handles %r -> %r (delta %s) ; refs before %r after %r"
         % (h_before, h_after,
            (h_after - h_before) if isinstance(h_before, int) and isinstance(h_after, int) else "?",
            R["ref_counts_before_20"], R["ref_counts_after_20"]))
    gate("S5_e1 %d consecutive reader calls ran and the handle count was read either side" % N_CONSECUTIVE,
         len(runs) == N_CONSECUTIVE and isinstance(h_before, int) and isinstance(h_after, int),
         "%r -> %r" % (h_before, h_after))
    flat = (isinstance(h_before, int) and isinstance(h_after, int) and abs(h_after - h_before) <= 100)
    gate("S5_e2 the handle count is flat within +-100 across the 20 calls", flat,
         "%r -> %r (a FAIL is a FINDING, not a blocker - 44(e)/49(j))" % (h_before, h_after))
    rc = R["ref_counts_after_20"] or {}
    gate("S5_e3 refs opened == closed, 0 live after the 20 calls",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    dump()


# ============================================================ MAIN
def main():
    print("=== diag_s3b_l0_localname_v2  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== cycle 60 attempt 2, material #2: build claudeDev\\OpLocalName_v0.vi WITH the TMSC cast to "
          "`Local`, and measure it", flush=True)
    rp = os.path.join(ROOT, "tools", "recipes")
    R["recipes_listing_before"] = sorted(os.listdir(rp))
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
    gate("T4 the donor OpNodeLabels_v0.vi is on disk at its recorded md5", dn.get("md5") == DONOR_MD5,
         "%r (pin %s)" % (dn.get("md5"), DONOR_MD5), fatal=True)
    cr = probe("T4b the CREATOR OpCreateLocal_v0.vi (S4 drives it)", CREATOR)
    R["creator"]["md5_before"] = cr.get("md5")
    gate("T4b OpCreateLocal_v0.vi is on disk at its recorded md5", cr.get("md5") == CREATOR_MD5,
         "%r (pin %s)" % (cr.get("md5"), CREATOR_MD5), fatal=True)

    D.fresh("T5 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    gate("T5 the pre-batch restart ran and the handle count was read either side",
         isinstance(R["handles"]["before"], int) and isinstance(R["handles"]["after_restart"], int),
         "%r -> %r" % (R["handles"]["before"], R["handles"]["after_restart"]))
    dump()

    op_ok = False
    S = None
    try:
        S = phase_s1()
    except Stop as s:
        R["S1_seed"]["stopped_at"] = str(s)
        fact("S1 STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        R["S1_seed"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("S1 raised %s: %s" % (type(e).__name__, str(e)[:600]))
    dump()

    if S is not None:
        try:
            op_ok = phase_s2(S)
        except Stop as s:
            R["S2_build"]["stopped_at"] = str(s)
            fact("S2 STOPPED: %s" % s)
        except Exception as e:                                                     # noqa: BLE001
            R["S2_build"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            fact("S2 raised %s: %s" % (type(e).__name__, str(e)[:600]))
    else:
        close_quietly(OP)
        R["S2_build"]["not_attempted"] = "S1 did not resolve the donor's cast node; nothing was built."
        fact("S2 NOT ATTEMPTED: %s" % R["S2_build"]["not_attempted"])
    dump()

    if not op_ok and os.path.exists(OP) and not isinstance(R["S2_build"].get("saved_bytes"), int):
        try:
            os.remove(OP)
            fact("S2 cleanup: the UNSAVED op file was removed (it was a byte copy of the donor with nothing "
                 "of its own saved into it). NOTHING SAVED IS EVER DELETED.")
        except Exception as e:                                                     # noqa: BLE001
            fact("S2 cleanup: removing %s FAILED %s: %s" % (os.path.basename(OP), type(e).__name__, e))

    if op_ok:
        try:
            phase_s345()
        except Stop as s:
            R["S3_ground_truth"]["stopped_at"] = str(s)
            fact("S3/S4/S5 STOPPED: %s" % s)
        except Exception as e:                                                     # noqa: BLE001
            R["S3_ground_truth"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            fact("S3/S4/S5 raised %s: %s" % (type(e).__name__, str(e)[:600]))
    else:
        R["S3_ground_truth"]["not_attempted"] = ("the reader did not reach a legal save point, so there is "
                                                 "nothing to validate. ExecState at the pass point: %r ; "
                                                 "reason: %r"
                                                 % (R["pass_criteria"]["op_execstate"],
                                                    R["S2_build"].get("stopped_because")))
        fact("S3/S4/S5 NOT ATTEMPTED: %s" % R["S3_ground_truth"]["not_attempted"])
    dump()

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
    gate("S5_e4 the scratch was DELETED in the same run", not os.path.exists(SCRATCH),
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
    gate("Z3 the DONOR OpNodeLabels_v0.vi is byte-unchanged", zd.get("md5") == DONOR_MD5,
         "%s vs %s" % (zd.get("md5"), DONOR_MD5))
    zc = probe("Z3b OpCreateLocal_v0.vi after everything", CREATOR)
    gate("Z3b OpCreateLocal_v0.vi is byte-unchanged", zc.get("md5") == CREATOR_MD5,
         "%s vs %s" % (zc.get("md5"), CREATOR_MD5))
    R["recipes_listing_after"] = sorted(os.listdir(rp))
    gate("Z4 tools/recipes/ holds exactly the same file list after the run as before it",
         R["recipes_listing_after"] == R["recipes_listing_before"],
         "%d files before, %d after; diff %r"
         % (len(R["recipes_listing_before"]), len(R["recipes_listing_after"]),
            sorted(set(R["recipes_listing_after"]) ^ set(R["recipes_listing_before"]))))

    print("\n--- THE ANSWER TABLE (readings, not a recommendation)", flush=True)
    KS = R["S1_seed"]
    fact("S1  TMSC %r ; its `%s` wire %r produced by %d node(s) on that diagram ; panel object(s) carrying "
         "that wire %r ; the Wire row %r ; the existing cast verb can cast to Local: %r"
         % (KS.get("tmsc_nodes"), T_CAST_IN, KS.get("tmsc_target_class_wire"),
            len(KS.get("seed_wire_producers_among_nodes") or []),
            KS.get("panel_objects_carrying_the_seed_wire"), KS.get("seed_wire_row"),
            (KS.get("cast_verb") or {}).get("can_cast_to_Local")))
    K0 = R["S2_build"]
    fact("S2  seed control %r ; TMSC `%s` row after %r ; `reference` row after %r ; ExecState at the pass "
         "point %r ; saved %r bytes -> md5 %r size %r version %r ; the reader's indicator label %r ; "
         "stopped_because %r"
         % ((K0.get("seed_control") or {}).get("label_from_the_machine"), T_CAST_IN,
            (K0.get("seed_wiring") or {}).get("target_class_row_after"),
            (K0.get("cast_to_property_wire") or {}).get("reference_row_after"),
            R["pass_criteria"]["op_execstate"], K0.get("saved_bytes"),
            K0.get("file_after", {}).get("md5"), K0.get("file_after", {}).get("size"),
            K0.get("file_after", {}).get("version_candidates"),
            R["pass_criteria"]["reader_indicator_label"], K0.get("stopped_because")))
    K1 = R["S3_ground_truth"]
    fact("S3  `Local` census %r ; uid -> Control Name %r ; strings ending in .vi %r"
         % (K1.get("local_census_before"),
            [(r.get("uid_from_report_all"), r.get("control_name")) for r in K1.get("control_name_reads", [])],
            K1.get("strings_that_are_vi_file_names")))
    K2 = R["S4_open_question"]
    fact("S4  label from the machine %r (hex %r) ; creator error cluster %s ; new Local %r ; ExecState %r -> "
         "%r ; READER says %r ; equal to the label asked for %r"
         % (K2.get("label_from_the_machine"), K2.get("label_hex"),
            K2.get("creator_call", {}).get("error_cluster_verbatim"),
            K2.get("creator_call", {}).get("new_local_uids"), K2.get("exec_state_before"),
            K2.get("exec_state_after"), K2.get("reader_readback", {}).get("control_name"),
            K2.get("matches_the_label_asked_for")))
    K3 = R["S5_hygiene"].get("consecutive", {})
    fact("S5  %r/%r calls returned a string ; handles %r -> %r ; refs %r"
         % (K3.get("n_with_a_string"), K3.get("n"), K3.get("handles_before"), K3.get("handles_after"),
            R.get("ref_counts_after_20")))
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
