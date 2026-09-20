"""diag_c60_n4_localbinding - cycle 60 (attempt 2) material #4. A **READ**, not a build.

WHAT THIS IS AND WHY IT IS SHORT
  The prior-art review `archive/peer/2026-09-21-priorart-c60-localname-decomposition.md` (verdict `NOT novel`,
  7 findings) established that the instrument cycle 60 was building ALREADY EXISTS:
      gscript.node_terms(target, diagram_index, node_index)   tools/gscript.py:870
      gscript.node_terms_uid(...)                             tools/gscript.py:925
  A local-variable node's SINGLE terminal is NAMED after the control it is bound to, and `is_source` gives the
  direction (TRUE = the local is READ, FALSE = WRITTEN) - `docs/main-vi-panel-map.md:405`, table at :409-416,
  `docs/NAMES.md:335`. All eight of the main VI's Locals are already tabulated there and in
  `tools/bench/main_vi_nodeterms.json`.
  So `OpLocalName_v0`, the `To More Specific Class` cast and Pre-decided 51's L1/L2/L3 are WITHDRAWN by the
  judgement session and NONE of them is built here. The ONE genuinely unmeasured fact is 51(d)'s question:
      **what is a NEWLY created Local bound to?**
  L0 made 21 Locals with `claudeDev\\OpCreateLocal_v0.vi` and never called `node_terms` on one.

PRIOR-ART / EXISTING-CAPABILITY CHECK DONE BEFORE WRITING THIS FILE (CLAUDE.md sec.3 "before creating any new op,
tool or recipe, check what already exists"):
  * `grep "^def " tools/gscript.py` - the readers used here ALL pre-exist: op :210, ref_counts :233, reset :262,
    report_all :488, node_labels :587, node_terms :870, node_terms_uid :925, count :1005, uids :1017,
    open_panel :1241, close_panel :1257, ensure_loaded :1268, exec_state :1977, fp_labels :2440, _run :341.
    NO new verb is added, NO fleet file is patched, NO op VI is built or saved.
  * `tools/recipes/build_d1_v0.py` - owner_of :338, diag_index :357 (imported unchanged; `move_in` is NOT
    imported and NOT called).
  * `tools/bench/diag_s3b_l0_createlocal.py:488-545` - the `create_local()` wrapper for the EXISTING op
    `claudeDev\\OpCreateLocal_v0.vi` (md5 58275b21...), copied here verbatim in shape. The op is READ-ONLY input:
    its md5 is pinned before and after.
  * `tools/bench/sweep_nodeterms_main.py` - the 2026-09-14 sweep that produced the reference table. It walked
    every diagram; this run resolves ONE diagram per Local instead (owner_of -> diag_index -> node_labels).
  * `tools/bench/c60c_astcheck.py` - the existing static gate, re-aimed by argv (no new gate file).

THE MEASUREMENT (on a SCRATCH duplicate of claudeDev\\D1_s3a_focus_ind.vi, md5 eef91c1d..., 49(e): never the
artefact itself; deleted in the same run)
  N1  Call `node_terms` on EVERY pre-existing `Local`. Report every uid -> terminal name + is_source + wire
      VERBATIM, and say plainly whether the set matches `docs/main-vi-panel-map.md:409-416` (measured on the MAIN
      VI; this scratch is the same lineage, so a MISMATCH is itself a finding worth reporting, never a failure).
  N2  Create ONE Local from the front-panel object whose owned label reads 'index' - the label is MATCHED against
      the machine's own bytes (fp_labels) and the op's `Text` indicator reports which label it walked to - then
      call `node_terms` on the new Local. Report the terminal name VERBATIM, is_source, wire, the new uid and
      owner, `Local` census 8 -> 9, and the scratch's ExecState before and after the create.
  N3  The same for 'Automatic Error Handling' (the second control S3b needs); census 9 -> 10.
  N4  Hygiene: 20 consecutive `node_terms` calls - handles flat +-100, refs opened == closed, 0 live. Then the
      scratch is deleted and `exists=False` is proved.

PREDICTION CONTRACT (machine-checkable; a FAIL here is a FACT about the READ, not a construction to retry)
  N0_a  four md5 pins hold BEFORE: ORIGINAL 2a78e17c (FATAL), D1_s1_copy 3e3d23ce, D1_s2_loops 6ff19497 (FATAL),
        D1_s3a_focus_ind eef91c1d (FATAL); OpCreateLocal_v0 is on disk and its md5 is recorded
  N0_b  the scratch is byte-identical to D1_s3a_focus_ind.vi at creation and opens at ExecState 1
  N1_a  the `Local` census is READ (docs/toolkit-capabilities.md:284 records 8 - the READING is the gate)
  N1_b  every pre-existing Local resolved to a (diagram index, node index) whose node_terms echo its own uid
  N1_c  every pre-existing Local returned EXACTLY ONE terminal, and its name is non-empty
  N1_d  REPORT: does the (uid -> name, direction) set match docs/main-vi-panel-map.md:409-416? (a mismatch is
        REPORTED, never repaired and never explained away)
  N2_a  'index' is on the scratch's front panel and its Panel.Controls[] position resolved
  N2_b  the create call returned and its error column / dialog text was captured VERBATIM
  N2_c  exactly ONE new Local appeared and the census went 8 -> 9
  N2_d  node_terms on the NEW Local echoed its uid and returned its terminal row VERBATIM   *** THE QUESTION ***
  N3_a-d the same four for 'Automatic Error Handling', census 9 -> 10
  N4_a  20 consecutive node_terms calls ran and the handle count was read either side
  N4_b  the handle count is flat within +-100
  N4_c  refs opened == closed, 0 live
  Z0    the scratch was DELETED in the same run (exists=False)
  Z1    the four md5 pins hold AFTER; Z3 OpCreateLocal_v0.vi is byte-unchanged
  Z4    nothing was written under tools/recipes/

WHAT THIS RUN DOES NOT DO
  No VI is built, edited-and-saved, cast, given a property node, or SAVED - `g.save` is never called and
  `gui_save` / `remove_bad_wires` / `remove_bad_wires_scripted` are neither imported nor called; `allow_broken`
  is never True. No VI is RUN (34(f)). No GUI action. No motor / ASI / camera (rig 조립). No new process device,
  no new gscript verb, no file under tools/recipes/. `retrospective.py` / `audit_cycle.py` / `violations.py` /
  `doc_ingest.py` / `prior_art_review.py` are NOT run (OPEN 54(a)). Owner comparisons accept BOTH 'Diagram' and
  'TopLevelDiagram'; every diagram index is resolved BY UID via `diag_index`, never hard-coded. NO ROUTE IS
  CHOSEN OR RECOMMENDED and no plan document or STATUS `## NEXT` line is edited - that is judgement's call.

  py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c60_n4_localbinding.log \
     -- py -u tools/bench/diag_c60_n4_localbinding.py
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

OP_CREATE_LOCAL = os.path.join(g.CLAUDEDEV, "OpCreateLocal_v0.vi")
OP_CREATE_LOCAL_MD5 = "58275b212dfa040685613e3edbf403f2"

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C60N4_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_c60_n4_localbinding.json")

LABEL_N2 = "index"                          # the numeric leg's S3a indicator (cycle 59 read it off the machine)
LABEL_N3 = "Automatic Error Handling"       # the boolean leg's S3a indicator
N_CONSECUTIVE = 20
SCAN_LIMIT = 80                             # bounded fallback scan for a node index, never an unbounded walk

# docs/main-vi-panel-map.md:409-416, measured 2026-09-14 on the MAIN VI by the OpNodeTerms_v0 sweep. Quoted here
# ONLY to be compared against what this run reads off the machine. `read` True = the local is READ (is_source).
PANEL_MAP_TABLE = [
    {"uid": 2991,  "diagram": 1,   "owner": "FlatSequenceFrame", "control": "Total Lost Frames", "read": False},
    {"uid": 4277,  "diagram": 17,  "owner": "FlatSequenceFrame", "control": "File # Saved",      "read": False},
    {"uid": 11574, "diagram": 73,  "owner": "CaseStructure",     "control": "Focus Pos (Track)", "read": False},
    {"uid": 3160,  "diagram": 83,  "owner": "FlatSequenceFrame", "control": "Rot pos (deg)",     "read": True},
    {"uid": 3097,  "diagram": 83,  "owner": "FlatSequenceFrame", "control": "Trans Pos (mm)",    "read": True},
    {"uid": 2143,  "diagram": 83,  "owner": "FlatSequenceFrame", "control": "Total Lost Frames", "read": False},
    {"uid": 16942, "diagram": 99,  "owner": "WhileLoop",         "control": "Picture",           "read": False},
    {"uid": 25805, "diagram": 167, "owner": "FlatSequenceFrame", "control": "Color table",       "read": True},
]

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 60 material #4, a READ: what is a NEWLY created Local bound to? (Pre-decided 51(d)) - "
             "answered with the EXISTING instrument gscript.node_terms (tools/gscript.py:870), which the "
             "prior-art review archive/peer/2026-09-21-priorart-c60-localname-decomposition.md (NOT novel, 7 "
             "findings) showed already reads a Local's bound control off its single terminal's NAME.",
     "withdrawn_by_judgement_and_not_built_here": ["OpLocalName_v0.vi", "the To More Specific Class cast to "
                                                   "Local", "Pre-decided 51's L1/L2/L3"],
     "builds_nothing": True, "saves_no_vi": True, "creates_no_op": True, "no_cast": True,
     "no_property_node": True, "no_new_verb": True, "no_recipe": True, "no_new_device": True,
     "no_vi_was_run": True, "no_gui_action": True,
     "rig_state": "조립 / ASSEMBLED (motors + ASI only through tools/motor_gate.py, which is not called; camera "
                  "not needed and not touched)",
     "chooses_no_route": True, "recommends_no_route": True, "interprets_nothing": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "gui_save": "NEVER called", "allow_broken": "NEVER True",
     "citations": {"instrument": "tools/gscript.py:870 (node_terms) / :925 (node_terms_uid)",
                   "naming_rule": "docs/main-vi-panel-map.md:405 ('a local-variable node's single terminal is "
                                  "NAMED after its control'; is_source TRUE = READ)",
                   "reference_table": "docs/main-vi-panel-map.md:409-416",
                   "local_census_8": "docs/toolkit-capabilities.md:284",
                   "creator_op": "claudeDev\\OpCreateLocal_v0.vi (built cycle 60 attempt 1, md5 %s) - READ-ONLY "
                                 "input here" % OP_CREATE_LOCAL_MD5,
                   "creator_wrapper_shape": "tools/bench/diag_s3b_l0_createlocal.py:488-545",
                   "owner_of_diag_index": "tools/recipes/build_d1_v0.py:338,:357",
                   "scratch_deleted_same_run": "CLAUDE.md rule 4; Pre-decided 49(e)",
                   "diagnostic_not_recipe": "Pre-decided 48(n)",
                   "restart": "Pre-decided 44(e)"},
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "s3a_artefact": {"path": S3A_ARTEFACT, "md5_pin": S3A_MD5},
     "creator_op": {"path": OP_CREATE_LOCAL, "md5_pin": OP_CREATE_LOCAL_MD5},
     "handles": {}, "hash_probe": [],
     "N1_preexisting_locals": {}, "N2_new_local_index": {}, "N3_new_local_aeh": {}, "N4_hygiene": {},
     "panel_map_reference_table": PANEL_MAP_TABLE,
     "the_question": {"asked": "what is a NEWLY created Local bound to, as node_terms reads it?",
                      "answer_index": None, "answer_aeh": None}}


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


def close_quietly(target):
    try:
        g.close_panel(target)
    except Exception as e:                                                         # noqa: BLE001
        fact("close_panel(%s) raised %s: %s" % (os.path.basename(target), type(e).__name__, e))


_LABEL_CACHE = {}


def node_label_rows(target, di):
    """node_labels for ONE diagram, cached. Rows come back in Nodes[] order, so a uid's position in this list is
    a CANDIDATE node index - candidate, because the correspondence is an assumption, and node_terms echoes the
    node's own UID, which is what actually verifies it below."""
    key = (target, int(di))
    if key not in _LABEL_CACHE:
        try:
            _LABEL_CACHE[key] = (g.node_labels(target, int(di)), "")
        except Exception as e:                                                     # noqa: BLE001
            _LABEL_CACHE[key] = ([], "%s: %s" % (type(e).__name__, str(e)[:250]))
    return _LABEL_CACHE[key]


def locate(target, uid):
    """uid -> {owner_class, owner_uid, diagram_index, node_index, how} for a node, all read off the machine.
    Owner comparisons accept BOTH 'Diagram' and 'TopLevelDiagram'."""
    loc = {"uid": uid}
    for strict in (True, False):
        try:
            cls, ouid = owner_of(target, uid, strict=strict)
            loc.update({"owner_strict": strict, "owner_class": cls, "owner_uid": ouid,
                        "owner_error_verbatim": ""})
            break
        except Exception as e:                                                     # noqa: BLE001
            loc.update({"owner_strict": strict, "owner_class": None, "owner_uid": None,
                        "owner_error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:250])})
    if loc.get("owner_class") not in ("Diagram", "TopLevelDiagram"):
        loc["diagram_index"] = None
        loc["why_no_diagram_index"] = ("owner_of answered %r, which is neither 'Diagram' nor 'TopLevelDiagram'"
                                       % (loc.get("owner_class"),))
        return loc
    try:
        loc["diagram_index"] = diag_index(target, loc["owner_uid"])
    except Exception as e:                                                         # noqa: BLE001
        loc["diagram_index"] = None
        loc["diag_index_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        return loc
    rows, err = node_label_rows(target, loc["diagram_index"])
    loc["node_labels_error_verbatim"] = err
    loc["nodes_on_that_diagram"] = len(rows)
    cand = next((i for i, r in enumerate(rows) if r["uid"] == uid), None)
    loc["candidate_node_index"] = cand
    loc["node_own_label"] = next((r["label"] for r in rows if r["uid"] == uid), None)
    return loc


def terms_of_uid(target, loc):
    """node_terms on the located node, VERIFIED by the node's own UID. Falls back to a BOUNDED scan when the
    candidate index does not echo the uid; reports which path was used."""
    rec = {"diagram_index": loc.get("diagram_index"), "candidate_node_index": loc.get("candidate_node_index")}
    di, uid = loc.get("diagram_index"), loc.get("uid")
    if di is None:
        rec["how"] = "not located"
        return rec
    tries = []
    if loc.get("candidate_node_index") is not None:
        tries.append(int(loc["candidate_node_index"]))
    for n in tries:
        try:
            node_uid, rows = g.node_terms_uid(target, di, n)
        except Exception as e:                                                     # noqa: BLE001
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
            continue
        if node_uid == uid:
            rec.update({"how": "node_labels position (verified by the node's own UID)", "node_index": n,
                        "node_uid": node_uid, "terms": rows})
            return rec
        rec.setdefault("rejected", []).append({"n": n, "node_uid_echoed": node_uid})
    scanned = 0
    for n in range(SCAN_LIMIT):
        if n in tries:
            continue
        scanned += 1
        try:
            node_uid, rows = g.node_terms_uid(target, di, n)
        except Exception as e:                                                     # noqa: BLE001
            rec.setdefault("scan_errors", []).append({"n": n, "error_verbatim": str(e)[:160]})
            continue
        if not node_uid:
            break
        if node_uid == uid:
            rec.update({"how": "bounded scan (%d calls)" % scanned, "node_index": n, "node_uid": node_uid,
                        "terms": rows})
            return rec
    rec["how"] = "NOT FOUND (candidate rejected and a bounded scan of %d nodes did not echo the uid)" % scanned
    return rec


def read_local(target, uid, tag):
    """The whole reading for ONE Local: where it is, and what node_terms says its terminal is called."""
    rd = {"tag": tag, "uid": uid}
    rd["locate"] = locate(target, uid)
    rd["node_terms"] = terms_of_uid(target, rd["locate"])
    terms = rd["node_terms"].get("terms") or []
    rd["n_terminals"] = len(terms)
    rd["terminal_rows_verbatim"] = [{"i": t["i"], "name": t["name"],
                                     "name_hex": (t["name"] or "").encode("utf-8").hex(),
                                     "is_source": t["is_source"], "wire": t["wire"],
                                     "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]}
                                    for t in terms]
    rd["bound_control_name"] = terms[0]["name"] if len(terms) == 1 else None
    rd["is_source"] = terms[0]["is_source"] if len(terms) == 1 else None
    rd["wire"] = terms[0]["wire"] if len(terms) == 1 else None
    fact("%s Local #%s: diagram %r (owner %r) node %r [%s] -> %d terminal(s); terminal 0 name %r (hex %s), "
         "is_source %r, wire %r"
         % (tag, uid, rd["locate"].get("diagram_index"),
            (rd["locate"].get("owner_class"), rd["locate"].get("owner_uid")),
            rd["node_terms"].get("node_index"), rd["node_terms"].get("how"), rd["n_terminals"],
            rd.get("bound_control_name"), ((rd.get("bound_control_name") or "").encode("utf-8").hex()),
            rd.get("is_source"), rd.get("wire")))
    return rd


def create_local(target, label, fp_map, tag=""):
    """tools/bench/diag_s3b_l0_createlocal.py:488-545 in shape: drive the EXISTING claudeDev\\OpCreateLocal_v0.vi
    by the control's Panel.Controls[] position (resolved from the machine's own label bytes by fp_labels, exactly
    as gscript.conpane_assign:2782-2788 does). The op's `Text` indicator reports which label it WALKED TO."""
    rd = {"tag": tag, "label_asked_for": label, "label_hex": label.encode("utf-8").hex()}
    if label not in fp_map:
        rd["error_verbatim"] = ("the label %r is not a front-panel object of %s"
                                % (label, os.path.basename(target)))
        return rd
    rd["panel_index"] = fp_map[label]
    g.ensure_loaded(target)
    before, err0 = uid_set(target, "Local")
    rd["local_uids_before"] = len(before)
    rd["local_uid_read_error"] = err0

    vi = g.op(OP_CREATE_LOCAL)
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
        rd["error_cluster_verbatim"] = ("NO 'error out' INDICATOR ON THE OP (%s: %s)"
                                        % (type(e).__name__, str(e)[:80]))
    after, err1 = uid_set(target, "Local")
    rd["local_uids_after"] = len(after)
    rd["local_uid_read_error_after"] = err1
    rd["new_local_uids"] = sorted(after - before)
    rd["lost_local_uids"] = sorted(before - after)
    fact("%s create_local(%r) ran %.2f s; the op WALKED TO %r (indicator=%r); run error VERBATIM %r; error "
         "cluster VERBATIM %s; Local uids %r -> %r; NEW %r"
         % (tag, label, rd.get("run_s", -1), rd.get("op_matched_label"), rd.get("op_is_indicator"),
            rd.get("run_error_verbatim"), rd.get("error_cluster_verbatim"), rd.get("local_uids_before"),
            rd.get("local_uids_after"), rd.get("new_local_uids")))
    return rd


# ============================================================ N1
def n1(K):
    print("\n--------- N1  node_terms on EVERY pre-existing Local (validate the instrument LIVE)", flush=True)
    census = count_of(SCRATCH, "Local")
    K["local_census_before"] = census
    gate("N1_a the `Local` census was READ (docs/toolkit-capabilities.md:284 records 8 - the READING is the "
         "gate, never the 8)", isinstance(census, int), "%r" % (census,))
    try:
        rows = g.report_all(SCRATCH, "Local")
        K["report_all_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rows = []
        K["report_all_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    K["report_all_rows"] = rows
    fact("N1 report_all('Local') returned %d rows: %r"
         % (len(rows), [(o["uid"], o["owner"], o["pos"]) for o in rows]))

    readings = []
    for o in rows:
        readings.append(read_local(SCRATCH, o["uid"], "N1"))
        dump()
    K["readings"] = readings
    located = [r for r in readings if r["node_terms"].get("node_uid") == r["uid"]]
    gate("N1_b every pre-existing Local resolved to a (diagram, node) whose node_terms echoed its own uid",
         len(located) == len(readings) and bool(readings),
         "%d of %d; unlocated %r" % (len(located), len(readings),
                                     [r["uid"] for r in readings if r not in located]))
    one_named = [r for r in readings if r["n_terminals"] == 1 and (r.get("bound_control_name") or "") != ""]
    gate("N1_c every pre-existing Local returned EXACTLY ONE terminal with a non-empty name",
         len(one_named) == len(readings) and bool(readings),
         "%d of %d; exceptions %r" % (len(one_named), len(readings),
                                      [(r["uid"], r["n_terminals"], r.get("bound_control_name"))
                                       for r in readings if r not in one_named]))

    # ---- the comparison against the doc's table (REPORT; a mismatch is a finding, never a repair)
    mine = {r["uid"]: (r.get("bound_control_name"), r.get("is_source")) for r in readings}
    theirs = {t["uid"]: (t["control"], t["read"]) for t in PANEL_MAP_TABLE}
    same = sorted(u for u in mine if u in theirs and mine[u] == theirs[u])
    differ = sorted([{"uid": u, "machine": mine[u], "doc": theirs[u]} for u in mine if u in theirs
                     and mine[u] != theirs[u]], key=lambda d: d["uid"])
    only_machine = sorted(u for u in mine if u not in theirs)
    only_doc = sorted(u for u in theirs if u not in mine)
    K["comparison_with_panel_map"] = {"agree_uids": same, "differ": differ,
                                      "uids_only_on_the_machine": only_machine,
                                      "uids_only_in_the_doc": only_doc,
                                      "verdict": ("IDENTICAL SET" if not differ and not only_machine
                                                  and not only_doc else "NOT IDENTICAL - reported, not repaired")}
    fact("N1_d vs docs/main-vi-panel-map.md:409-416 -> %s | agree on %d uid(s) %r | differ %r | only on the "
         "machine %r | only in the doc %r"
         % (K["comparison_with_panel_map"]["verdict"], len(same), same, differ, only_machine, only_doc))
    gate("N1_d REPORT: the machine's (uid -> name, direction) set was compared with "
         "docs/main-vi-panel-map.md:409-416 and the verdict recorded", "verdict" in K["comparison_with_panel_map"],
         K["comparison_with_panel_map"]["verdict"])
    dump()
    return readings


# ============================================================ N2 / N3
def create_and_read(K, label, fp_map, expect_census_before, tag, gate_prefix):
    print("\n--------- %s  create ONE Local from %r, then node_terms on it" % (gate_prefix, label), flush=True)
    es_before = read_exec_state(K, "%s before the create" % gate_prefix, SCRATCH)
    K["exec_state_before"] = es_before
    K["local_census_before"] = count_of(SCRATCH, "Local")
    gate("%s_a %r is on the scratch's front panel and its Panel.Controls[] position resolved" % (gate_prefix,
                                                                                                 label),
         label in fp_map, "position %r" % (fp_map.get(label),))
    if label not in fp_map:
        K["not_attempted"] = "the label is not on the front panel"
        return None
    rd = create_local(SCRATCH, label, fp_map, tag=tag)
    K["create"] = rd
    gate("%s_b the create call returned and its error column / dialog text was captured VERBATIM" % gate_prefix,
         "run_error_verbatim" in rd, "%r" % (rd.get("run_error_verbatim"),))
    K["local_census_after"] = count_of(SCRATCH, "Local")
    new = rd.get("new_local_uids") or []
    gate("%s_c exactly ONE new Local appeared and the census moved %r -> %r"
         % (gate_prefix, expect_census_before, expect_census_before + 1 if
            isinstance(expect_census_before, int) else "?"),
         len(new) == 1 and K["local_census_after"] == (K["local_census_before"] + 1
                                                       if isinstance(K["local_census_before"], int) else None),
         "new %r; census %r -> %r" % (new, K["local_census_before"], K["local_census_after"]))
    K["exec_state_after"] = read_exec_state(K, "%s after the create" % gate_prefix, SCRATCH)
    if len(new) != 1:
        K["the_answer"] = None
        gate("%s_d node_terms on the NEW Local  *** THE QUESTION ***" % gate_prefix, False,
             "no single new Local to read")
        dump()
        return None
    rd2 = read_local(SCRATCH, new[0], "%s NEW" % gate_prefix)
    K["readback"] = rd2
    ok = (rd2["node_terms"].get("node_uid") == new[0]) and rd2["n_terminals"] >= 1
    K["the_answer"] = {"new_local_uid": new[0],
                       "owner": (rd2["locate"].get("owner_class"), rd2["locate"].get("owner_uid")),
                       "diagram_index": rd2["locate"].get("diagram_index"),
                       "node_index": rd2["node_terms"].get("node_index"),
                       "n_terminals": rd2["n_terminals"],
                       "terminal_name_verbatim": rd2.get("bound_control_name"),
                       "terminal_name_hex": (rd2.get("bound_control_name") or "").encode("utf-8").hex(),
                       "is_source": rd2.get("is_source"), "wire": rd2.get("wire"),
                       "node_own_label": rd2["locate"].get("node_own_label"),
                       "label_asked_for": label,
                       "matches_the_label_asked_for": rd2.get("bound_control_name") == label}
    gate("%s_d node_terms on the NEW Local echoed its uid and returned its terminal row  *** THE QUESTION ***"
         % gate_prefix, ok, "terminal name %r vs label asked for %r (a difference is a FACT, not a failure); "
         "is_source %r; wire %r" % (rd2.get("bound_control_name"), label, rd2.get("is_source"),
                                    rd2.get("wire")))
    dump()
    return rd2


# ============================================================ N4
def n4(K, readings):
    print("\n--------- N4  %d consecutive node_terms calls (handles +-100, refs 0 live)" % N_CONSECUTIVE,
          flush=True)
    target_reading = next((r for r in readings if r["node_terms"].get("node_index") is not None), None)
    if target_reading is None:
        K["not_attempted"] = "no located Local to call node_terms on"
        gate("N4_a %d consecutive node_terms calls ran" % N_CONSECUTIVE, False, K["not_attempted"])
        return
    di = target_reading["node_terms"]["diagram_index"]
    ni = target_reading["node_terms"]["node_index"]
    uid = target_reading["uid"]
    K["on"] = {"uid": uid, "diagram_index": di, "node_index": ni}
    R["ref_counts_before_20"] = g.ref_counts()
    h_before = labview_handles()
    R["handles"]["before_20"] = h_before
    t0 = time.time()
    runs = []
    for n in range(N_CONSECUTIVE):
        try:
            node_uid, rows = g.node_terms_uid(SCRATCH, di, ni)
            runs.append({"n": n + 1, "node_uid": node_uid, "n_terms": len(rows),
                         "name0": rows[0]["name"] if rows else None, "error_verbatim": ""})
        except Exception as e:                                                     # noqa: BLE001
            runs.append({"n": n + 1, "node_uid": None, "n_terms": None, "name0": None,
                         "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:200])})
        print("     call %2d: node_uid %r, terms %r, name0 %r"
              % (n + 1, runs[-1]["node_uid"], runs[-1]["n_terms"], runs[-1]["name0"]), flush=True)
    h_after = labview_handles()
    R["handles"]["after_20"] = h_after
    R["ref_counts_after_20"] = g.ref_counts()
    K.update({"n": N_CONSECUTIVE, "runs": runs, "elapsed_s": round(time.time() - t0, 1),
              "handles_before": h_before, "handles_after": h_after,
              "n_echoing_the_uid": sum(1 for r in runs if r["node_uid"] == uid),
              "n_with_an_error": sum(1 for r in runs if r["error_verbatim"])})
    fact("N4 %d calls in %.1f s on Local #%s (diagram %r, node %r): %d echoed the uid, %d carried an error; "
         "handles %r -> %r; refs before %r after %r"
         % (N_CONSECUTIVE, K["elapsed_s"], uid, di, ni, K["n_echoing_the_uid"], K["n_with_an_error"],
            h_before, h_after, R["ref_counts_before_20"], R["ref_counts_after_20"]))
    gate("N4_a %d consecutive node_terms calls ran and the handle count was read either side" % N_CONSECUTIVE,
         len(runs) == N_CONSECUTIVE and isinstance(h_before, int) and isinstance(h_after, int),
         "%r -> %r" % (h_before, h_after))
    flat = (isinstance(h_before, int) and isinstance(h_after, int) and abs(h_after - h_before) <= 100)
    gate("N4_b the handle count is flat within +-100 across the %d calls" % N_CONSECUTIVE, flat,
         "%r -> %r (a FAIL is a FINDING, not a blocker - 44(e)/49(j))" % (h_before, h_after))
    rc = R["ref_counts_after_20"] or {}
    gate("N4_c refs opened == closed, 0 live after the %d calls" % N_CONSECUTIVE,
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    dump()


# ============================================================ THE BODY
def body():
    read_exec_state(R["N1_preexisting_locals"], "the scratch, before any call", SCRATCH)
    es0 = R["N1_preexisting_locals"]["exec_state_timeline"][-1]["value"]
    gate("N0_b1 the scratch opens at ExecState 1", es0 == 1, "%r" % (es0,))

    readings = n1(R["N1_preexisting_locals"])

    t0 = time.time()
    try:
        rows = g.fp_labels(SCRATCH, max_n=200)
    except Exception as e:                                                         # noqa: BLE001
        rows = []
        fact("fp_labels raised %s: %s" % (type(e).__name__, str(e)[:200]))
    fp_map = {}
    for i, lab, _ind in rows:
        fp_map.setdefault(lab, i)
    R["fp_sweep"] = {"n": len(rows), "seconds": round(time.time() - t0, 1),
                     "rows_for_the_two_labels": [(i, lab, ind) for i, lab, ind in rows
                                                 if lab in (LABEL_N2, LABEL_N3)]}
    fact("fp_labels swept %d panel objects in %.1f s; the rows for the two labels this run needs, VERBATIM off "
         "the machine: %r" % (len(rows), R["fp_sweep"]["seconds"], R["fp_sweep"]["rows_for_the_two_labels"]))

    c_before = count_of(SCRATCH, "Local")
    create_and_read(R["N2_new_local_index"], LABEL_N2, fp_map, c_before, "N2", "N2")
    R["the_question"]["answer_index"] = R["N2_new_local_index"].get("the_answer")

    c_mid = count_of(SCRATCH, "Local")
    create_and_read(R["N3_new_local_aeh"], LABEL_N3, fp_map, c_mid, "N3", "N3")
    R["the_question"]["answer_aeh"] = R["N3_new_local_aeh"].get("the_answer")

    n4(R["N4_hygiene"], readings or [])
    fact("the scratch was NEVER SAVED (g.save is not called on it) and is deleted below.")


# ============================================================ MAIN
def main():
    print("=== diag_c60_n4_localbinding  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== a READ: what is a NEWLY created Local bound to? (node_terms, tools/gscript.py:870)", flush=True)
    print("=== NOTHING IS BUILT, NOTHING IS SAVED, NO VI IS RUN", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 the S3a artefact (the bed's SOURCE, never the bed)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"), fatal=True)
    cl = probe("T4 the creator op OpCreateLocal_v0.vi", OP_CREATE_LOCAL)
    R["creator_op"]["md5_before"] = cl.get("md5")
    gate("T4 OpCreateLocal_v0.vi is on disk and its md5 equals the pin",
         cl.get("exists") == "1" and cl.get("md5") == OP_CREATE_LOCAL_MD5,
         "%r (pin %s)" % (cl.get("md5"), OP_CREATE_LOCAL_MD5), fatal=True)

    D.fresh("T5 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    shutil.copy2(S3A_ARTEFACT, SCRATCH)
    p = probe("N0_b the scratch at creation", SCRATCH)
    R["scratch"] = {"path": SCRATCH, "at_creation": p}
    gate("N0_b the scratch copy is byte-identical to D1_s3a_focus_ind.vi at creation",
         p.get("md5") == S3A_MD5, "%s (expected %s)" % (p.get("md5", "?"), S3A_MD5))

    try:
        g.open_panel(SCRATCH)
        time.sleep(1.0)
        body()
    except Stop as s:
        R["stopped_at"] = str(s)
        fact("STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        R["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
    finally:
        close_quietly(SCRATCH)
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
    gate("Z0 the scratch was DELETED in the same run", not os.path.exists(SCRATCH),
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
    zc = probe("Z3 OpCreateLocal_v0.vi after everything", OP_CREATE_LOCAL)
    gate("Z3 the creator op OpCreateLocal_v0.vi is byte-unchanged",
         zc.get("md5") == R["creator_op"].get("md5_before"),
         "%s vs %s" % (zc.get("md5"), R["creator_op"].get("md5_before")))
    gate("Z4 no file was created under tools/recipes/ by this run", True,
         "this diagnostic writes only tools/bench/diag_c60_n4_localbinding.{log,json} and the scratch it deletes")

    print("\n--- THE ANSWER TABLE (readings, not a recommendation)", flush=True)
    for r in (R["N1_preexisting_locals"].get("readings") or []):
        fact("N1 PRE-EXISTING Local #%s -> terminal %r, is_source %r, wire %r"
             % (r["uid"], r.get("bound_control_name"), r.get("is_source"), r.get("wire")))
    fact("N1 vs the doc's table: %s"
         % (R["N1_preexisting_locals"].get("comparison_with_panel_map", {}).get("verdict"),))
    for key, lab in (("answer_index", LABEL_N2), ("answer_aeh", LABEL_N3)):
        a = R["the_question"].get(key)
        fact("NEW Local from %r -> %r" % (lab, a))
    fact("ARTEFACTS ON DISK: [] (this run builds and saves nothing; the scratch is deleted)")

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
