"""diag_c62_branch2 - cycle 62 material #1, the ONE gap diag_c62_branch left. PURE MEASUREMENT.

WHY THIS EXISTS (it is NOT a full-length retry of diag_c62_branch - 48(o))
  diag_c62_branch answered M-A, M-B and M-C and ran M-D's two deletes (27 pass / 1 fail,
  tools/bench/diag_c62_branch.log). Its ONE failing gate, A_4, was an ADDRESSING defect in the script, and
  it cost exactly one reading: the PANEL INDICATOR's connected-wire state AFTER each delete.
  MEASURED IN v1, not assumed: `ControlTerminal` #23541 / #23576 exist and are owned by `Diagram #639`
  (`owner_of` echoed the class), but NEITHER is a member of that diagram's `Nodes[]` - node_labels
  enumerated all 73 nodes and none echoes those uids (diag_c62_branch.log:81,:85,:100,:104) - so
  `node_terms`, which addresses through `Diagram.Nodes[]`, cannot reach them. v1's fallback then matched
  `panel_wiring` rows by the label `node_labels` reports, which is `None` for a non-Node, so it matched
  nothing and both AFTER readings came back empty (diag_c62_branch.log:134-135).

WHAT CHANGES - ONE THING
  The panel row is identified by its own CONTROL UID, captured BEFORE the delete as "the row whose
  connected wire is the wire about to be deleted", and looked up again AFTER by that same control uid.
  The FULL panel_wiring row list is stored before and after, so the reading is auditable rather than
  filtered. Nothing else is different: same beds, same deletes, same order, no `Is Broken?` anywhere.
  ⚠️ The link `ControlTerminal uid` <-> `Control uid` is NOT measured and is not claimed: this fleet has
  no verb for it (`ControlTerminal.Control` 6353000 is UNVERIFIED - docs/d1-build-plan.md:866,:909).
  What IS measured is the panel terminal that carries the wire, by the control uid panel_wiring reports.

WHAT THIS IS NOT
  Nothing is built, nothing is saved (`save` never called), no op, no new `gscript` verb, no edit to
  tools/gscript.py, no recipe, no VI run (34(f)), no GUI action, no motor / ASI / camera (rig 조립), no new
  process device. `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` neither imported nor
  called; `allow_broken` never True. No `Wire.Is Broken?` read anywhere (docs/NAMES.md:912-918).
  Both beds are SCRATCH duplicates of claudeDev\\D1_s3a_focus_ind.vi, deleted in the same run (49(e)).
  NO ROUTE IS CHOSEN OR RECOMMENDED; docs/cycle27-plan.md and STATUS's `## NEXT` are not edited.

WHAT IS REUSED INSTEAD OF REBUILT
  gscript.node_terms_uid / node_labels / panel_wiring / report_all / count / exec_state / delete_object /
  open_panel / close_panel / ref_counts; build_d1_v0.owner_of + diag_index; diag_s2_scaffold.fresh;
  hash_probe.probe; bench_prep.labview_handles. The harness is diag_c62_branch's, trimmed to M-D.

PREDICTION CONTRACT
  T_*   four md5 gates BEFORE (ORIGINAL FATAL, s1, s2 FATAL, s3a FATAL)
  E_a   scratch A: ExecState 1 cold; `#10407` t0 carries a non-zero wire; EXACTLY ONE panel_wiring row
        carries that same wire uid BEFORE the delete
  E_b   the delete removes exactly that uid; ExecState after is recorded; `#10407` t0, the far end
        `#10686` t0 'x .and. y?' and THAT PANEL ROW (by its control uid) are all re-read AFTER
  F_a/F_b  the same on an independent scratch B for `#10407` t2, far end `#10757` t1 'element'
  Z_*   four md5 gates PASS after; both scratches exists=False; refs/handles reported
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

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_c62_branch2.json")

CASE_UID = 10407
CT_NUM = 23541
CT_BOOL = 23576
SCAN_LIMIT = 120

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 62 material #1, the one gap diag_c62_branch left: the PANEL INDICATOR's connected-wire "
             "state AFTER each delete, the row identified by its own control uid. PURE MEASUREMENT.",
     "not_a_full_length_retry": "diag_c62_branch answered M-A/M-B/M-C and ran both deletes; only one reading "
                                "was missed, and only that reading is retaken",
     "control_terminal_uid_to_control_uid_link": "NOT MEASURED and NOT CLAIMED - no verb in this fleet "
                                                 "(`ControlTerminal.Control` 6353000 UNVERIFIED, "
                                                 "docs/d1-build-plan.md:866,:909)",
     "no_new_verb": True, "no_recipe": True, "no_new_device": True, "nothing_saved": True,
     "gscript_not_edited": True, "is_broken_read_anywhere": False,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's normal mechanism",
     "no_gui_action": True,
     "rig_state": "조립 / ASSEMBLED - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True, "interprets_nothing": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "gui_save": "NEVER called", "allow_broken": "NEVER True",
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "legs": {}}


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


def close_quietly(target):
    try:
        g.close_panel(target)
    except Exception as e:                                                         # noqa: BLE001
        fact("close_panel(%s) raised %s: %s" % (os.path.basename(target), type(e).__name__, e))


def term_rows_verbatim(terms):
    return [{"i": t["i"], "name": t["name"], "name_hex": (t["name"] or "").encode("utf-8").hex(),
             "is_source": t["is_source"], "wire": t["wire"],
             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]} for t in terms]


def node_table(target, uid, tag):
    """locate a NODE by uid and read its full terminal table, verified by the node's own uid echo."""
    loc = {"uid": uid}
    for strict in (True, False):
        try:
            cls, ouid = owner_of(target, uid, strict=strict)
            loc.update({"owner_class": cls, "owner_uid": ouid, "owner_error_verbatim": ""})
            break
        except Exception as e:                                                     # noqa: BLE001
            loc.update({"owner_class": None, "owner_uid": None,
                        "owner_error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:250])})
    if loc.get("owner_class") not in ("Diagram", "TopLevelDiagram"):
        loc["diagram_index"] = None
        fact("%s #%s: owner %r - not a diagram owner, no terminal table" % (tag, uid, loc.get("owner_class")))
        return [], loc
    try:
        loc["diagram_index"] = diag_index(target, loc["owner_uid"])
    except Exception as e:                                                         # noqa: BLE001
        loc["diagram_index"] = None
        loc["diag_index_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        return [], loc
    try:
        rows_l = g.node_labels(target, int(loc["diagram_index"]))
    except Exception as e:                                                         # noqa: BLE001
        rows_l = []
        loc["node_labels_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    loc["nodes_on_that_diagram"] = len(rows_l)
    n = next((i for i, r in enumerate(rows_l) if r["uid"] == uid), None)
    loc["nodes_index"] = n
    loc["node_own_label"] = next((r["label"] for r in rows_l if r["uid"] == uid), None)
    rows = []
    if n is not None:
        try:
            node_uid, trows = g.node_terms_uid(target, int(loc["diagram_index"]), n)
            loc["node_uid_echo"] = node_uid
            if node_uid == uid:
                rows = term_rows_verbatim(trows)
                loc["how"] = "node_labels position (verified by the node's own UID)"
            else:
                loc["how"] = "REJECTED: Nodes[%d] echoed uid %r, not %r" % (n, node_uid, uid)
        except Exception as e:                                                     # noqa: BLE001
            loc["how"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:250])
    else:
        loc["how"] = ("NOT IN Diagram.Nodes[] (node_labels lists %d nodes, none echoes this uid)"
                      % len(rows_l))
    fact("%s #%s: owner %r#%r diagram %r Nodes[%r] [%s] label %r ; TABLE %r"
         % (tag, uid, loc.get("owner_class"), loc.get("owner_uid"), loc.get("diagram_index"),
            loc.get("nodes_index"), loc.get("how"), loc.get("node_own_label"), rows))
    return rows, loc


def panel_all(target, tag):
    try:
        rows = g.panel_wiring(target)
        err = ""
    except Exception as e:                                                         # noqa: BLE001
        rows, err = [], "%s: %s" % (type(e).__name__, str(e)[:250])
    fact("%s panel_wiring: %d rows%s" % (tag, len(rows), (" ; ERROR " + err) if err else ""))
    return rows, err


# ============================================================ one leg
def leg(bed, which_terminal, far_uid, far_term, tag):
    print("\n========== %s: delete the Wire on #%d t%d on %s"
          % (tag, CASE_UID, which_terminal, os.path.basename(bed)), flush=True)
    K = R["legs"].setdefault(tag, {})
    K["bed"] = os.path.basename(bed)
    K["terminal"] = "#%d t%d" % (CASE_UID, which_terminal)

    shutil.copy2(S3A_ARTEFACT, bed)
    pb = probe("%s the bed at creation" % tag, bed)
    K["bed_md5_at_creation"] = pb.get("md5")
    gate("%s_0 the bed is byte-identical to D1_s3a_focus_ind.vi at creation" % tag,
         pb.get("md5") == S3A_MD5, "%s (expected %s)" % (pb.get("md5", "?"), S3A_MD5), fatal=True)
    g.open_panel(bed)
    time.sleep(1.0)

    es_before = read_exec_state(K, "%s cold open, before the delete" % tag, bed)
    K["exec_state_before"] = es_before
    K["wire_census_before"] = count_of(bed, "Wire")
    K["control_terminal_census_before"] = count_of(bed, "ControlTerminal")
    gate("%s_a the bed opens COLD at ExecState 1" % tag, es_before == 1, "%r" % (es_before,))

    case_before, case_loc = node_table(bed, CASE_UID, "%s BEFORE #%d" % (tag, CASE_UID))
    K["case_table_before"] = case_before
    row = next((r for r in case_before if r["i"] == which_terminal), None)
    K["target_terminal_row_before"] = row
    W = (row or {}).get("wire")
    K["wire_uid_read_off_the_machine"] = W
    gate("%s_b the target wire uid was read off the machine" % tag, bool(W),
         "wire %r on %s" % (W, K["terminal"]), fatal=True)

    far_before, _fl = node_table(bed, far_uid, "%s BEFORE far end #%d" % (tag, far_uid))
    K["far_end_table_before"] = far_before
    K["far_end_row_before"] = next((r for r in far_before if r["i"] == far_term), None)

    fp_before, perr = panel_all(bed, "%s BEFORE" % tag)
    K["panel_wiring_error_verbatim"] = perr
    K["panel_rows_before_count"] = len(fp_before)
    K["panel_rows_before_all"] = fp_before
    carriers = [r for r in fp_before if r["wire"] == W]
    K["panel_rows_carrying_the_target_wire_BEFORE"] = carriers
    fact("%s the panel row(s) carrying wire %r BEFORE, VERBATIM: %r" % (tag, W, carriers))
    gate("%s_c EXACTLY ONE panel_wiring row carries the target wire before the delete" % tag,
         len(carriers) == 1, "%d row(s): %r" % (len(carriers), [r["label"] for r in carriers]))
    carrier_uid = carriers[0]["uid"] if carriers else None
    K["carrier_control_uid"] = carrier_uid
    K["carrier_label_read_off_the_machine"] = carriers[0]["label"] if carriers else None
    K["carrier_label_hex"] = (carriers[0]["label"] if carriers else "").encode("utf-8").hex()

    # the two ControlTerminal uids STATUS records, re-checked for EXISTENCE only (they are not addressable
    # through Diagram.Nodes[] - measured in diag_c62_branch.log:81,:85,:100,:104)
    try:
        cts = g.report_all(bed, "ControlTerminal")
    except Exception as e:                                                         # noqa: BLE001
        cts = []
        K["control_terminal_census_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    K["control_terminal_rows_of_interest_BEFORE"] = [o for o in cts if o["uid"] in (CT_NUM, CT_BOOL)]
    fact("%s ControlTerminal census rows for #%d / #%d BEFORE: %r"
         % (tag, CT_NUM, CT_BOOL, K["control_terminal_rows_of_interest_BEFORE"]))

    # ---- the delete
    try:
        wires = g.report_all(bed, "Wire")
        idx = [o["i"] for o in wires if o["uid"] == W]
        K["wire_traverse_matches"] = idx
    except Exception as e:                                                         # noqa: BLE001
        K["wire_traverse_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        idx = []
    gate("%s_d exactly ONE Traverse 'Wire' entry carries uid %r" % (tag, W), len(idx) == 1,
         "matches %r" % (idx,), fatal=True)
    try:
        gone = g.delete_object(bed, "Wire", idx[0])
        K["delete_error_verbatim"] = ""
        K["uids_gone"] = sorted(gone) if gone else gone
    except Exception as e:                                                         # noqa: BLE001
        K["delete_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        K["uids_gone"] = None
    fact("%s delete_object(Wire[%r] = uid %r): gone %r ; error %r"
         % (tag, idx[0], W, K["uids_gone"], K["delete_error_verbatim"]))
    gate("%s_e the delete removed EXACTLY the wire uid targeted" % tag, K["uids_gone"] == [W],
         "gone %r, targeted %r" % (K["uids_gone"], W))

    # ---- after
    es_after = read_exec_state(K, "%s AFTER the delete" % tag, bed)
    K["exec_state_after"] = es_after
    K["wire_census_after"] = count_of(bed, "Wire")
    K["control_terminal_census_after"] = count_of(bed, "ControlTerminal")

    case_after, _cl = node_table(bed, CASE_UID, "%s AFTER #%d" % (tag, CASE_UID))
    K["case_table_after"] = case_after
    K["target_terminal_row_after"] = next((r for r in case_after if r["i"] == which_terminal), None)
    far_after, _fl2 = node_table(bed, far_uid, "%s AFTER far end #%d" % (tag, far_uid))
    K["far_end_table_after"] = far_after
    K["far_end_row_after"] = next((r for r in far_after if r["i"] == far_term), None)

    fp_after, _pe2 = panel_all(bed, "%s AFTER" % tag)
    K["panel_rows_after_count"] = len(fp_after)
    K["panel_rows_after_all"] = fp_after
    carrier_after = next((r for r in fp_after if r["uid"] == carrier_uid), None)
    K["carrier_row_AFTER_by_control_uid"] = carrier_after
    fact("%s the SAME panel row (control uid %r, label %r) AFTER, VERBATIM: %r"
         % (tag, carrier_uid, K["carrier_label_read_off_the_machine"], carrier_after))
    gate("%s_f the carrier panel row was found again AFTER, by its own control uid" % tag,
         carrier_after is not None, "control uid %r" % (carrier_uid,))
    try:
        cts2 = g.report_all(bed, "ControlTerminal")
    except Exception:                                                              # noqa: BLE001
        cts2 = []
    K["control_terminal_rows_of_interest_AFTER"] = [o for o in cts2 if o["uid"] in (CT_NUM, CT_BOOL)]

    table = [
        {"what": "#%d t%d (the deleted wire's sink)" % (CASE_UID, which_terminal),
         "before": (K["target_terminal_row_before"] or {}).get("wire"),
         "after": (K["target_terminal_row_after"] or {}).get("wire")},
        {"what": "far end #%d t%d %r" % (far_uid, far_term, (K["far_end_row_before"] or {}).get("name")),
         "before": (K["far_end_row_before"] or {}).get("wire"),
         "after": (K["far_end_row_after"] or {}).get("wire")},
        {"what": "panel indicator %r (control uid %r)"
                 % (K["carrier_label_read_off_the_machine"], carrier_uid),
         "before": (carriers[0]["wire"] if carriers else None),
         "after": (carrier_after or {}).get("wire")},
        {"what": "ExecState", "before": es_before, "after": es_after},
        {"what": "Wire census", "before": K["wire_census_before"], "after": K["wire_census_after"]},
        {"what": "ControlTerminal census", "before": K["control_terminal_census_before"],
         "after": K["control_terminal_census_after"]},
        {"what": "panel_wiring row count", "before": K["panel_rows_before_count"],
         "after": K["panel_rows_after_count"]},
    ]
    for r in table:
        r["went_bare"] = (bool(r["before"]) and not r["after"]) if r["what"].startswith(("#", "far", "panel i")) \
            else None
    K["before_after_table"] = table
    for r in table:
        fact("%s TABLE  %-54s  %r -> %r%s" % (tag, r["what"], r["before"], r["after"],
                                              ("   WENT BARE" if r["went_bare"] else "")))
    K["terminals_that_went_bare"] = [r["what"] for r in table if r["went_bare"]]
    gate("%s_g the before->after table is complete (7 rows)" % tag, len(table) == 7,
         "went bare: %r" % (K["terminals_that_went_bare"],))
    close_quietly(bed)
    dump()


# ============================================================ MAIN
def main():
    print("=== diag_c62_branch2  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== the ONE reading diag_c62_branch missed: the panel indicator's wire AFTER each delete", flush=True)
    print("=== PURE MEASUREMENT: nothing built, nothing saved, no route chosen, no `Is Broken?` read",
          flush=True)

    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 the S3a artefact (the beds' SOURCE, never a bed)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)

    D.fresh("T4 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    bed_a = os.path.join(g.CLAUDEDEV, "SCRATCH_C62B_A_%s.vi" % STAMP)
    bed_b = os.path.join(g.CLAUDEDEV, "SCRATCH_C62B_B_%s.vi" % STAMP)
    try:
        leg(bed_a, 0, 10686, 0, "E")     # far end: 'x .and. y?'
        leg(bed_b, 2, 10757, 1, "F")     # far end: 'element'
    except Stop as s:
        R["stopped_at"] = str(s)
        fact("STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        R["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
    finally:
        for p in (bed_a, bed_b):
            close_quietly(p)
    dump()

    print("\n--- Z: the closing facts", flush=True)
    removed = {}
    for p in (bed_a, bed_b):
        if os.path.exists(p):
            try:
                os.remove(p)
                removed[os.path.basename(p)] = True
            except Exception as e:                                                 # noqa: BLE001
                removed[os.path.basename(p)] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
    R["scratches_removed"] = removed
    gate("Z_2 BOTH scratches were DELETED in the same run",
         not os.path.exists(bed_a) and not os.path.exists(bed_b),
         "A exists=%r, B exists=%r" % (os.path.exists(bed_a), os.path.exists(bed_b)))

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
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z_1c refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    gate("Z_1e no `Wire.Is Broken?` was read at any point", R["is_broken_read_anywhere"] is False,
         "docs/NAMES.md:912-918 - the read perturbs ExecState")
    fact("THE COMPLETE ExecState TIMELINE: %r" % (R["exec_state_timeline"],))

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
