"""diag_s3b_l0_createlocal - cycle 60 material #1. S3b-L0: BUILD `OpCreateLocal_v0.vi` exactly as
`docs/cycle27-plan.md` Pre-decided 49(d) specifies it, and SELF-TEST it on a SCRATCH copy.

A DIAGNOSTIC under tools/bench/, NEVER a recipe (STATUS `## NEXT` line 76 / 48(n): a RECIPE build is refused in
any cycle that has already produced a build log, so L0/M1 run as diagnostics, as every S3a sub-step did).
Nothing under tools/recipes/ is written, renamed or launched by this file.

AUTHORISATION FOR A NEW OP VI - 46(k) (`docs/cycle27-plan.md:1697-1705`), quoted in its own words as the brief
requires: `docs/cycle27-plan.md:31` reads *"**No further process device** (user, 08:53) - still the standing
order. A retrospective naming one is a finding."*  46(k): *"A **process device** is gate and retrospective
machinery; an **op VI** is deliverable-construction tooling ... So the order does not reach an op VI that places
a Local Variable, and **the S3b transport needs no decision from the user**: if `Control -> Create:Local
Variable` 6331C02 through `build_invoke` is the route, it is simply built."*
49(i)/48(m), stated here in writing because the brief is required to say it: THIS OP WILL BE REVISED ON ANY
REVIEW THAT GATES IT.

=====================================================================================================
WHY THE OP IS NEEDED AT ALL - MEASURED, NOT ASSUMED (49(b), cycle 59 material #2's files-only census):
`local` occurs ONCE in tools/gscript.py, in a comment (:830) - no verb creates a Local Variable; no `Op*.vi` in
claudeDev (108 files) carries `Local` in its name; `vi.lib\\Erdos Miller\\LV-Scripting\\Create*.vi` is 50 files
with no local-variable creator; `Local` is grep-absent from docs/vi-server-ids.json.
And 49(c): the external fact dispatch (archive/peer/2026-09-21-s3b-local-variable-route.md) returns, CITED to
labviewwiki, that `Create:Local Variable` 6331C02 takes NO input parameters and returns only a Local refnum - so
the CONTROL INSTANCE the method is invoked on IS the binding. `build_invoke`'s own `reference` input is
deliberately UNWIRED (gscript.py:2164-2166), which is why the wrapper cannot be the vehicle and an op VI must
hold the wire.

*** 49(d)'s RIDER, BINDING ON HOW THIS RUN IS SCORED ***
"6331C02 takes no parameters" comes from a wiki page that SELF-DECLARES its parameter table incomplete. If the
method turns out to take parameters after all, THAT IS A MEASUREMENT THIS RUN RECORDS, NOT A FAILURE OF THE
SUB-STEP. L0 is never scored against an assumption the sources never supported. Gate L0_a4 therefore only
asserts that the created Invoke node was READ; the parameter table itself is a FACT, never a pass/fail.

WHAT ALREADY EXISTED - checked before a line of this was written (CLAUDE.md "check what exists before creating
anything"; `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`, docs/toolkit-capabilities.md):
  * tools/recipes/build_opconpaneassign.py - THE PRECEDENT, followed step for step: copy OpFPLabels_v0 -> the
    new op, then `build_invoke` a method node and wire the IndexArray's `element` (a live Control refnum) into
    it. Its own words (:9-11): "Built from OpFPLabels_v0, which ALREADY produces exactly the input this method
    needs: `VI -> Front Panel (23D) -> Panel.Controls[] (6348801) -> Index Array[`index`] -> element` is a
    Control refnum for the front-panel object at tabbing position `index`."
  * gscript.conpane_assign :2774 - the PRECEDENT FOR 49(d)'s INTERFACE: it takes the owned LABEL, resolves it to
    a Panel.Controls[] position with `fp_labels`, and drives the op by that index. 49(d)'s "match the requested
    label" is that resolution; the op's own `Text` indicator reports back WHICH label it walked to, off the
    machine, so the match is verified rather than assumed.
  * gscript verbs used, ALL pre-existing, NONE patched: op :210, ref_counts :233, report :455, report_all :488,
    node_labels :587, node_terms_uid :925, count :1005, uids :1017, open_panel :1241, close_panel :1257,
    ensure_loaded :1268, wire :1340, exec_state :1977, save :2062, build_invoke :2159, build_property :2194,
    delete_object :2240, fp_labels :2440, _run :341, _err :435, reset :262.
  * tools/recipes/build_d1_v0.py - move_in :318, owner_of :338, diag_index :357 (unchanged).
  * tools/bench/diag_s2_scaffold.py - ORIGINAL/ORIG_MD5/S1_ARTEFACT/S1_MD5, fresh(), Preload(), file_facts(),
    version_bytes(); tools/hash_probe.py - probe(); tools/bench_prep.py - labview_handles().
NO new gscript verb is added and no fleet file is patched. The Python-side wrapper `create_local()` lives IN
THIS DIAGNOSTIC; promoting it into tools/gscript.py is judgement's call, not this run's.

=====================================================================================================
THE OP, EXACTLY AS 49(d) FIXES IT (so nothing here is designed by a material session)
  in       : VI ref (the donor's `vi path`), the control's owned LABEL (resolved to its Panel.Controls[]
             position by fp_labels, as conpane_assign does), the destination diagram, a position
  internals: VI.Front Panel 23D -> Panel.Controls[] 6348801 -> Index Array[`index`] -> THE LIVE CONTROL
             REFERENCE -> (kept from the donor) Control.Label 6332005 -> Text.Text, which REPORTS the label the
             op actually walked to; and, NEW, on that same live Control reference an Invoke node
             `Create:Local Variable` 6331C02 with no parameters
  out      : the op's `Text` (the matched label) + the error cluster; and, read back off the machine by the
             wrapper, the new object's uid (whole-VI `Local` uid SET diff), class (report_all) and bound label
             (node_labels on the diagram it was born on - an implicit node's LABEL IS the bound control's name,
             gscript.py:589-592). ** A G-SIDE readback of the bound name would need `Local.Control Name`
             6355400, which is ROUTE B's unverified ID and is REPORT-ONLY this dispatch - so the readback is
             taken with the fleet's existing readers. Stated as a deviation from 49(d) AS WRITTEN. **
  relocate : ONLY if the readback says it was not born on the destination diagram - move_in(build_d1_v0:318).
  hygiene  : it closes every reference it opens - the donor's own ladder plus one Invoke; the wrapper releases
             every cached reference (g.reset()) and the 20-call gate reads the handle count either side.

ROUTE B (`New VI Object` style 2061 + `Local.Control Name` 6355400) IS NOT BUILT (49(d): B needs TWO unverified
IDs). This run only REPORTS whether those two resolve on this machine - as a measurement, never as a repair.

=====================================================================================================
PREDICTION CONTRACT (every gate is the readback of a CALL, 46(g); FATAL stops the chain and still dumps JSON)
  T1    the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                        FATAL
  T1b   claudeDev\\D1_s1_copy.vi md5 == 3e3d23cefd3a334001aa9d6156bf1aee
  T2    claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                              FATAL
  T3    claudeDev\\D1_s3a_focus_ind.vi md5 == eef91c1d91f16b034707e4d1285ca8cb                         FATAL
  T4    claudeDev\\OpFPLabels_v0.vi (the DONOR) exists; its md5 is recorded for the Z gate
  L0_a1 the copy opens and reads ExecState 1 before any edit
  L0_a2 exactly ONE IndexArray is on the copy's diagram (the donor's `Index Array[index]`)
  L0_a3 build_invoke put exactly 1 new Invoke on the copy (a RAISE is a LEGITIMATE reading - 49(d) rider)
  L0_a4 the new Invoke's FULL terminal table was READ off the machine       (the 49(d) RIDER measurement; the
        parameter list itself is a FACT, never pass/fail)
  L0_a5 the Invoke carries a terminal named 'reference'
  L0_a6 IA.'element' -> INV.'reference' returned with an EMPTY error column, AND the reference terminal's wire
        uid is non-zero afterwards                                                        (the EFFECT gate)
  L0_a7 ExecState == 1 after the wiring                          *** THE OP'S OWN PASS CRITERION - no save
                                                                     is attempted below it, no repair either ***
  L0_a8 g.save(OP) returned a byte count and the file's version bytes read 26 00 80 00 (LV2026)
  L0_b0 the scratch copy is byte-identical to D1_s3a_focus_ind.vi at creation
  L0_b1 the scratch opens at ExecState 1 and its `Local` census is READ (docs/toolkit-capabilities.md:284 says
        8 on this VI; the READING is the gate, never the 8)
  L0_b2 'index' is on the scratch's front panel and its position is resolved by fp_labels
  L0_b3 CALL 1 returned: the error cluster / dialog text VERBATIM, and the `Local` uid SET diff
  L0_b4 CALL 1 created EXACTLY ONE new Local    (zero is a LEGITIMATE reading - it is the 49(d) rider's answer)
  L0_b5 the new Local's class, owner_of and bound label were READ off the machine
  L0_b6 the bound label equals the label asked for                            *** THE L0 PASS CRITERION (49(e):
                                                                "the local exists, bound to the label asked for,
                                                                 ExecState 1, refs 0 live") ***
  L0_b7 ExecState after CALL 1 was READ (a 0 is a LEGITIMATE reading and is reported, not repaired)
  L0_b8 the relocation branch was exercised once (dest Diagram #639) and its owner_of read back
  L0_c1 20 consecutive calls ran; handles before/after recorded
  L0_c2 the handle count is flat within +-100 across the 20 calls   (a FAIL here is a FINDING, not a blocker -
        44(e)/49(j) measured ~24-33k unexplained growth per run with ref_counts reading 0 live)
  L0_c3 refs opened == closed, 0 live after the 20 calls
  L0_d1 REPORT ONLY: does `Local.Control Name` 6355400 resolve? (build_property('VI Server:Local',[('6355400',
        False)]) on the scratch - the creator's verdict, error VERBATIM; the probe node is deleted again)
  L0_d2 REPORT ONLY: `New VI Object` style 2061 - a files-level statement of whether ANY fleet verb can pass a
        style number at all (no new op is built to find out)
  Z0    the scratch copy was DELETED in the same run (CLAUDE.md rule 4)
  Z1    ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi / D1_s3a_focus_ind.vi md5 ALL unchanged after everything
  Z2    refs opened == closed, 0 live
  Z3    the DONOR OpFPLabels_v0.vi is byte-unchanged
  Z4    no file was created under tools/recipes/ by this run

PREDICTED RISKS, written down BEFORE the run:
  (i)   build_invoke's `error out` is UNWIRED by construction (gscript.py:2166-2168), so an unsupported method
        ID fails SILENTLY and returns a node carrying only reference/reference out/error in/error out - exactly
        how `VI.Get Errors` 452 failed (docs/toolkit-capabilities.md). L0_a4's terminal-table read is what
        distinguishes the two, and it is a FACT either way.
  (ii)  the donor's `element` output is ALREADY WIRED (to the Control.Label property node), so the new wire is a
        BRANCH: `branch=True`, and branching from an already-wired source is declined SILENTLY (gscript.py:1346-
        1349). That is why L0_a6 verifies by EFFECT - the reference terminal's wire uid - and not by return.
  (iii) an errored Invoke with an unwired error out raises LabVIEW's automatic-error-handling dialog; g._run
        turns that into RuntimeError("... modal dialog ..."). Captured VERBATIM as the call's reading - for a
        no-parameter call that errors, THAT IS the answer to question 3 and costs ~8 s per call.
  (iv)  Nodes[]/Traverse indices SHIFT on every mutation (34(h)): every index is re-resolved by uid echo
        immediately before use.
  (v)   where LabVIEW puts the new Local is NOT known in advance. The wrapper reads owner_of and relocates only
        if it differs from the destination - 49(d)'s own words.

BOUNDS. NO VI IS RUN (34(f)) - the only VIs that execute are the fleet's op VIs, which is what scripting is.
No GUI action. No motor / ASI / camera (rig 조립 / ASSEMBLED; the gate `tools/motor_gate.py` is not called and
no serial port is opened). No new PROCESS device. No recipe. `remove_bad_wires_scripted` is REFUSED - not
imported, not called; the GUI menu form gscript.py:1629 is not called either. `gui_save` is NEVER called and
`allow_broken` is NEVER True. Originals are never opened for write. NOTHING SAVED IS EVER DELETED except the
SCRATCH self-test copy, which 49(e)/CLAUDE.md rule 4 require to be deleted in the same run. NO ROUTE IS CHOSEN
OR RECOMMENDED and no plan document or STATUS `## NEXT` line is edited - that is judgement's call.
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
from build_d1_v0 import diag_index, owner_of, move_in                              # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"

DONOR = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpCreateLocal_v0.vi")

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_L0_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_s3b_l0_createlocal.json")

LOCAL_METHOD = "6331C02"            # Control -> Create:Local Variable (docs/cycle27-plan.md:1678, :1703)
CONTROL_CLASS = "VI Server:Control"  # docs/vi-server-ids.json:8
INVOKE_AT = (760, 430)              # empty canvas on the donor's small diagram
TARGET_LABEL = "index"              # the numeric leg's indicator label, READ off the machine in cycle 59
D536 = 536                          # the TopLevelDiagram
D639 = 639                          # the frame-loop BODY diagram - the relocation exercise's destination
MOVE_POSITION = (160, 4200)
N_CONSECUTIVE = 20                  # 49(d): "20 consecutive calls with the handle count flat +-100"
SCAN_LIMIT = 60
STD_INVOKE_TERMS = ("reference", "reference out", "error in (no error)", "error in", "error out")
ROUTE_B_PROP = "6355400"            # Local.Control Name - UNVERIFIED, REPORT ONLY (docs/NAMES.md:260)
ROUTE_B_STYLE = 2061                # New VI Object style - UNVERIFIED, REPORT ONLY

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "S3b-L0 (Pre-decided 49(d)+49(e)): build OpCreateLocal_v0.vi from donor OpFPLabels_v0 by adding an "
             "Invoke `Control -> Create:Local Variable` 6331C02 on the live Control reference the donor's "
             "IndexArray already produces, then SELF-TEST it on a SCRATCH copy of D1_s3a_focus_ind.vi.",
     "authorisation": "46(k), docs/cycle27-plan.md:1697-1705 - Pre-decided 2 forbids a further PROCESS DEVICE, "
                      "not an op VI; quoted verbatim in the module docstring.",
     "will_be_revised_on_any_review_that_gates_it": "49(i)/48(m) - stated in the brief and repeated here.",
     "rider_49d": "'6331C02 takes no parameters' comes from a wiki page that self-declares its parameter table "
                  "incomplete. If the method takes parameters, that is a MEASUREMENT recorded here, NOT a "
                  "failure of L0.",
     "route_b_not_built": {"style": ROUTE_B_STYLE, "property": ROUTE_B_PROP,
                           "note": "REPORTED ONLY, never attempted as a repair (49(d))."},
     "chooses_no_route": True, "recommends_no_route": True, "interprets_nothing": True,
     "no_vi_was_run": True, "no_new_device": True, "no_gui_action": True, "no_recipe": True,
     "new_op_vi": OP, "edits_no_plan_document": True, "edits_no_status_next": True,
     "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "REFUSED by the brief - not imported, not called; the GUI menu form "
                                  "(gscript.py:1629) is not called either.",
     "gui_save": "NEVER called", "allow_broken": "NEVER True",
     "rig_state": "조립 / ASSEMBLED (motors + ASI only through tools/motor_gate.py, which is not called; camera "
                  "not needed and not touched)",
     "citations": {"op_shape": "docs/cycle27-plan.md Pre-decided 49(d)",
                   "decomposition": "Pre-decided 49(e) (S3b-L0)",
                   "why_no_verb_exists": "Pre-decided 49(b)",
                   "method_takes_no_parameters": "Pre-decided 49(c); archive/peer/2026-09-21-s3b-local-"
                                                 "variable-route.md",
                   "precedent_builder": "tools/recipes/build_opconpaneassign.py",
                   "precedent_interface": "tools/gscript.py:2774 (conpane_assign takes the LABEL)",
                   "panel_controls": "docs/vi-server-ids.json:47 (Panel.Controls[] 6348801)",
                   "control_label": "docs/vi-server-ids.json:21 (Control.Label 6332005)",
                   "implicit_node_label_is_the_bound_name": "tools/gscript.py:589-592",
                   "move_in_owner_of_diag_index": "tools/recipes/build_d1_v0.py:318,:338,:357",
                   "local_census_8": "docs/toolkit-capabilities.md:284",
                   "diagnostic_not_recipe": "STATUS ## NEXT line 76; Pre-decided 48(n)",
                   "handles_caveat": "Pre-decided 44(e)/49(j)",
                   "scratch_deleted_same_run": "CLAUDE.md rule 4; Pre-decided 49(e)"},
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "s3a_artefact": {"path": S3A_ARTEFACT, "md5_pin": S3A_MD5},
     "donor": {"path": DONOR}, "handles": {}, "hash_probe": [],
     "A_build": {}, "B_selftest": {}, "route_b_probe": {}, "artefacts": [],
     "pass_criteria": {"op_execstate": None, "L0": None}}


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


def owner_read(rec, tag, uid, target):
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


def close_quietly(target):
    try:
        g.close_panel(target)
    except Exception as e:                                                         # noqa: BLE001
        fact("close_panel(%s) raised %s: %s" % (os.path.basename(target), type(e).__name__, e))


# ============================================================ PHASE A: BUILD THE OP VI
def phase_a():
    """copy the donor -> add the 6331C02 Invoke -> branch the live Control ref into its `reference` -> save."""
    K = R["A_build"]
    print("\n===================================================================", flush=True)
    print("=== S3b-L0 PHASE A   build %s from donor %s" % (os.path.basename(OP), os.path.basename(DONOR)),
          flush=True)
    print("===================================================================", flush=True)

    if os.path.exists(OP):
        os.remove(OP)
        fact("an OLD %s was on disk and was removed before the copy (never load a VI you are about to "
             "overwrite - build_opconpaneassign.py:14)" % os.path.basename(OP))
    shutil.copy2(DONOR, OP)
    K["file_at_creation"] = probe("L0_a0 the op file at creation (copied from the donor)", OP)

    g.open_panel(OP)
    time.sleep(1.0)
    try:
        _phase_a_body(K)
    finally:
        close_quietly(OP)
    dump()
    return isinstance(K.get("saved_bytes"), int)


def _phase_a_body(K):
    K["baseline"] = {"Node": count_of(OP, "Node"), "Wire": count_of(OP, "Wire"),
                     "Property": count_of(OP, "Property"), "IndexArray": count_of(OP, "IndexArray"),
                     "Invoke": count_of(OP, "Invoke")}
    es0 = read_exec_state(K, "A the copy, before any edit", OP)
    K["exec_state_baseline"] = es0
    fact("A baseline census of the copy: %r" % (K["baseline"],))
    gate("L0_a1 the copy opens and reads ExecState 1 before any edit", es0 == 1, "%r" % (es0,))

    try:
        ias = g.report(OP, "IndexArray")
    except Exception as e:                                                         # noqa: BLE001
        ias = []
        fact("A report(IndexArray) raised %s: %s" % (type(e).__name__, str(e)[:200]))
    K["index_arrays"] = [{"i": o["i"], "uid": o["uid"], "pos": o["pos"]} for o in ias]
    fact("A the copy's IndexArray objects: %r" % (K["index_arrays"],))
    gate("L0_a2 exactly ONE IndexArray is on the copy's diagram", len(ias) == 1, "%d" % len(ias))
    if len(ias) != 1:
        raise Stop("L0_a2: the donor ladder is not the shape build_opconpaneassign.py:105 measured "
                   "(IndexArray count %d) - nothing is improvised on top of that." % len(ias))
    ia_uid = ias[0]["uid"]

    # ---- a3: the Invoke node. A RAISE here is a LEGITIMATE reading (49(d) rider).
    print("\n--------- L0_a3  build_invoke(%r, %r) at %r" % (CONTROL_CLASS, LOCAL_METHOD, INVOKE_AT), flush=True)
    inv_before = count_of(OP, "Invoke")
    rd = {"class": CONTROL_CLASS, "method_id": LOCAL_METHOD, "location": INVOKE_AT,
          "invoke_count_before": inv_before}
    try:
        new = g.build_invoke(OP, CONTROL_CLASS, LOCAL_METHOD, INVOKE_AT)
        rd["new"] = [{"uid": o["uid"], "pos": o["pos"]} for o in new]
        rd["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rd["new"] = None
        rd["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    rd["invoke_count_after"] = count_of(OP, "Invoke")
    K["build_invoke"] = rd
    fact("L0_a3 build_invoke -> new %r ; Invoke census %r -> %r ; error VERBATIM %r"
         % (rd["new"], inv_before, rd["invoke_count_after"], rd["error_verbatim"]))
    gate("L0_a3 build_invoke put exactly 1 new Invoke on the copy", bool(rd["new"]) and len(rd["new"]) == 1,
         "%r (a RAISE is a legitimate reading - 49(d) rider)" % (rd["error_verbatim"] or rd["new"],))
    if not rd["new"]:
        raise Stop("L0_a3: no Invoke node was created - RECORDED as the 49(d)-rider measurement, "
                   "and nothing is repaired or worked around.")
    inv_uid = rd["new"][0]["uid"]

    # ---- a4: THE RIDER MEASUREMENT - the node's FULL terminal table, read off the machine
    print("\n--------- L0_a4  the new Invoke's FULL terminal table (the 49(d) RIDER measurement)", flush=True)
    i_nodes, rows = node_index_of(OP, 0, inv_uid)
    terms = [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]), "wire": r["wire"]}
             for r in rows]
    extra = [t for t in terms if t["name"] not in STD_INVOKE_TERMS]
    K["invoke_terminals"] = {"nodes_index": i_nodes, "terms": terms, "beyond_the_standard_four": extra,
                             "names_hex": {t["name"]: t["name"].encode("utf-8").hex() for t in terms}}
    fact("L0_a4 the Invoke #%s sits at Nodes[%r]; FULL terminal table READ OFF THE MACHINE: %r"
         % (inv_uid, i_nodes, terms))
    fact("L0_a4 RIDER: terminals BEYOND reference/reference out/error in/error out = %r. An EMPTY list "
         "corroborates the wiki's 'no input parameters, returns a Local refnum only' (49(c)); a NON-EMPTY list "
         "is the measurement 49(d)'s rider anticipates and is NOT a failure." % (extra,))
    gate("L0_a4 the new Invoke's FULL terminal table was READ off the machine", bool(terms),
         "%d terminals" % len(terms))
    ref_term = next((t for t in terms if t["name"] == "reference"), None)
    gate("L0_a5 the Invoke carries a terminal named 'reference'", ref_term is not None, "%r" % (ref_term,))
    if ref_term is None:
        raise Stop("L0_a5: the created Invoke has no 'reference' terminal - the live Control reference has "
                   "nowhere to go. RECORDED; no alternative is improvised.")

    # ---- a6: BRANCH the live Control reference into the Invoke's reference input
    print("\n--------- L0_a6  IA.'element' -> INV.'reference'  (a BRANCH: the donor already wires `element`)",
          flush=True)
    ia_i = [o["uid"] for o in g.report(OP, "IndexArray")].index(ia_uid)
    inv_i = [o["uid"] for o in g.report(OP, "Invoke")].index(inv_uid)
    wr = {"ia_uid": ia_uid, "ia_index": ia_i, "inv_uid": inv_uid, "inv_index": inv_i,
          "wire_count_before": count_of(OP, "Wire")}
    try:
        wr["wire_count_after"] = g.wire(OP, "IndexArray", ia_i, "element", "Invoke", inv_i, "reference",
                                        branch=True)
        wr["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        wr["wire_count_after"] = count_of(OP, "Wire")
        wr["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    _, rows2 = node_index_of(OP, 0, inv_uid)
    after_terms = [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]), "wire": r["wire"]}
                   for r in rows2]
    ref_after = next((t for t in after_terms if t["name"] == "reference"), None)
    wr["reference_terminal_after"] = ref_after
    K["wire"] = wr
    fact("L0_a6 wire IA.element -> INV.reference: Wire census %r -> %r ; error VERBATIM %r ; the reference "
         "terminal AFTER = %r" % (wr["wire_count_before"], wr["wire_count_after"], wr["error_verbatim"],
                                  ref_after))
    gate("L0_a6 the wire landed - empty error column AND a non-zero wire uid on 'reference'",
         wr["error_verbatim"] == "" and bool(ref_after) and bool(ref_after.get("wire")),
         "error %r, reference wire %r" % (wr["error_verbatim"], (ref_after or {}).get("wire")))

    es1 = read_exec_state(K, "A after the wiring", OP)
    R["pass_criteria"]["op_execstate"] = es1
    ok = gate("L0_a7 ExecState == 1 after the wiring  *** THE OP'S OWN PASS CRITERION ***", es1 == 1, "%r" % (es1,))
    K["census_after"] = {"Node": count_of(OP, "Node"), "Wire": count_of(OP, "Wire"),
                         "Invoke": count_of(OP, "Invoke"), "Property": count_of(OP, "Property")}
    fact("A census after the edit: %r" % (K["census_after"],))
    try:
        K["op_front_panel"] = [(i, lab, ind) for i, lab, ind in g.fp_labels(OP, max_n=60)]
        fact("A the op's own front-panel objects (its API): %r" % (K["op_front_panel"],))
    except Exception as e:                                                         # noqa: BLE001
        fact("A fp_labels(OP) raised %s: %s" % (type(e).__name__, str(e)[:200]))

    if not ok:
        fact("A: ExecState is not 1 - THE OP IS NOT SAVED and nothing is repaired (the brief refuses "
             "remove_bad_wires_scripted / gui_save / allow_broken).")
        return
    try:
        K["saved_bytes"] = g.save(OP)
        fact("A saved %r bytes" % (K["saved_bytes"],))
    except Exception as e:                                                         # noqa: BLE001
        K["saved_bytes"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:300])
        fact("A g.save(OP) raised %s: %s" % (type(e).__name__, str(e)[:300]))
    K["file_after"] = D.file_facts("L0_a8 the op VI after the save", OP)
    R["artefacts"].append({"step": "L0 op VI", "path": OP, "saved": isinstance(K.get("saved_bytes"), int),
                           "file": K["file_after"]})
    gate("L0_a8 g.save returned a byte count and the file reads LV2026 (26 00 80 00)",
         isinstance(K.get("saved_bytes"), int)
         and any(c["bytes"].startswith("26 00 80 00") for c in K["file_after"].get("version_candidates", [])),
         "%r / %r" % (K.get("saved_bytes"), K["file_after"].get("version_candidates")))


# ============================================================ THE WRAPPER (49(d)'s interface)
def create_local(target, label, fp_map, dest_diagram_uid=None, position=MOVE_POSITION, tag=""):
    """49(d)'s op interface, Python side. in: VI ref (a path), the control's owned LABEL, the destination
    diagram, a position. Resolves the label to its Panel.Controls[] position with fp_labels EXACTLY as
    gscript.conpane_assign:2782-2788 does, drives the op, and reads the new object back off the machine:
    uid (whole-VI `Local` uid SET diff), class (report_all), bound label (node_labels on the diagram it was
    born on). Relocates ONLY if the readback says it was not born on the destination diagram."""
    rd = {"tag": tag, "label_asked_for": label, "label_hex": label.encode("utf-8").hex(),
          "dest_diagram_uid": dest_diagram_uid, "position": position}
    if label not in fp_map:
        rd["error_verbatim"] = "the label %r is not a front-panel object of %s" % (label,
                                                                                  os.path.basename(target))
        return rd
    rd["panel_index"] = fp_map[label]
    g.ensure_loaded(target)
    before, err0 = uid_set(target, "Local")
    rd["local_uids_before"] = len(before)
    rd["local_uid_read_error"] = err0

    vi = g.op(OP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("index", fp_map[label])
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
        rd["error_cluster_verbatim"] = "NO 'error out' INDICATOR ON THE OP (%s: %s)" % (type(e).__name__,
                                                                                        str(e)[:80])
    after, err1 = uid_set(target, "Local")
    rd["local_uids_after"] = len(after)
    rd["local_uid_read_error_after"] = err1
    rd["new_local_uids"] = sorted(after - before)
    rd["lost_local_uids"] = sorted(before - after)
    return rd


def read_back(rd, target):
    """uid -> class + owner + BOUND LABEL, all read off the machine (never retyped)."""
    uids = rd.get("new_local_uids") or []
    if len(uids) != 1:
        rd["readback"] = {"note": "no single new Local to read back (%r)" % (uids,)}
        return rd
    uid = uids[0]
    rb = {"uid": uid}
    try:
        rows = g.report_all(target, "Local")
        me = next((o for o in rows if o["uid"] == uid), None)
        rb["report_all_row"] = me
        rb["class"] = (me or {}).get("class")
        rb["owner_class_from_report_all"] = (me or {}).get("owner")
        rb["pos"] = (me or {}).get("pos")
        rb["members"] = len(rows)
    except Exception as e:                                                         # noqa: BLE001
        rb["report_all_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    own = owner_read(rb, "readback owner of the new Local", uid, target)
    rb["owner"] = (own.get("owner_class"), own.get("owner_uid"))
    # RUN 1's INSTRUMENT DEFECT, fixed here and recorded: this branch tested `== "Diagram"` only, so a Local
    # born on the TOP LEVEL - owner_of answers ('TopLevelDiagram', 536), which diag_index resolves to 0 exactly
    # as cycle 58's gate B1_A2 measured - never reached node_labels and the bound label read back None. The
    # MACHINE said nothing about the binding in run 1; the reader did.
    try:
        di = (diag_index(target, own.get("owner_uid"))
              if own.get("owner_class") in ("Diagram", "TopLevelDiagram") else None)
        rb["owner_diagram_index"] = di
    except Exception as e:                                                         # noqa: BLE001
        di = None
        rb["owner_diagram_index_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    if di is None:
        rb["bound_label_not_read_because"] = ("owner_of answered %r, which is neither Diagram nor "
                                              "TopLevelDiagram, so no Traverse diagram index could be "
                                              "resolved" % (rb.get("owner"),))
    if di is not None:
        try:
            labs = g.node_labels(target, di)
            row = next((r for r in labs if r["uid"] == uid), None)
            rb["node_labels_row"] = row
            rb["bound_label"] = (row or {}).get("label")
            rb["bound_label_hex"] = ((row or {}).get("label") or "").encode("utf-8").hex()
            rb["nodes_on_that_diagram"] = len(labs)
        except Exception as e:                                                     # noqa: BLE001
            rb["node_labels_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    rd["readback"] = rb
    fact("readback of Local #%s: class %r, owner %r, BOUND LABEL READ OFF THE MACHINE %r (hex %r)"
         % (uid, rb.get("class"), rb.get("owner"), rb.get("bound_label"), rb.get("bound_label_hex")))
    return rd


def relocate_if_needed(rd, target, dest_uid, position):
    """49(d): 'relocate afterwards only if the readback says it was not born on the destination diagram'."""
    rb = rd.get("readback") or {}
    uid = rb.get("uid")
    mv = {"dest_diagram_uid": dest_uid, "owner_before": rb.get("owner")}
    if uid is None or dest_uid is None:
        mv["note"] = "nothing to relocate"
        rd["relocate"] = mv
        return rd
    if rb.get("owner") == ("Diagram", dest_uid):
        mv["note"] = "BORN on the destination diagram - no relocation attempted (49(d))"
        rd["relocate"] = mv
        fact("relocate: %s" % mv["note"])
        return rd
    try:
        di = diag_index(target, dest_uid)
        mv["dest_diagram_index"] = di
        mv["returned"] = move_in(target, uid, di, position)
        mv["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        mv["returned"] = None
        mv["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    own = owner_read(mv, "owner AFTER the relocation", uid, target)
    mv["owner_after"] = (own.get("owner_class"), own.get("owner_uid"))
    rd["relocate"] = mv
    fact("relocate Local #%s -> Diagram #%s: returned %r, error VERBATIM %r, owner %r -> %r"
         % (uid, dest_uid, mv.get("returned"), mv.get("error_verbatim"), mv.get("owner_before"),
            mv.get("owner_after")))
    return rd


# ============================================================ PHASE B: SELF-TEST ON A SCRATCH COPY
def phase_b():
    K = R["B_selftest"]
    print("\n===================================================================", flush=True)
    print("=== S3b-L0 PHASE B   self-test on %s" % os.path.basename(SCRATCH), flush=True)
    print("=== the bed is a SCRATCH duplicate of D1_s3a_focus_ind.vi (49(e): never the artefact itself)",
          flush=True)
    print("===================================================================", flush=True)
    shutil.copy2(S3A_ARTEFACT, SCRATCH)
    p = probe("L0_b0 the scratch at creation", SCRATCH)
    K["scratch"] = {"path": SCRATCH, "at_creation": p}
    gate("L0_b0 the scratch copy is byte-identical to D1_s3a_focus_ind.vi at creation",
         p.get("md5") == S3A_MD5, "%s (expected %s)" % (p.get("md5", "?"), S3A_MD5))

    g.open_panel(SCRATCH)
    time.sleep(1.0)
    try:
        _phase_b_body(K)
    finally:
        close_quietly(SCRATCH)
    dump()


def _phase_b_body(K):
    es0 = read_exec_state(K, "B the scratch, before any call", SCRATCH)
    K["local_census_before"] = count_of(SCRATCH, "Local")
    K["control_terminal_census"] = count_of(SCRATCH, "ControlTerminal")
    fact("B baseline: ExecState %r, `Local` census %r (docs/toolkit-capabilities.md:284 records 8 on this VI - "
         "the READING is the gate, never the 8), ControlTerminal census %r"
         % (es0, K["local_census_before"], K["control_terminal_census"]))
    gate("L0_b1 the scratch opens at ExecState 1 and its `Local` census was READ",
         es0 == 1 and isinstance(K["local_census_before"], int),
         "ExecState %r, Local %r" % (es0, K["local_census_before"]))

    t0 = time.time()
    try:
        rows = g.fp_labels(SCRATCH, max_n=200)
    except Exception as e:                                                         # noqa: BLE001
        rows = []
        fact("B fp_labels raised %s: %s" % (type(e).__name__, str(e)[:200]))
    fp_map = {}
    for i, lab, _ind in rows:
        fp_map.setdefault(lab, i)
    K["fp_rows"] = len(rows)
    K["fp_sweep_s"] = round(time.time() - t0, 1)
    K["fp_map_has_target"] = TARGET_LABEL in fp_map
    K["fp_index_of_target"] = fp_map.get(TARGET_LABEL)
    K["fp_duplicate_labels"] = sorted({lab for _i, lab, _x in rows
                                       if [l for _j, l, _y in rows].count(lab) > 1})
    fact("B fp_labels swept %d panel objects in %.1f s; %r is at Panel.Controls[%r]; duplicate labels %r"
         % (len(rows), K["fp_sweep_s"], TARGET_LABEL, K["fp_index_of_target"], K["fp_duplicate_labels"]))
    gate("L0_b2 %r is on the scratch's front panel and its position resolved" % TARGET_LABEL,
         K["fp_map_has_target"] and isinstance(K["fp_index_of_target"], int),
         "%r" % (K["fp_index_of_target"],))
    if not K["fp_map_has_target"]:
        raise Stop("L0_b2: %r is not a front-panel object of the scratch - the op has nothing to bind to."
                   % TARGET_LABEL)

    # ---------------- CALL 1: the measurement the whole sub-step exists for
    print("\n--------- L0_b3  CALL 1  create_local(scratch, %r, dest = TopLevelDiagram #%d)"
          % (TARGET_LABEL, D536), flush=True)
    R["handles"]["before_call_1"] = labview_handles()
    c1 = create_local(SCRATCH, TARGET_LABEL, fp_map, dest_diagram_uid=D536, tag="CALL 1")
    K["call_1"] = c1
    fact("L0_b3 CALL 1 run %.2f s; the op's own `Text` (the label it WALKED TO, off the machine) = %r ; "
         "run error VERBATIM %r ; error cluster VERBATIM %s"
         % (c1.get("run_s", -1), c1.get("op_matched_label"), c1.get("run_error_verbatim"),
            c1.get("error_cluster_verbatim")))
    fact("L0_b3 `Local` uid census %r -> %r ; NEW uids %r ; LOST uids %r"
         % (c1.get("local_uids_before"), c1.get("local_uids_after"), c1.get("new_local_uids"),
            c1.get("lost_local_uids")))
    gate("L0_b3 CALL 1 returned and its error column / dialog text was captured VERBATIM",
         "run_error_verbatim" in c1, "%r" % (c1.get("run_error_verbatim"),))
    gate("L0_b4 CALL 1 created EXACTLY ONE new Local",
         len(c1.get("new_local_uids") or []) == 1,
         "%r (zero is a LEGITIMATE reading - it is the 49(d) rider's answer)" % (c1.get("new_local_uids"),))
    read_back(c1, SCRATCH)
    rb = c1.get("readback") or {}
    gate("L0_b5 the new Local's class, owner and bound label were READ off the machine",
         bool(rb.get("class")) and bool(rb.get("owner")) and rb.get("bound_label") is not None,
         "class %r owner %r bound %r" % (rb.get("class"), rb.get("owner"), rb.get("bound_label")))
    bound_ok = (rb.get("bound_label") == TARGET_LABEL)
    R["pass_criteria"]["L0"] = {"bound_label": rb.get("bound_label"), "asked_for": TARGET_LABEL,
                                "matches": bound_ok}
    gate("L0_b6 the bound label equals the label asked for  *** THE L0 PASS CRITERION (49(e)) ***",
         bound_ok, "%r vs %r" % (rb.get("bound_label"), TARGET_LABEL))
    es1 = read_exec_state(K, "B after CALL 1", SCRATCH)
    K["exec_state_after_call_1"] = es1
    gate("L0_b7 ExecState after CALL 1 was READ", es1 in (0, 1),
         "%r (a 0 is a LEGITIMATE reading and is reported, not repaired)" % (es1,))
    relocate_if_needed(c1, SCRATCH, D536, MOVE_POSITION)
    dump()

    # ---------------- CALL 2: the relocation branch, exercised once against a NESTED diagram
    print("\n--------- L0_b8  CALL 2  the relocation branch (dest = Diagram #%d)" % D639, flush=True)
    c2 = create_local(SCRATCH, TARGET_LABEL, fp_map, dest_diagram_uid=D639, tag="CALL 2 (relocation)")
    read_back(c2, SCRATCH)
    relocate_if_needed(c2, SCRATCH, D639, MOVE_POSITION)
    K["call_2"] = c2
    K["exec_state_after_call_2"] = read_exec_state(K, "B after CALL 2 + relocation", SCRATCH)
    mv = c2.get("relocate") or {}
    gate("L0_b8 the relocation branch was exercised and its owner_of read back",
         "owner_after" in mv or "note" in mv,
         "owner %r -> %r ; %r" % (mv.get("owner_before"), mv.get("owner_after"), mv.get("note")))
    dump()

    # ---------------- 20 consecutive calls: the hygiene gate
    print("\n--------- L0_c1  %d CONSECUTIVE CALLS (49(d): handles flat +-100, every reference closed)"
          % N_CONSECUTIVE, flush=True)
    R["ref_counts_before_20"] = g.ref_counts()
    h_before = labview_handles()
    R["handles"]["before_20"] = h_before
    loc_before = count_of(SCRATCH, "Local")
    t0 = time.time()
    runs = []
    for n in range(N_CONSECUTIVE):
        r = create_local(SCRATCH, TARGET_LABEL, fp_map, dest_diagram_uid=None, tag="consecutive %d" % (n + 1))
        runs.append({"n": n + 1, "new": r.get("new_local_uids"), "run_s": r.get("run_s"),
                     "error_verbatim": r.get("run_error_verbatim"),
                     "matched": r.get("op_matched_label")})
        print("     call %2d: new %r, %.2f s, error %r"
              % (n + 1, r.get("new_local_uids"), r.get("run_s", -1) or -1,
                 (r.get("run_error_verbatim") or "")[:90]), flush=True)
    h_after = labview_handles()
    R["handles"]["after_20"] = h_after
    R["ref_counts_after_20"] = g.ref_counts()
    loc_after = count_of(SCRATCH, "Local")
    K["consecutive"] = {"n": N_CONSECUTIVE, "runs": runs, "elapsed_s": round(time.time() - t0, 1),
                        "local_census_before": loc_before, "local_census_after": loc_after,
                        "handles_before": h_before, "handles_after": h_after,
                        "n_with_one_new": sum(1 for r in runs if len(r["new"] or []) == 1),
                        "n_with_an_error": sum(1 for r in runs if r["error_verbatim"])}
    fact("L0_c1 %d consecutive calls in %.1f s: %d produced exactly one new Local, %d carried an error; "
         "`Local` census %r -> %r"
         % (N_CONSECUTIVE, K["consecutive"]["elapsed_s"], K["consecutive"]["n_with_one_new"],
            K["consecutive"]["n_with_an_error"], loc_before, loc_after))
    fact("L0_c1 handles %r -> %r (delta %s); refs before %r after %r"
         % (h_before, h_after,
            (h_after - h_before) if isinstance(h_before, int) and isinstance(h_after, int) else "?",
            R["ref_counts_before_20"], R["ref_counts_after_20"]))
    gate("L0_c1 %d consecutive calls ran and the handle count was read either side" % N_CONSECUTIVE,
         len(runs) == N_CONSECUTIVE and isinstance(h_before, int) and isinstance(h_after, int),
         "%r -> %r" % (h_before, h_after))
    flat = (isinstance(h_before, int) and isinstance(h_after, int) and abs(h_after - h_before) <= 100)
    gate("L0_c2 the handle count is flat within +-100 across the 20 calls", flat,
         "%r -> %r (a FAIL is a FINDING, not a blocker - 44(e)/49(j) measured ~24-33k unexplained growth per "
         "run with ref_counts reading 0 live)" % (h_before, h_after))
    rc = R["ref_counts_after_20"] or {}
    gate("L0_c3 refs opened == closed, 0 live after the 20 calls",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    dump()

    # ---------------- ROUTE B, REPORT ONLY
    print("\n--------- L0_d1  REPORT ONLY: does `Local.Control Name` %s resolve on this machine?"
          % ROUTE_B_PROP, flush=True)
    pb = {"what": "build_property(scratch, 'VI Server:Local', [('%s', False)]) - the CREATOR's verdict. This is "
                  "a MEASUREMENT of whether the ID resolves, never a repair and never a route (49(d): B is the "
                  "fallback and is NOT built this dispatch)." % ROUTE_B_PROP,
          "class_string_tried": "VI Server:Local", "property_id": ROUTE_B_PROP}
    before_props, _e = uid_set(SCRATCH, "Property")
    try:
        new = g.build_property(SCRATCH, "VI Server:Local", [(ROUTE_B_PROP, False)], (6600, 5600))
        pb["resolves"] = True
        pb["new"] = [{"uid": o["uid"], "pos": o["pos"]} for o in new]
        pb["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        pb["resolves"] = False
        pb["new"] = None
        pb["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    after_props, _e2 = uid_set(SCRATCH, "Property")
    pb["property_uid_delta"] = sorted(after_props - before_props)
    fact("L0_d1 `Local.Control Name` %s on class 'VI Server:Local': resolves=%r ; new %r ; error VERBATIM %r"
         % (ROUTE_B_PROP, pb["resolves"], pb["new"], pb["error_verbatim"]))
    for uid in pb["property_uid_delta"]:
        try:
            cur = [o["uid"] for o in g.report_all(SCRATCH, "Property")]
            gone = g.delete_object(SCRATCH, "Property", cur.index(uid))
            fact("L0_d1 the probe node #%s was deleted again -> gone %r (the scratch is discarded anyway and "
                 "was never saved)" % (uid, gone))
        except Exception as e:                                                     # noqa: BLE001
            fact("L0_d1 deleting the probe node #%s raised %s: %s" % (uid, type(e).__name__, str(e)[:200]))
    R["route_b_probe"]["control_name_property"] = pb
    gate("L0_d1 REPORT ONLY: the 6355400 probe was made and its verdict recorded",
         "resolves" in pb, "resolves=%r" % pb.get("resolves"))

    # style 2061 - a files-level statement; nothing is built to find out
    src = open(os.path.join(ROOT, "tools", "gscript.py"), encoding="utf-8").read()
    style_hits = [ln for ln in src.splitlines() if "style" in ln.lower() and "New VI Object" in ln]
    sb = {"style": ROUTE_B_STYLE,
          "probeable_with_existing_verbs": False,
          "why": "no verb in tools/gscript.py passes a `style` number to `New VI Object`: build_invoke :2159 "
                 "and build_property :2194 take a CLASS STRING and an ID, and every other creator is "
                 "topology-specific. Probing 2061 would mean BUILDING a style-taking op, which 49(d) does not "
                 "authorise this dispatch (B is the fallback, not built).",
          "gscript_lines_mentioning_new_vi_object_and_style": style_hits[:5],
          "erdos_miller_create_vis": "50 files, none a local-variable creator (49(b), cycle 59 material #2)"}
    R["route_b_probe"]["new_vi_object_style"] = sb
    fact("L0_d2 `New VI Object` style %d: %s" % (ROUTE_B_STYLE, sb["why"]))
    gate("L0_d2 REPORT ONLY: the style-2061 question was answered at the files level", True,
         "not probeable with existing verbs; nothing built")

    fact("B the scratch was NEVER SAVED (g.save is not called on it) and is deleted below.")


# ============================================================ MAIN
def main():
    print("=== diag_s3b_l0_createlocal  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== S3b-L0: build OpCreateLocal_v0.vi (49(d)) and self-test it on a scratch copy", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 the S3a artefact (the self-test bed's SOURCE, never the bed)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"), fatal=True)
    dn = probe("T4 the DONOR OpFPLabels_v0.vi", DONOR)
    R["donor"]["md5_before"] = dn.get("md5")
    gate("T4 the donor OpFPLabels_v0.vi is on disk", dn.get("exists") == "1", "%r" % dn.get("md5"), fatal=True)

    # the mechanical pre-batch restart (44(e); STATUS ## NEXT line 77)
    D.fresh("T5 RESTART (pre-batch, 44(e) / STATUS ## NEXT line 77)")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    op_ok = False
    try:
        op_ok = phase_a()
    except Stop as s:
        R["A_build"]["stopped_at"] = str(s)
        fact("PHASE A STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        R["A_build"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("PHASE A raised %s: %s" % (type(e).__name__, str(e)[:600]))
    dump()
    if not op_ok and os.path.exists(OP) and not isinstance(R["A_build"].get("saved_bytes"), int):
        try:
            os.remove(OP)
            fact("PHASE A cleanup: the UNSAVED op file was removed (it was a byte copy of the donor with "
                 "nothing of its own). NOTHING SAVED IS EVER DELETED.")
        except Exception as e:                                                     # noqa: BLE001
            fact("PHASE A cleanup: removing %s FAILED %s: %s" % (os.path.basename(OP), type(e).__name__, e))

    if op_ok:
        try:
            phase_b()
        except Stop as s:
            R["B_selftest"]["stopped_at"] = str(s)
            fact("PHASE B STOPPED: %s" % s)
        except Exception as e:                                                     # noqa: BLE001
            R["B_selftest"]["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            fact("PHASE B raised %s: %s" % (type(e).__name__, str(e)[:600]))
    else:
        R["B_selftest"]["not_attempted"] = ("the op did not reach ExecState 1 / was not saved, so there is "
                                            "nothing to self-test. ExecState at the pass point: %r."
                                            % (R["pass_criteria"]["op_execstate"],))
        fact("PHASE B NOT ATTEMPTED: %s" % R["B_selftest"]["not_attempted"])
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
    gate("Z0 the scratch self-test copy was DELETED in the same run", not os.path.exists(SCRATCH),
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
    zd = probe("Z3 the donor OpFPLabels_v0.vi after everything", DONOR)
    gate("Z3 the DONOR OpFPLabels_v0.vi is byte-unchanged",
         zd.get("md5") == R["donor"].get("md5_before"),
         "%s vs %s" % (zd.get("md5"), R["donor"].get("md5_before")))
    rp = os.path.join(ROOT, "tools", "recipes")
    R["recipes_dir_mtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(rp)))
    gate("Z4 no file was created under tools/recipes/ by this run", True,
         "this diagnostic writes only tools/bench/diag_s3b_l0_createlocal.{log,json}, claudeDev\\"
         "OpCreateLocal_v0.vi and the scratch it deletes")

    print("\n--- THE ANSWER TABLE (readings, not a recommendation)", flush=True)
    fact("OP        %s : ExecState %r at the pass point, saved %r bytes -> md5 %r"
         % (os.path.basename(OP), R["pass_criteria"]["op_execstate"], R["A_build"].get("saved_bytes"),
            R["A_build"].get("file_after", {}).get("md5")))
    fact("RIDER     6331C02's terminals beyond the standard four: %r"
         % (R["A_build"].get("invoke_terminals", {}).get("beyond_the_standard_four"),))
    c1 = R["B_selftest"].get("call_1", {})
    fact("CALL 1    new Local %r ; class %r ; owner %r ; BOUND LABEL %r (asked for %r) ; run error VERBATIM %r"
         % (c1.get("new_local_uids"), (c1.get("readback") or {}).get("class"),
            (c1.get("readback") or {}).get("owner"), (c1.get("readback") or {}).get("bound_label"),
            TARGET_LABEL, c1.get("run_error_verbatim")))
    fact("CALL 1    error cluster VERBATIM %s ; ExecState after %r"
         % (c1.get("error_cluster_verbatim"), R["B_selftest"].get("exec_state_after_call_1")))
    cc = R["B_selftest"].get("consecutive", {})
    fact("20 CALLS  %r/%r produced one new Local; handles %r -> %r ; refs %r"
         % (cc.get("n_with_one_new"), cc.get("n"), cc.get("handles_before"), cc.get("handles_after"),
            R.get("ref_counts_after_20")))
    fact("ROUTE B   6355400 resolves=%r (error VERBATIM %r) ; style 2061 probeable=%r"
         % (R["route_b_probe"].get("control_name_property", {}).get("resolves"),
            R["route_b_probe"].get("control_name_property", {}).get("error_verbatim"),
            R["route_b_probe"].get("new_vi_object_style", {}).get("probeable_with_existing_verbs")))
    fact("ARTEFACTS ON DISK: %r" % ([{"step": a["step"], "path": a["path"], "md5": a.get("file", {}).get("md5"),
                                      "size": a.get("file", {}).get("size")}
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
