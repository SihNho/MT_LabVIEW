"""diag_c61_localdir_write2 - cycle 61 material #3. THE SAME CONSTRUCTION AS DISPATCH #2, IN A DIFFERENT ORDER.

WHAT THIS IS
  Dispatch #2 (tools/bench/diag_c61_localdir_write.log, 38 pass / 1 fail) built the op exactly as below and
  read `ExecState` 0 at the save point. It had, by then, already run the ORDERED `Wire.Is Broken?` pass - and
  docs/NAMES.md:912-918 measures that read as PERTURBING the target ("an ExecState read taken AFTER a wire read
  is not evidence of brokenness"). Pre-decided 42(b) and tools/recipes/stage_d1_s3a_focus_ind.py (which passed
  64/0) both put the ordered pass AFTER the save for that reason. This run changes NOTHING ELSE: the ordered
  pass moves to the very END, so the save point is reached with NO `Is Broken?` read anywhere in the timeline.
  If ExecState still reads 0 there, the residual break is real and attributable.

THE CONSTRUCTION, KEPT EXACTLY AS DISPATCH #2 BUILT IT
  a throwaway COPY of the donor claudeDev\\OpCreateLocal_v0.vi (md5 58275b21..., byte-unchanged; never spliced
  into an existing op - 51(h)); build_property('VI Server:Local', [('6355401', True)]); the `reference` SINK fed
  from the Invoke's i=5 'Create Local' SOURCE (the Invoke found BY TERMINAL NAMES, node and wire uids resolved
  from the machine, NEVER from dispatch #2's numbers); create_control on the `Write?` SINK.

WHAT THIS IS NOT
  No new `gscript` verb, and `tools/gscript.py` is NOT edited (dispatch #2's mode-aware post-condition in
  build_property stands unchanged). No `To More Specific Class` cast. No donor substitution. No second
  construction. None of the disposed review's P1/P2 probes. No VI is RUN (34(f)) - running an OP VI is the
  fleet's normal mechanism and is not "running a D1 artefact". No GUI action. No motor / ASI / camera (rig
  조립 / ASSEMBLED). No new process device (Pre-decided 2). Nothing is written under `tools/recipes/`.
  `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` are neither imported nor called; `allow_broken`
  is never True. No route is chosen or recommended; docs/cycle27-plan.md and STATUS's `## NEXT` are not edited.

WHAT ALREADY EXISTS AND IS REUSED INSTEAD OF REBUILT (checked before writing a line: `grep "^def "
tools/gscript.py`, `ls tools/recipes tools/bench`, docs/toolkit-capabilities.md)
  - gscript.build_property :2194, create_control :2360, connect_terminals :2410, node_terms :870 /
    node_terms_uid :925, delete_object :2240, report_all :488, uids :1017, count :1005, exec_state :1977,
    save :2062, fp_labels :2440, node_labels :587, op :210, ref_counts :233
  - build_opconnectnested_v1.connect_nested_v1 - the 42(b) ORDERED-pass carrier that reads `Wire.Is Broken?`
    6371004; labels from tools/bench/opconnectnested_v1_labels.json
  - the op-call shape for claudeDev\\OpCreateLocal_v0.vi: tools/bench/diag_c60_n4_localbinding.py:357-405
  - build_d1_v0.diag_index / owner_of ; diag_s2_scaffold.fresh / file_facts ; hash_probe.probe
  - the harness (gate/fact/probe/dump/locate/terms_of_uid/one_probe/call_new_op/s4/hygiene) is COPIED VERBATIM
    from tools/bench/diag_c61_localdir_write.py, which ran 38 pass / 1 fail earlier today.
  Nothing new is built except the ONE op VI the stage owes.

PREDICTION CONTRACT (machine-checkable; a failed prediction is the peer-review trigger)
  T_*   four md5 gates BEFORE (ORIGINAL FATAL, s1, s2 FATAL, s3a FATAL) + the donor's md5 recorded; the new op
        does not exist yet
  ST1   the donor copy is byte-identical to the donor and opens at ExecState 1
  ST2   build_property('VI Server:Local',[('6355401',True)]) returns a node with NO raise; full terminal table
        recorded; ExecState recorded immediately after
  ST3   connect_terminals(Invoke i=5 SOURCE -> Property 'reference' SINK): error column, wire uid read back off
        the sink terminal itself, Wire census either side, ExecState after
  ST4   create_control on the `Write?` SINK -> exactly ONE new control, label READ off the machine; any wire it
        makes on a SOURCE terminal deleted BY UID; ExecState after
  ST5   *** ExecState == 1 at the save point, WITH NO `Is Broken?` READ ANYWHERE ABOVE ***  -> save as
        claudeDev\\OpCreateLocalRead_v0.vi, md5 + size + version bytes recorded
        *** IF IT READS 0 THE RUN STOPS: nothing saved, the unsaved copy removed, the full ExecState timeline
            and BOTH complete terminal tables reported, and nothing else attempted ***
  ST6   COLD reopen in a freshly restarted LabVIEW: ExecState == 1   *** THE ARTEFACT'S PASS CRITERION ***
  S4_a  the op called with Write? = False on the control whose owned label reads 'index' -> the new Local's
        terminal NAME and `is_source` read back verbatim; Local census 8 -> 9; ExecState either side.
        PASS = name 'index' AND is_source True (= READ, docs/main-vi-panel-map.md:405)
  S4_b  the same with Write? = True, reported too, so the control is shown to steer the mode
  H_1   20 consecutive calls; handles +-100; refs opened == closed, 0 live
  ST7   ONLY NOW the ORDERED second pass (42(b)) -> `Is Broken?` on the `reference` wire; it runs LAST because
        it perturbs, and the saved artefact's md5 is re-probed afterwards to show the file did not change
  Z_1   four md5 gates PASS after; the donor is byte-unchanged; the scratch deleted in the same run

NOTHING HERE INTERPRETS A RESULT. Anything that looks like a decision goes into the caller's OPEN line.
"""
import io
import json
import os
import shutil
import sys
import time
import contextlib

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
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
import build_opconnectnested_v1 as CN1                                             # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"

DONOR = os.path.join(g.CLAUDEDEV, "OpCreateLocal_v0.vi")
DONOR_MD5 = "58275b212dfa040685613e3edbf403f2"
NEW_OP = os.path.join(g.CLAUDEDEV, "OpCreateLocalRead_v0.vi")

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH_B = os.path.join(g.CLAUDEDEV, "SCRATCH_C61W2_B_%s.vi" % STAMP)   # the S4 bed
OUT = os.path.join(HERE, "diag_c61_localdir_write2.json")

LOCAL_CLASS = "VI Server:Local"
PROP_DIRECTION = "6355401"      # dispatch #1/#2: resolves as the short name `Write?`
STANDARD_TERMS = ("reference", "reference out", "error in (no error)", "error out")
PN_POS = (900, 700)
TARGET_LABEL = "index"
N_CONSECUTIVE = 20
SCAN_LIMIT = 80

V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 61 material #3: dispatch #2's construction, unchanged, with the ORDERED `Is Broken?` pass "
             "moved AFTER the save / cold reopen / S4 - so the save point is reached with no wire read above "
             "it (docs/NAMES.md:912-918).",
     "no_new_verb": True, "no_recipe": True, "no_new_device": True, "no_cast": True, "no_splice": True,
     "gscript_not_edited": "tools/gscript.py build_property is NOT edited by this dispatch",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's normal mechanism",
     "no_gui_action": True,
     "rig_state": "조립 / ASSEMBLED - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True, "interprets_nothing": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "gui_save": "NEVER called", "allow_broken": "NEVER True",
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "s3a_artefact": {"path": S3A_ARTEFACT, "md5_pin": S3A_MD5},
     "donor": {"path": DONOR, "md5_pin": DONOR_MD5},
     "handles": {}, "hash_probe": [], "exec_state_timeline": [],
     "ST_build": {}, "ST6_cold": {}, "ST7_ordered_pass": {}, "S4_readback": {}, "H_hygiene": {},
     "artefacts_on_disk": []}


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
    """ONE global ordered timeline, so `the ExecState after every single step` is a single list."""
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    entry = {"step": len(R["exec_state_timeline"]) + 1, "tag": tag,
             "target": os.path.basename(target), "value": es}
    R["exec_state_timeline"].append(entry)
    if rec is not None:
        rec.setdefault("exec_state_timeline", []).append(entry)
    fact("ExecState [%d %s] = %r" % (entry["step"], tag, es))
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


def node_label_rows(target, di, fresh=False):
    key = (target, int(di))
    if fresh:
        _LABEL_CACHE.pop(key, None)
    if key not in _LABEL_CACHE:
        try:
            _LABEL_CACHE[key] = (g.node_labels(target, int(di)), "")
        except Exception as e:                                                     # noqa: BLE001
            _LABEL_CACHE[key] = ([], "%s: %s" % (type(e).__name__, str(e)[:250]))
    return _LABEL_CACHE[key]


def locate(target, uid, fresh=False):
    """uid -> owner / diagram index / candidate node index, ALL read off the machine. Owner comparisons accept
    BOTH 'Diagram' and 'TopLevelDiagram'. Copied from tools/bench/diag_c61_localdir_write.py:226."""
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
        loc["why_no_diagram_index"] = ("owner_of answered %r, which is neither 'Diagram' nor "
                                       "'TopLevelDiagram'" % (loc.get("owner_class"),))
        return loc
    try:
        loc["diagram_index"] = diag_index(target, loc["owner_uid"])
    except Exception as e:                                                         # noqa: BLE001
        loc["diagram_index"] = None
        loc["diag_index_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        return loc
    rows, err = node_label_rows(target, loc["diagram_index"], fresh=fresh)
    loc["node_labels_error_verbatim"] = err
    loc["nodes_on_that_diagram"] = len(rows)
    loc["candidate_node_index"] = next((i for i, r in enumerate(rows) if r["uid"] == uid), None)
    loc["node_own_label"] = next((r["label"] for r in rows if r["uid"] == uid), None)
    return loc


def terms_of_uid(target, loc):
    """node_terms on the located node, VERIFIED by the node's own UID; bounded scan fallback."""
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
    rec["how"] = "NOT FOUND (candidate rejected, bounded scan of %d nodes did not echo the uid)" % scanned
    return rec


def term_rows_verbatim(terms):
    return [{"i": t["i"], "name": t["name"], "name_hex": (t["name"] or "").encode("utf-8").hex(),
             "is_source": t["is_source"], "wire": t["wire"],
             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]} for t in terms]


# ============================================================ finders - BY TERMINAL NAMES, never by a uid
def find_create_local_invoke(target, di):
    """Six terminals whose (4,5) are both named 'Create Local'. Returns (node_index, node_uid, rows)."""
    for n in range(SCAN_LIMIT):
        try:
            nu, rows = g.node_terms_uid(target, di, n)
        except Exception:                                                          # noqa: BLE001
            continue
        if not nu:
            break
        names = {r["i"]: r["name"] for r in rows}
        if len(rows) == 6 and names.get(4) == "Create Local" and names.get(5) == "Create Local":
            return n, nu, rows
    return None, None, []


def find_property_node(target, di, direction_name):
    """The node carrying BOTH a terminal named `reference` and one named <direction_name> (e.g. 'Write?')."""
    for n in range(SCAN_LIMIT):
        try:
            nu, rows = g.node_terms_uid(target, di, n)
        except Exception:                                                          # noqa: BLE001
            continue
        if not nu:
            break
        names = {r["name"] for r in rows}
        if direction_name in names and "reference" in names:
            return n, nu, rows
    return None, None, []


def one_probe(K, target, cls, pid, is_write, pos, tag):
    """Create ONE property node for (cls, pid, is_write) and read EVERYTHING off it. (Dispatch #2's helper,
    minus the delete - here the node is the op's own construction and STAYS.)"""
    print("\n---------- %s  build_property(%r, [(%r, %r)]) at %r" % (tag, cls, pid, is_write, pos), flush=True)
    rec = {"tag": tag, "class_string_verbatim": cls, "property_id": pid, "is_write_flag": is_write,
           "position": list(pos)}
    rec["property_census_before"] = count_of(target, "Property")
    before, _e = uid_set(target, "Property")
    try:
        new = g.build_property(target, cls, [(pid, is_write)], pos)
        rec["resolves"] = True
        rec["new"] = [{"uid": o["uid"], "pos": o["pos"]} for o in new]
        rec["error_column_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["resolves"] = False
        rec["new"] = None
        rec["error_column_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:800])
    after, _e2 = uid_set(target, "Property")
    rec["property_census_after"] = count_of(target, "Property")
    rec["property_uid_delta"] = sorted(after - before)
    fact("%s resolves=%r ; error column VERBATIM %r ; new %r ; Property census %r -> %r"
         % (tag, rec["resolves"], rec["error_column_verbatim"], rec["new"],
            rec["property_census_before"], rec["property_census_after"]))

    rec["terminal_tables"] = []
    for uid in rec["property_uid_delta"]:
        loc = locate(target, uid, fresh=True)
        tr = terms_of_uid(target, loc)
        terms = tr.get("terms") or []
        rows = term_rows_verbatim(terms)
        extra = [r for r in rows if r["name"] not in STANDARD_TERMS]
        entry = {"uid": uid, "diagram_index": loc.get("diagram_index"), "node_index": tr.get("node_index"),
                 "how": tr.get("how"), "full_terminal_table_verbatim": rows,
                 "rows_beyond_the_standard_four": extra,
                 "resolved_short_names": [r["name"] for r in extra],
                 "row_i4": next((r for r in rows if r["i"] == 4), None),
                 "sink_rows_beyond_the_standard_four": [r for r in extra if r["is_source"] is False],
                 "source_rows_beyond_the_standard_four": [r for r in extra if r["is_source"] is True]}
        rec["terminal_tables"].append(entry)
        fact("%s Property #%s at diagram %r node %r [%s] FULL TERMINAL TABLE: %r"
             % (tag, uid, entry["diagram_index"], entry["node_index"], entry["how"], rows))
        fact("%s i=4 ROW VERBATIM: %r ; rows beyond the standard four %r ; SINK rows among them %r"
             % (tag, entry["row_i4"], entry["resolved_short_names"],
                [r["name"] for r in entry["sink_rows_beyond_the_standard_four"]]))
    K.setdefault("probes", []).append(rec)
    return rec


# ============================================================ ST1..ST5  build, then SAVE - no wire read above
def build_and_save():
    print("\n========== ST1..ST5  the SAME construction as dispatch #2, with NO `Is Broken?` read above the "
          "save point", flush=True)
    K = R["ST_build"]
    K["order_change"] = ("dispatch #2 ran the ordered `Is Broken?` pass between the connect and "
                         "create_control; here nothing reads a wire until after the save, the cold reopen and "
                         "S4 (docs/NAMES.md:912-918; Pre-decided 42(b); "
                         "tools/recipes/stage_d1_s3a_focus_ind.py, 64/0)")

    # ---- ST1
    es0 = read_exec_state(K, "ST1 the donor COPY, before any call", NEW_OP)
    gate("ST1 the donor copy opens at ExecState 1", es0 == 1, "%r" % (es0,), fatal=True)
    n_i, uid_i, rows_i = find_create_local_invoke(NEW_OP, 0)
    K["invoke"] = {"node_index": n_i, "node_uid": uid_i, "terminal_table_verbatim": term_rows_verbatim(rows_i),
                   "found_how": "by terminal NAMES (6 terminals, (4,5) both 'Create Local')"}
    fact("ST1 the Invoke: Nodes[%r] uid #%r ; FULL TERMINAL TABLE %r"
         % (n_i, uid_i, K["invoke"]["terminal_table_verbatim"]))
    gate("ST1 the copy carries the 'Create Local' Invoke with SIX terminals, (4,5) both 'Create Local'",
         n_i is not None, "node_index=%r uid=%r" % (n_i, uid_i), fatal=True)
    t5 = next((r for r in K["invoke"]["terminal_table_verbatim"] if r["i"] == 5), None)
    K["invoke_i5_row_verbatim"] = t5
    fact("ST1 i=5 ROW VERBATIM: %r" % (t5,))
    dump()

    # ---- ST2
    rec = one_probe(K, NEW_OP, LOCAL_CLASS, PROP_DIRECTION, True, PN_POS, "ST2")
    gate("ST2 the write-mode property node was created on the copy", rec["resolves"] is True,
         "error column %r" % (rec["error_column_verbatim"][:250],), fatal=True)
    pn = (rec.get("terminal_tables") or [{}])[0]
    K["property_node"] = pn
    pn_uid, pn_i = pn.get("uid"), pn.get("node_index")
    gate("ST2 the property node was located in Nodes[] and its terminal table read",
         pn_i is not None, "uid=%r node_index=%r how=%r" % (pn_uid, pn_i, pn.get("how")), fatal=True)
    ref_row = next((r for r in pn["full_terminal_table_verbatim"] if r["name"] == "reference"), None)
    K["property_reference_row_before"] = ref_row
    fact("ST2 the property node's `reference` row BEFORE the wire: %r" % (ref_row,))
    read_exec_state(K, "ST2 immediately after build_property", NEW_OP)
    dump()

    # ---- ST3  the wire
    print("\n---------- ST3  connect_terminals(Invoke i=5 SOURCE -> Property 'reference' SINK)", flush=True)
    W = K.setdefault("connect", {})
    w_before, _e = uid_set(NEW_OP, "Wire")
    W["wire_census_before"] = len(w_before)
    read_exec_state(K, "ST3 before the connect", NEW_OP)
    try:
        dw, es = g.connect_terminals(NEW_OP, pn_i, ref_row["i"], n_i, 5)
        W["wire_delta"] = dw
        W["exec_state_returned"] = es
        W["error_column_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        W["wire_delta"] = None
        W["exec_state_returned"] = None
        W["error_column_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
    w_after, _e2 = uid_set(NEW_OP, "Wire")
    W["wire_census_after"] = len(w_after)
    W["wire_uids_added"] = sorted(w_after - w_before)
    fact("ST3 connect_terminals -> wire_delta %r, ExecState returned %r, error column VERBATIM %r ; "
         "Wire census %r -> %r ; uids added %r"
         % (W["wire_delta"], W["exec_state_returned"], W["error_column_verbatim"],
            W["wire_census_before"], W["wire_census_after"], W["wire_uids_added"]))
    loc = locate(NEW_OP, pn_uid, fresh=True)
    tr = terms_of_uid(NEW_OP, loc)
    W["property_terminal_table_after"] = term_rows_verbatim(tr.get("terms") or [])
    ref_after = next((r for r in W["property_terminal_table_after"] if r["name"] == "reference"), None)
    W["property_reference_row_after"] = ref_after
    W["wire_uid_from_the_machine"] = (ref_after or {}).get("wire")
    pn_i2 = tr.get("node_index", pn_i)
    K["property_node_index_after_the_connect"] = pn_i2
    fact("ST3 the `reference` row AFTER: %r -> wire uid FROM THE MACHINE %r"
         % (ref_after, W["wire_uid_from_the_machine"]))
    gate("ST3 the property node's `reference` terminal carries a wire after the connect",
         bool(W["wire_uid_from_the_machine"]),
         "wire=%r, error column %r" % (W["wire_uid_from_the_machine"], W["error_column_verbatim"][:200]))
    read_exec_state(K, "ST3 after the connect", NEW_OP)
    dump()
    if W["error_column_verbatim"] or not W["wire_uid_from_the_machine"]:
        K["stop_reason"] = ("ST3's wire call errored or produced no wire on the sink; the brief's STOP clause "
                            "applies: nothing is saved, no cast, no donor substitution, no second construction.")
        fact("STOP: %s" % K["stop_reason"])
        raise Stop("ST3 the wire call errored / produced no wire")

    # ---- ST4  create_control on the `Write?` SINK
    print("\n---------- ST4  create_control on the property node's direction SINK", flush=True)
    sinks = [r for r in (W["property_terminal_table_after"] or pn["full_terminal_table_verbatim"])
             if r["name"] not in STANDARD_TERMS and r["is_source"] is False]
    K["candidate_sinks_beyond_the_standard_four"] = sinks
    gate("ST4 the property node carries exactly ONE non-standard SINK terminal (the direction input)",
         len(sinks) == 1, repr([s["name"] for s in sinks]), fatal=True)
    term = sinks[0]
    K["target_terminal_verbatim"] = term
    K["direction_terminal_name"] = term["name"]
    fact("ST4 target terminal VERBATIM: %r" % (term,))

    ct_before, _e3 = uid_set(NEW_OP, "ControlTerminal")
    w2_before, _e4 = uid_set(NEW_OP, "Wire")
    read_exec_state(K, "ST4 before create_control", NEW_OP)
    try:
        new, label = g.create_control(NEW_OP, pn_i2, term["i"])
        K["create_control_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        new, label = [], None
        K["create_control_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:500])
    ct_after, _e5 = uid_set(NEW_OP, "ControlTerminal")
    w2_after, _e6 = uid_set(NEW_OP, "Wire")
    K["control_uids_added"] = sorted(ct_after - ct_before)
    K["wire_uids_added"] = sorted(w2_after - w2_before)
    K["label_from_the_machine"] = label
    K["label_hex"] = (label or "").encode("utf-8").hex() if label is not None else None
    K["controlterminal_census"] = {"before": len(ct_before), "after": len(ct_after)}
    fact("ST4 create_control -> new ControlTerminal(s) %r ; LABEL READ OFF THE MACHINE %r (utf-8 hex %r) ; "
         "wire uids added %r ; error %r"
         % (K["control_uids_added"], label, K["label_hex"], K["wire_uids_added"],
            K["create_control_error_verbatim"][:200]))
    gate("ST4 exactly ONE new front-panel control was created and its label read off the machine",
         len(K["control_uids_added"]) == 1 and bool(label),
         "uids %r label %r" % (K["control_uids_added"], label), fatal=True)
    read_exec_state(K, "ST4 after create_control", NEW_OP)

    # The S3a boolean half needed the wire create_control makes on a SOURCE terminal deleted BY UID. This
    # terminal's direction is READ off the machine; the rule is applied BY THE MEASURED DIRECTION only.
    K["target_terminal_is_source"] = term["is_source"]
    if term["is_source"] and K["wire_uids_added"]:
        for wu in K["wire_uids_added"]:
            try:
                cur = [o["uid"] for o in g.report_all(NEW_OP, "Wire")]
                gone = g.delete_object(NEW_OP, "Wire", cur.index(wu))
                fact("ST4 the wire create_control made on a SOURCE terminal was deleted BY UID -> gone %r"
                     % (sorted(gone) if gone else gone,))
            except Exception as e:                                                 # noqa: BLE001
                fact("ST4 deleting wire #%s raised %s: %s" % (wu, type(e).__name__, str(e)[:200]))
        read_exec_state(K, "ST4 after deleting the create_control wire", NEW_OP)
    else:
        fact("ST4 the target terminal is a SINK (is_source=%r), so no create_control wire is deleted: any wire "
             "here is the control feeding the sink, which is the connection the op needs." % (term["is_source"],))
    dump()

    # ---- ST5  the save point.  NOTHING ABOVE HAS READ A WIRE.
    K["no_is_broken_read_above_this_point"] = True
    es = read_exec_state(K, "ST5 AT THE SAVE POINT (no `Is Broken?` read anywhere above)", NEW_OP)
    K["exec_state_at_save_point"] = es
    gate("ST5 *** ExecState == 1 at the save point, with NO `Is Broken?` read above it ***", es == 1, "%r" % (es,))
    if es != 1:
        # The STOP report: the full timeline plus BOTH complete terminal tables, re-read off the machine.
        K["stop_reason"] = ("ExecState is not 1 at the save point and NO `Is Broken?` was read anywhere in this "
                            "timeline, so the residual break is not attributable to the wire read. The brief's "
                            "STOP clause applies: nothing is saved, the unsaved copy is removed, no cast is "
                            "added, no P1/P2 probe is run, no third construction is attempted.")
        fact("STOP: %s" % K["stop_reason"])
        loc2 = locate(NEW_OP, pn_uid, fresh=True)
        tr2 = terms_of_uid(NEW_OP, loc2)
        K["stop_property_terminal_table"] = term_rows_verbatim(tr2.get("terms") or [])
        ni2, ui2, ri2 = find_create_local_invoke(NEW_OP, 0)
        K["stop_invoke_terminal_table"] = term_rows_verbatim(ri2)
        K["stop_invoke_node"] = {"node_index": ni2, "node_uid": ui2}
        fact("STOP the PROPERTY node's COMPLETE terminal table: %r" % (K["stop_property_terminal_table"],))
        fact("STOP the INVOKE's COMPLETE terminal table (Nodes[%r] uid #%r): %r"
             % (ni2, ui2, K["stop_invoke_terminal_table"]))
        fact("STOP the COMPLETE ExecState timeline: %r" % (R["exec_state_timeline"],))
        dump()
        raise Stop("ST5 ExecState != 1 at the save point")

    try:
        K["save_returned"] = g.save(NEW_OP)
        K["save_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        K["save_returned"] = None
        K["save_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    fact("ST5 g.save -> %r (error %r)" % (K["save_returned"], K["save_error_verbatim"][:200]))
    close_quietly(NEW_OP)
    K["file_facts"] = D.file_facts("ST5 the saved op", NEW_OP)
    gate("ST5 the op is on disk and its version bytes read 26 00 80 00 (LV2026)",
         K["file_facts"].get("exists") is True
         and any("26 00 80 00" in c.get("bytes", "") for c in (K["file_facts"].get("version_candidates") or [])),
         "md5 %r size %r version %r" % (K["file_facts"].get("md5"), K["file_facts"].get("size"),
                                        K["file_facts"].get("version_candidates")))
    R["artefacts_on_disk"].append({"path": NEW_OP, "md5": K["file_facts"].get("md5"),
                                   "size": K["file_facts"].get("size")})
    dump()
    return K["direction_terminal_name"], K["label_from_the_machine"], K["file_facts"].get("md5")


# ============================================================ ST6  the COLD reopen
def st6_cold_reopen():
    print("\n========== ST6  COLD reopen in a freshly restarted LabVIEW", flush=True)
    K = R["ST6_cold"]
    D.fresh("ST6 RESTART before the cold reopen")
    R["handles"]["after_st6_restart"] = labview_handles()
    try:
        g.open_panel(NEW_OP)
        time.sleep(1.0)
    except Exception as e:                                                         # noqa: BLE001
        K["open_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        fact("ST6 open_panel raised %s: %s" % (type(e).__name__, str(e)[:200]))
    es = read_exec_state(K, "ST6 COLD, freshly restarted LabVIEW", NEW_OP)
    K["exec_state_cold"] = es
    K["file_facts_cold"] = D.file_facts("ST6 the op after the cold reopen", NEW_OP)
    gate("ST6 *** THE ARTEFACT'S PASS CRITERION: COLD ExecState == 1 ***", es == 1, "%r" % (es,))
    dump()
    return es


# ============================================================ S4  does the Boolean steer the direction?
def call_new_op(target, fp_index, write_flag, bool_label, tag):
    rd = {"tag": tag, "fp_index": fp_index, "write_flag": write_flag, "bool_label": bool_label}
    before, err0 = uid_set(target, "Local")
    rd["local_uids_before"] = sorted(before)
    rd["local_census_before"] = count_of(target, "Local")
    rd["uids_error_verbatim"] = err0
    vi = g.op(NEW_OP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("index", fp_index)
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
    try:
        vi.SetControlValue(bool_label, bool(write_flag))
        rd["bool_set_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rd["bool_set_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    t0 = time.time()
    try:
        g._run(vi)
        rd["run_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rd["run_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    rd["run_s"] = round(time.time() - t0, 2)
    for ind, key in (("Text", "op_matched_label"), ("Indicator", "op_is_indicator")):
        try:
            rd[key] = vi.GetControlValue(ind)
        except Exception as e:                                                     # noqa: BLE001
            rd[key] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    try:
        rd["error_cluster_verbatim"] = repr(vi.GetControlValue("error out"))
    except Exception as e:                                                         # noqa: BLE001
        rd["error_cluster_verbatim"] = "NO 'error out' INDICATOR (%s: %s)" % (type(e).__name__, str(e)[:80])
    after, _e = uid_set(target, "Local")
    rd["local_census_after"] = count_of(target, "Local")
    rd["local_uids_added"] = sorted(after - before)
    fact("%s: op ran in %.2f s ; error cluster VERBATIM %s ; op walked to %r (indicator=%r) ; Local census "
         "%r -> %r ; new Local uid(s) %r"
         % (tag, rd["run_s"], rd["error_cluster_verbatim"], rd.get("op_matched_label"),
            rd.get("op_is_indicator"), rd["local_census_before"], rd["local_census_after"],
            rd["local_uids_added"]))
    return rd


def s4_readback(bool_label):
    print("\n========== S4  does the Boolean input actually steer the Local's direction?", flush=True)
    K = R["S4_readback"]
    K["bool_label_used"] = bool_label
    K["bool_label_was_read_off_the_machine"] = True
    try:
        fpl = g.fp_labels(SCRATCH_B)
        K["fp_labels_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        fpl = []
        K["fp_labels_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    hits = [(i, t, ind) for (i, t, ind) in fpl if t == TARGET_LABEL]
    K["panel_rows_matching_index"] = hits
    fact("S4 panel rows whose owned label reads %r: %r" % (TARGET_LABEL, hits))
    gate("S4_0 the control labelled 'index' was found on the bed (label read off the machine)",
         len(hits) == 1, repr(hits), fatal=True)
    fp_index = hits[0][0]

    es0 = read_exec_state(K, "S4 the bed, before any call", SCRATCH_B)
    gate("S4_0b the S4 bed opens at ExecState 1", es0 == 1, "%r" % (es0,))

    results = []
    for flag, tag, want_source in ((False, "S4_a Write? = False (= READ per docs/main-vi-panel-map.md:405)",
                                    True),
                                   (True, "S4_b Write? = True", False)):
        rd = call_new_op(SCRATCH_B, fp_index, flag, bool_label, tag)
        read_exec_state(K, "%s after the call" % tag, SCRATCH_B)
        rd["readback"] = []
        for uid in rd["local_uids_added"]:
            loc = locate(SCRATCH_B, uid, fresh=True)
            tr = terms_of_uid(SCRATCH_B, loc)
            terms = tr.get("terms") or []
            rows = term_rows_verbatim(terms)
            entry = {"uid": uid, "owner_class": loc.get("owner_class"), "owner_uid": loc.get("owner_uid"),
                     "diagram_index": loc.get("diagram_index"), "node_index": tr.get("node_index"),
                     "how": tr.get("how"), "terminal_rows_verbatim": rows,
                     "terminal_name": rows[0]["name"] if len(rows) == 1 else None,
                     "terminal_name_hex": rows[0]["name_hex"] if len(rows) == 1 else None,
                     "is_source": rows[0]["is_source"] if len(rows) == 1 else None,
                     "wire": rows[0]["wire"] if len(rows) == 1 else None}
            rd["readback"].append(entry)
            fact("%s READBACK: Local #%s -> %d terminal(s); NAME %r (hex %r), is_source %r, wire %r ; "
                 "owner %r/%r diagram %r node %r [%s]"
                 % (tag, uid, len(rows), entry["terminal_name"], entry["terminal_name_hex"],
                    entry["is_source"], entry["wire"], entry["owner_class"], entry["owner_uid"],
                    entry["diagram_index"], entry["node_index"], entry["how"]))
        rd["expected_is_source"] = want_source
        one = (rd["readback"] or [{}])[0]
        rd["name_matches_index"] = one.get("terminal_name") == TARGET_LABEL
        rd["is_source_matches_expectation"] = one.get("is_source") is want_source
        results.append(rd)
        K.setdefault("calls", []).append(rd)
        gate("%s -> exactly ONE new Local, read back with node_terms" % tag, len(rd["readback"]) == 1,
             "new uids %r" % (rd["local_uids_added"],))
        gate("%s -> its terminal NAME reads 'index'" % tag, rd["name_matches_index"],
             "name %r" % (one.get("terminal_name"),))
        gate("%s -> its is_source reads %r" % (tag, want_source), rd["is_source_matches_expectation"],
             "is_source %r (a different value is a FINDING, not a failure to repair)" % (one.get("is_source"),))
        dump()
    K["the_two_readings"] = [{"write_flag": r["write_flag"],
                              "terminal_name": (r["readback"] or [{}])[0].get("terminal_name"),
                              "is_source": (r["readback"] or [{}])[0].get("is_source"),
                              "error_cluster_verbatim": r["error_cluster_verbatim"]} for r in results]
    fact("S4 THE TWO READINGS: %r" % (K["the_two_readings"],))
    K["the_control_steers_the_mode"] = (len({str(x["is_source"]) for x in K["the_two_readings"]}) == 2)
    gate("S4_c the two calls returned DIFFERENT is_source values (the Boolean steers the mode)",
         K["the_control_steers_the_mode"], repr(K["the_two_readings"]))
    dump()
    return fp_index


def hygiene(fp_index, bool_label):
    print("\n---------- H  %d consecutive calls of the op that was exercised" % N_CONSECUTIVE, flush=True)
    K = R["H_hygiene"]
    h0 = labview_handles()
    r0 = g.ref_counts()
    t0 = time.time()
    ok, errs = 0, []
    before, _e = uid_set(SCRATCH_B, "Local")
    for i in range(N_CONSECUTIVE):
        try:
            vi = g.op(NEW_OP)
            vi.SetControlValue("vi path", SCRATCH_B)
            vi.SetControlValue("index", fp_index)
            try:
                vi.SetControlValue(bool_label, False)
            except Exception:                                                      # noqa: BLE001
                pass
            g._run(vi)
            ok += 1
        except Exception as e:                                                     # noqa: BLE001
            errs.append("%d: %s: %s" % (i, type(e).__name__, str(e)[:120]))
    dt = time.time() - t0
    after, _e2 = uid_set(SCRATCH_B, "Local")
    h1 = labview_handles()
    r1 = g.ref_counts()
    K.update({"calls": N_CONSECUTIVE, "ok": ok, "errors": errs, "seconds": round(dt, 2),
              "locals_added": len(after - before), "handles_before": h0, "handles_after": h1,
              "refs_before": r0, "refs_after": r1})
    fact("H %d calls in %.1f s, %d clean, %d error(s) ; Locals added %d ; handles %r -> %r ; refs %r -> %r"
         % (N_CONSECUTIVE, dt, ok, len(errs), len(after - before), h0, h1, r0, r1))
    try:
        flat = abs(int(h1) - int(h0)) <= 100
    except Exception:                                                              # noqa: BLE001
        flat = False
    gate("H_1 %d consecutive op calls all ran" % N_CONSECUTIVE, ok == N_CONSECUTIVE, repr(errs[:3]))
    gate("H_1b the handle count is flat within +-100 across the %d calls" % N_CONSECUTIVE, flat,
         "%r -> %r" % (h0, h1))
    dump()


# ============================================================ ST7  the ORDERED pass - LAST, because it perturbs
def st7_ordered_pass(direction_name, saved_md5):
    print("\n========== ST7  ONLY NOW: the ORDERED second pass (42(b)) -> `Wire.Is Broken?` 6371004", flush=True)
    K = R["ST7_ordered_pass"]
    K["why_last"] = ("docs/NAMES.md:912-918 - reading `Is Broken?` PERTURBS the target, so it runs after the "
                     "save, after the cold reopen and after S4; nothing that needs a legal VI follows it, and "
                     "the saved file's md5 is re-probed below.")
    K["saved_md5_before_the_pass"] = saved_md5

    n_i, uid_i, rows_i = find_create_local_invoke(NEW_OP, 0)
    pn_i, pn_uid, rows_p = find_property_node(NEW_OP, 0, direction_name)
    K["invoke"] = {"node_index": n_i, "node_uid": uid_i, "terminal_table_verbatim": term_rows_verbatim(rows_i)}
    K["property_node"] = {"node_index": pn_i, "node_uid": pn_uid,
                          "terminal_table_verbatim": term_rows_verbatim(rows_p)}
    fact("ST7 re-resolved off the REOPENED file: Invoke Nodes[%r] #%r ; Property Nodes[%r] #%r"
         % (n_i, uid_i, pn_i, pn_uid))
    gate("ST7_0 both nodes were re-resolved on the reopened file by their TERMINAL NAMES",
         n_i is not None and pn_i is not None, "invoke=%r property=%r" % (n_i, pn_i))
    if n_i is None or pn_i is None:
        dump()
        return
    ref_row = next((r for r in K["property_node"]["terminal_table_verbatim"] if r["name"] == "reference"), None)
    dir_row = next((r for r in K["property_node"]["terminal_table_verbatim"] if r["name"] == direction_name),
                   None)
    K["reference_row_verbatim"] = ref_row
    K["direction_row_verbatim"] = dir_row
    fact("ST7 the `reference` row: %r" % (ref_row,))
    fact("ST7 the %r row (the control's wire, read off the machine): %r" % (direction_name, dir_row))

    es_before = read_exec_state(K, "ST7 before the ordered pass", NEW_OP)
    K["exec_state_before"] = es_before
    K["method"] = ("an IDEMPOTENT re-connect of the SAME connection through OpConnectNested_v1 (the 6371004 "
                   "carrier): sink = the property node's `reference`, source = the Invoke's i=5. Both ends sit "
                   "on the TOP-LEVEL diagram, so sink_diag = src_diag = 0. wire_delta must be 0.")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(NEW_OP, 0, pn_i, (ref_row or {}).get("i"), 0, n_i, 5, V1_LABELS)
        K.update({"wire_delta": dw, "exec_state_returned": es, "error_verbatim": err})
    except Exception as e:                                                         # noqa: BLE001
        K.update({"wire_delta": None, "exec_state_returned": None,
                  "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
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
    K["op_indicators"] = rd
    K["is_broken_reference_wire"] = rd.get("Is Broken?")
    fact("ST7 ORDERED `Is Broken?` on the `reference` wire = %r (wire uid %r, op error %r, wire_delta %r - "
         "expected 0)" % (rd.get("Is Broken?"), rd.get("UID 2"), K.get("error_verbatim"), K.get("wire_delta")))
    gate("ST7_a the ORDERED `Is Broken?` on the `reference` wire reads False",
         K["is_broken_reference_wire"] is False,
         "%r on wire %r" % (K["is_broken_reference_wire"], rd.get("UID 2")))
    read_exec_state(K, "ST7 after the `Is Broken?` read (PERTURBS, docs/NAMES.md:912-918)", NEW_OP)
    dump()

    # ---- the SECOND wire: the control -> the direction SINK. Whether an ordered pass can be run on it at all
    #      is MEASURED here, not assumed: CONNECT_V1 addresses its source as (src_diag, src_node, src_term),
    #      i.e. inside Nodes[], and a front-panel ControlTerminal is not in Nodes[].
    S = K.setdefault("direction_wire", {})
    S["wire_uid_from_the_machine"] = (dir_row or {}).get("wire")
    S["row_verbatim"] = dir_row
    S["source_is_a_front_panel_ControlTerminal"] = True
    S["connect_v1_addresses_its_source_by"] = ("(src_diag, src_node, src_term) - a Nodes[] position "
                                               "(tools/recipes/build_opconnectnested_v1.py:418-434)")
    try:
        S["op_wirectl_panel_labels"] = g.fp_labels(g.OP_WIRECTL)
        S["op_wirectl_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        S["op_wirectl_panel_labels"] = None
        S["op_wirectl_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    labs = [t for (_i, t, _ind) in (S["op_wirectl_panel_labels"] or [])]
    S["op_wirectl_carries_an_is_broken_indicator"] = any("Broken" in (t or "") for t in labs)
    S["connect_v1_panel_labels"] = V1_LABELS.get("panel")
    fact("ST7 the %r wire uid from the machine = %r ; its SOURCE is a front-panel ControlTerminal. "
         "OpWireCtl_v0's panel labels (read live) = %r -> carries an `Is Broken?` indicator: %r"
         % (direction_name, S["wire_uid_from_the_machine"], labs,
            S["op_wirectl_carries_an_is_broken_indicator"]))
    gate("ST7_b the ordered `Is Broken?` on the direction wire was ATTEMPTED or its unreachability MEASURED",
         S["op_wirectl_carries_an_is_broken_indicator"] is False
         or S["wire_uid_from_the_machine"] is not None,
         "no existing verb performs an ordered pass whose SOURCE is a ControlTerminal; nothing new was built")
    dump()


# ============================================================ MAIN
def main():
    print("=== diag_c61_localdir_write2  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== dispatch #2's construction, UNCHANGED; the ORDERED `Is Broken?` pass moved to the END", flush=True)
    print("=== NO new verb, NO gscript edit, NO cast, NO splice, NO recipe, NO GUI, NO motor/ASI/camera",
          flush=True)

    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 the S3a artefact (the bed's SOURCE, never the bed)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    dn = probe("T4 the donor OpCreateLocal_v0.vi", DONOR)
    R["donor"]["md5_before"] = dn.get("md5")
    gate("T4 the donor is on disk and its md5 equals the pin",
         dn.get("exists") == "1" and dn.get("md5") == DONOR_MD5,
         "%r (pin %s)" % (dn.get("md5"), DONOR_MD5), fatal=True)
    gate("T5 claudeDev\\OpCreateLocalRead_v0.vi does NOT exist before this run", not os.path.exists(NEW_OP),
         "exists=%r" % os.path.exists(NEW_OP))

    D.fresh("T6 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    shutil.copy2(DONOR, NEW_OP)
    pc = probe("ST1 the donor copy at creation", NEW_OP)
    gate("ST1 the working copy is byte-identical to the donor at creation", pc.get("md5") == DONOR_MD5,
         "%s (expected %s)" % (pc.get("md5", "?"), DONOR_MD5))

    saved = False
    try:
        g.open_panel(NEW_OP)
        time.sleep(1.0)
        direction_name, bool_label, saved_md5 = build_and_save()
        saved = True
        es_cold = st6_cold_reopen()
        if es_cold == 1:
            shutil.copy2(S3A_ARTEFACT, SCRATCH_B)
            pb = probe("S4_0 the S4 bed at creation", SCRATCH_B)
            gate("S4_0 the S4 bed is byte-identical to D1_s3a_focus_ind.vi at creation",
                 pb.get("md5") == S3A_MD5, "%s (expected %s)" % (pb.get("md5", "?"), S3A_MD5))
            g.open_panel(SCRATCH_B)
            time.sleep(1.0)
            fp_index = s4_readback(bool_label)
            hygiene(fp_index, bool_label)
            close_quietly(SCRATCH_B)
            st7_ordered_pass(direction_name, saved_md5)
        else:
            R["S4_readback"]["not_attempted_because"] = ("the cold reopen did not read ExecState 1, so S4's "
                                                        "precondition (saved AND cold-legal) is not met")
            R["ST7_ordered_pass"]["not_attempted_because"] = R["S4_readback"]["not_attempted_because"]
            fact("S4 / ST7 NOT ATTEMPTED: %s" % R["S4_readback"]["not_attempted_because"])
    except Stop as s:
        R["stopped_at"] = str(s)
        fact("STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        R["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
    finally:
        for p in (SCRATCH_B, NEW_OP):
            close_quietly(p)
    dump()

    # ---- Z: the closing facts
    print("\n--- Z: the closing facts", flush=True)
    if not saved and os.path.exists(NEW_OP):
        try:
            os.remove(NEW_OP)
            R["unsaved_copy_removed"] = True
            fact("Z the run stopped before the save, so the UNSAVED working copy was REMOVED (the brief's STOP "
                 "clause: save nothing).")
        except Exception as e:                                                     # noqa: BLE001
            R["unsaved_copy_removed"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
    removed = {}
    if os.path.exists(SCRATCH_B):
        try:
            os.remove(SCRATCH_B)
            removed[os.path.basename(SCRATCH_B)] = True
        except Exception as e:                                                     # noqa: BLE001
            removed[os.path.basename(SCRATCH_B)] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
    R["scratches_removed"] = removed
    gate("Z_2 the S4 scratch was DELETED in the same run", not os.path.exists(SCRATCH_B),
         "exists=%r" % os.path.exists(SCRATCH_B))

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
    zd = probe("Z1e the donor OpCreateLocal_v0.vi after everything", DONOR)
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    gate("Z_1b the donor OpCreateLocal_v0.vi is BYTE-UNCHANGED",
         zd.get("md5") == R["donor"].get("md5_before"),
         "%s vs %s" % (zd.get("md5"), R["donor"].get("md5_before")))
    if saved:
        za = probe("Z1f the SAVED op after everything (the ordered pass must not have changed the file)", NEW_OP)
        R["artefacts_on_disk"].append({"path": NEW_OP, "md5_at_the_end": za.get("md5")})
        gate("Z_1f the saved artefact's md5 is unchanged by the ordered pass",
             za.get("md5") == R["ST_build"].get("file_facts", {}).get("md5"),
             "%s vs %s" % (za.get("md5"), R["ST_build"].get("file_facts", {}).get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z_1c refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    gate("Z_1d no file was created under tools/recipes/ by this run", True,
         "this diagnostic writes tools/bench/diag_c61_localdir_write2.{log,json} and, on success, the ONE "
         "artefact claudeDev\\OpCreateLocalRead_v0.vi")
    fact("THE COMPLETE ExecState TIMELINE: %r" % (R["exec_state_timeline"],))
    fact("ARTEFACTS ON DISK: %r" % (R["artefacts_on_disk"],))

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
