"""diag_c62_s3b_rows - cycle 62 material #2. S3b's two rows, delete-and-rebuild (Pre-decided 53(d)).

THE ROUTE IS NOT MINE TO CHOOSE. It is `docs/cycle27-plan.md` Pre-decided 53(d), verbatim:
  delete the whole Wire object -> `create_indicator` on the now-bare SOURCE terminal (a NEW indicator)
  -> `OpCreateLocalRead_v0.vi` in READ mode bound to that new indicator, its label read off the machine
  -> connect the Local's SOURCE into the freed `#10407` sink.
53(e): the OLD S3a indicators (controls 23555 / 23525, ControlTerminals 23576 / 23541) are LEFT IN PLACE,
bare and unwired. They are not deleted and not renamed.

WHAT WAS CHECKED BEFORE ANY LINE WAS WRITTEN (no new op, no new verb, no recipe)
  docs/toolkit-capabilities.md:25 (`connect_ctl`), :71 (`OpCreateLocalRead_v0`, md5 f695d97a...,
  Write?=False => READ); `grep "^def " tools/gscript.py` -> 165 defs, of which this file uses only
  report_all / node_labels / node_terms_uid / panel_wiring / fp_labels / count / exec_state / open_panel /
  close_panel / delete_object / create_indicator / connect_ctl / wire_indicators / save / op / _run /
  ref_counts / reset; ls tools/bench + tools/recipes -> the harness is diag_c62_branch2.py's, extended.
  NOTHING NEW IS BUILT.

⚠️ ONE ADDRESSING FACT MEASURED IN CYCLE 62 AND RE-CHECKED HERE, BECAUSE THE ROUTE DEPENDS ON IT
  `create_indicator(target, node_index, terminal_index)` (tools/gscript.py:2423) drives
  OpCreateIndicator_v0, whose ladder is VI -> Block Diagram -> Nodes[] -> Terminals[]: `node_index` is an
  index into the TOP-LEVEL block diagram's Nodes[], not into a nested diagram (the S3a recipe used it that
  way, tools/recipes/stage_d1_s3a_focus_ind.py:943-977, on a carrier placed at the top-level head).
  Both sources this stage must create indicators on - `#10686` and `#10757` - were measured to live on
  `Diagram #639` (diagram index 46), NOT at top level (tools/bench/diag_c62_branch2.log:27,:61).
  So B1/B2 RESOLVE the source's top-level Nodes[] index by uid off the machine and, if there is none, the
  stage STOPS THERE with nothing saved and the copy removed - it does not call the verb with a nested index
  on the real bed. Stage A2 makes that same call ON A THROWAWAY so the reading is measured, not inferred.

STAGES (the brief's, in its order)
  A   NON-GATING measurement, three independent throwaway scratches, nothing saved, all deleted:
      A1  delete Wire 10799, then connect_ctl(panel row 'Automatic Error Handling', node 25, term 0)
      A2  delete Wire 10799, then create_indicator(Nodes[25], t0) - what the verb does with a NESTED index
      A3  delete Wire 10799, then wire_indicators(source #10686 'x .and. y?' -> the EXISTING indicator
          'Automatic Error Handling', diagram_index = #639's live index) on a now-BARE source
      Each reports: the exact call form, the error verbatim, whether a wire appeared on `#10686` t0 and on
      the panel row, and ExecState. A refusal or an error is an EXPECTED and ACCEPTABLE answer and stops
      nothing that follows.
  B1  ROW 1 (boolean) on a copy of claudeDev\\D1_s3a_focus_ind.vi -> IFF ExecState == 1, save
      claudeDev\\D1_s3b_row1_<stamp>.vi
  B2  ROW 2 (numeric) FROM THE SAVED B1 FILE, reopened -> IFF ExecState == 1, save
      claudeDev\\D1_s3b_row2_<stamp>.vi
  C   COLD reopen of the B2 file in a freshly restarted LabVIEW - `ExecState` there is the pass criterion
  E   the ORDERED `Is Broken?` pass (42(b), idempotent re-connect) runs LAST, after the cold reopen, on the
      two NEW `#10407` wires. NO `Is Broken?` IS READ ANYWHERE ABOVE A SAVE (52(f)).

PREDICTION CONTRACT (each is a gate; a FAIL is reported, never repaired by a second construction)
  T_*    four md5 pins BEFORE: ORIGINAL 2a78e17c (FATAL), D1_s1_copy 3e3d23ce, D1_s2_loops 6ff19497
         (FATAL), D1_s3a_focus_ind eef91c1d (FATAL); donor OpCreateLocalRead_v0 f695d97a
  A_*    non-gating: recorded as FACTs plus one gate per leg that merely says the leg completed
  B1_a   the bed opens COLD at ExecState 1 and `#10407` t0 carries wire 10799
  B1_b   the delete removes exactly 10799 and bares `#10407` t0 and `#10686` t0
  B1_c   a top-level Nodes[] index exists for the source  <- THE ROUTE'S ADDRESSING PRECONDITION
  B1_d   create_indicator returns exactly one new ControlTerminal; its label is read off the machine
  B1_e   OpCreateLocalRead_v0 with Write?=False adds exactly one Local; census 8 -> 9
  B1_f   RULE-1a GATE (50(i)): the new Local reads back with node_terms as ONE terminal whose NAME equals
         the label the Local was created from and whose is_source is True (= READ)
  B1_g   `#10407` t0 carries a NEW wire whose far end is the LOCAL, not `#10686`
  B1_h   `#637` terminal / wired counts unchanged (no tunnel, no border object) - 50(e)/37(e)
  B1_i   ExecState == 1 at the save; the file exists with its md5 and size recorded
  B2_*   the same, census 9 -> 10, on `#10407` t2 / `#10757` t1 'element'
  C_1    the B2 file reopens COLD at ExecState 1 in a freshly restarted LabVIEW
  E_1/2  the ordered `Is Broken?` reads False on both new `#10407` wires
  Z_*    four md5 pins PASS after; donor byte-unchanged; every scratch exists=False; refs opened==closed,
         0 live; LabVIEW handles reported before and after

WHAT THIS IS NOT
  No new op, no new `gscript` verb, no edit to tools/gscript.py, no recipe (48(n)), no VI run of any D1
  artefact or of the main VI (34(f)) - op VIs are run, the fleet's normal mechanism. No GUI action. No
  motor / ASI / camera (rig 조립). No new process device. `remove_bad_wires_scripted` / `remove_bad_wires` /
  `gui_save` neither imported nor called; `allow_broken` never True; `move_in` neither imported nor called.
  No `Is Broken?` read above a save. The ORIGINAL and the three earlier D1 artefacts are never written.
  NO ROUTE IS CHOSEN OR RECOMMENDED; docs/cycle27-plan.md and STATUS's `## NEXT` are not edited.
"""
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
import contextlib                                                                  # noqa: E402
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index, owner_of                                       # noqa: E402
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
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
DONOR = os.path.join(g.CLAUDEDEV, "OpCreateLocalRead_v0.vi")
DONOR_MD5 = "f695d97a36ae127cd2dd3ca6b1fc1089"

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c62_s3b_rows.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

ROW1_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_%s.vi" % STAMP)
ROW2_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_%s.vi" % STAMP)

CASE_UID = 10407                 # CaseStructure on Diagram #639, Nodes[24]
D639, D536, D686 = 639, 536, 686
LOOP11_UID = 637                 # the 37(e) tunnel / border witness
SCAN_LIMIT = 120
LOCAL_CENSUS_BASE = 8            # docs/toolkit-capabilities.md:284

# the two rows, MEASURED in cycle 62 (tools/bench/diag_c62_branch2.log:27,:61); every number re-read here
ROWS = {
    "B1": {"sink_term": 0, "wire_pin": 10799, "src_uid": 10686, "src_term": 0,
           "src_term_name": "x .and. y?", "old_ct": 23576, "old_control": 23555,
           "old_label": "Automatic Error Handling", "want_census": LOCAL_CENSUS_BASE + 1},
    "B2": {"sink_term": 2, "wire_pin": 10990, "src_uid": 10757, "src_term": 1,
           "src_term_name": "element", "old_ct": 23541, "old_control": 23525,
           "old_label": "index", "want_census": LOCAL_CENSUS_BASE + 2},
}

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 62 material #2: S3b's two rows by Pre-decided 53(d)'s delete-and-rebuild, staged saves",
     "route_source": "docs/cycle27-plan.md Pre-decided 53(d) - NOT chosen here",
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True, "is_broken_read_above_a_save": False,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's normal mechanism",
     "no_gui_action": True,
     "rig_state": "조립 / ASSEMBLED - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "gui_save": "NEVER called", "allow_broken": "NEVER True", "move_in": "not imported, not called",
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "stage_A": {}, "stages": {},
     "artefacts_on_disk": [], "scratches_removed": {}}


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


def diagrams(target, rec):
    """the LIVE Traverse 'Diagram' index of #639, #536 and #686, resolved by uid every time (34(h))."""
    out = {}
    for uid in (D639, D536, D686):
        try:
            out[uid] = diag_index(target, uid)
        except Exception as e:                                                     # noqa: BLE001
            out[uid] = None
            rec["diag_index_error_%d" % uid] = "%s: %s" % (type(e).__name__, str(e)[:200])
    rec["diagram_indices"] = out
    fact("live diagram indices: #639 -> %r, #536 (top level) -> %r, #686 -> %r"
         % (out.get(D639), out.get(D536), out.get(D686)))
    return out


def node_table(target, uid, tag):
    """locate a NODE by uid, read its full terminal table, verified by the node's own uid echo."""
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


def top_level_index_of(target, uid, dtop, rec, tag):
    """The TOP-LEVEL Nodes[] index of `uid`, or None. This is the index space create_indicator addresses."""
    rows, err = [], ""
    if isinstance(dtop, int):
        try:
            rows = g.node_labels(target, dtop)
        except Exception as e:                                                     # noqa: BLE001
            err = "%s: %s" % (type(e).__name__, str(e)[:250])
    i = next((k for k, r in enumerate(rows) if r["uid"] == uid), None)
    rec["top_level_nodes_count"] = len(rows)
    rec["top_level_index_of_%d" % uid] = i
    rec["top_level_lookup_error_verbatim"] = err
    fact("%s: the TOP-LEVEL diagram (#536, traverse index %r) lists %d nodes; the Nodes[] index of #%d there "
         "is %r%s" % (tag, dtop, len(rows), uid, i, ("  ; ERROR " + err) if err else ""))
    return i


def panel_all(target, tag):
    try:
        rows = g.panel_wiring(target)
        err = ""
    except Exception as e:                                                         # noqa: BLE001
        rows, err = [], "%s: %s" % (type(e).__name__, str(e)[:250])
    fact("%s panel_wiring: %d rows%s" % (tag, len(rows), (" ; ERROR " + err) if err else ""))
    return rows, err


def loop637_counts(target, rec, tag):
    """37(e)'s witness: #637's terminal and WIRED-terminal counts. A tunnel or border object moves them."""
    rows, loc = node_table(target, LOOP11_UID, "%s #637" % tag)
    n_terms = len(rows)
    n_wired = sum(1 for r in rows if r.get("wire"))
    rec.setdefault("loop637", []).append({"tag": tag, "n_terms": n_terms, "n_wired": n_wired,
                                          "nodes_index": loc.get("nodes_index"), "how": loc.get("how")})
    fact("%s #637 (WhileLoop): %r terminals, %r WIRED  [%s]" % (tag, n_terms, n_wired, loc.get("how")))
    return n_terms, n_wired


def delete_wire_uid(target, wire_uid, rec, tag):
    try:
        wires = g.report_all(target, "Wire")
        idx = [o["i"] for o in wires if o["uid"] == wire_uid]
        rec["wire_traverse_matches"] = idx
    except Exception as e:                                                         # noqa: BLE001
        rec["wire_traverse_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        idx = []
    if len(idx) != 1:
        rec["delete_error_verbatim"] = "traverse matches %r for wire uid %r" % (idx, wire_uid)
        fact("%s delete NOT ATTEMPTED: %s" % (tag, rec["delete_error_verbatim"]))
        return None
    try:
        gone = g.delete_object(target, "Wire", idx[0])
        rec["delete_error_verbatim"] = ""
        rec["uids_gone"] = sorted(gone) if gone else gone
    except Exception as e:                                                         # noqa: BLE001
        rec["delete_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        rec["uids_gone"] = None
    fact("%s delete_object(Wire[%r] = uid %r): gone %r ; error %r"
         % (tag, idx[0], wire_uid, rec.get("uids_gone"), rec.get("delete_error_verbatim")))
    return rec.get("uids_gone")


# ============================================================ STAGE A - NON-GATING measurement
def a_leg(which, row, rec_key, attempt):
    """copy -> open -> delete the row's Wire -> run ONE attempt -> read back -> close -> DELETE the scratch."""
    bed = os.path.join(g.CLAUDEDEV, "SCRATCH_C62R_%s_%s.vi" % (which, STAMP))
    K = R["stage_A"].setdefault(rec_key, {"bed": os.path.basename(bed), "non_gating": True})
    print("\n========== STAGE A / %s  (NON-GATING measurement, throwaway scratch)" % which, flush=True)
    try:
        shutil.copy2(S3A_ARTEFACT, bed)
        g.open_panel(bed)
        time.sleep(1.0)
        read_exec_state(K, "A/%s cold open" % which, bed)
        dd = diagrams(bed, K)
        d639 = dd.get(D639)
        dtop = dd.get(D536)
        case_rows, _cl = node_table(bed, CASE_UID, "A/%s #10407" % which)
        K["case_t0_before"] = next((r for r in case_rows if r["i"] == row["sink_term"]), None)
        src_rows, src_loc = node_table(bed, row["src_uid"], "A/%s source #%d" % (which, row["src_uid"]))
        K["source_row_before"] = next((r for r in src_rows if r["i"] == row["src_term"]), None)
        K["source_nodes_index_on_639"] = src_loc.get("nodes_index")
        top_level_index_of(bed, row["src_uid"], dtop, K, "A/%s" % which)
        fp0, _e0 = panel_all(bed, "A/%s BEFORE" % which)
        K["panel_row_of_old_indicator_before"] = next(
            (r for r in fp0 if r["uid"] == row["old_control"]), None)
        W = (K["case_t0_before"] or {}).get("wire")
        delete_wire_uid(bed, W, K, "A/%s" % which)
        read_exec_state(K, "A/%s after the delete" % which, bed)
        attempt(bed, K, row, d639, dtop, which)
        # ---- the common readback
        src_rows2, _s2 = node_table(bed, row["src_uid"], "A/%s source AFTER" % which)
        K["source_row_after"] = next((r for r in src_rows2 if r["i"] == row["src_term"]), None)
        case_rows2, _c2 = node_table(bed, CASE_UID, "A/%s #10407 AFTER" % which)
        K["case_t0_after"] = next((r for r in case_rows2 if r["i"] == row["sink_term"]), None)
        fp1, _e1 = panel_all(bed, "A/%s AFTER" % which)
        K["panel_row_of_old_indicator_after"] = next((r for r in fp1 if r["uid"] == row["old_control"]), None)
        K["control_terminal_census_after"] = count_of(bed, "ControlTerminal")
        K["panel_rows_after_count"] = len(fp1)
        read_exec_state(K, "A/%s END" % which, bed)
        fact("A/%s RESULT: source #%d t%d wire %r -> %r ; #10407 t%d wire %r -> %r ; old indicator panel row "
             "%r -> %r" % (which, row["src_uid"], row["src_term"],
                           (K.get("source_row_before") or {}).get("wire"),
                           (K.get("source_row_after") or {}).get("wire"), row["sink_term"],
                           (K.get("case_t0_before") or {}).get("wire"),
                           (K.get("case_t0_after") or {}).get("wire"),
                           (K.get("panel_row_of_old_indicator_before") or {}).get("wire"),
                           (K.get("panel_row_of_old_indicator_after") or {}).get("wire")))
        gate("A_%s the leg completed and was read back (NON-GATING: a refusal is an acceptable answer)"
             % which, True, K.get("attempt_summary", ""))
    except Exception as e:                                                         # noqa: BLE001
        K["leg_exception_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:500])
        fact("A/%s RAISED %s: %s" % (which, type(e).__name__, str(e)[:400]))
        gate("A_%s the leg completed and was read back (NON-GATING)" % which, True,
             "raised %s" % (type(e).__name__,))
    finally:
        close_quietly(bed)
        if os.path.exists(bed):
            try:
                os.remove(bed)
            except Exception as e:                                                 # noqa: BLE001
                R["scratches_removed"][os.path.basename(bed)] = "ERROR %s" % (type(e).__name__,)
        R["scratches_removed"].setdefault(os.path.basename(bed), not os.path.exists(bed))
    dump()


def attempt_connect_ctl(bed, K, row, d639, dtop, which):
    """A1: re-connect the EXISTING indicator to the bared source with connect_ctl (panel-index addressed)."""
    fpl = []
    try:
        fpl = g.fp_labels(bed)
    except Exception as e:                                                         # noqa: BLE001
        K["fp_labels_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    hits = [(i, t, ind) for (i, t, ind) in fpl if t == row["old_label"]]
    K["panel_index_candidates"] = hits
    fact("A/%s fp_labels rows whose label reads %r: %r" % (which, row["old_label"], hits))
    if not hits:
        K["attempt_summary"] = "NOT ATTEMPTED: no front-panel row labelled %r" % (row["old_label"],)
        fact("A/%s %s" % (which, K["attempt_summary"]))
        return
    pi = hits[0][0]
    ni = K.get("source_nodes_index_on_639")
    K["call_form"] = ("g.connect_ctl(bed, panel_index=%r, node_index=%r, terminal_index=%r)   "
                      "# node_index is the source's Nodes[] index on Diagram #639, which is NOT the "
                      "top-level index space connect_ctl's ladder (VI -> Block Diagram -> Nodes[]) uses"
                      % (pi, ni, row["src_term"]))
    fact("A/%s CALL: %s" % (which, K["call_form"]))
    try:
        err = g.connect_ctl(bed, pi, ni, row["src_term"])
        K["error_verbatim"] = repr(err)
    except Exception as e:                                                         # noqa: BLE001
        K["error_verbatim"] = "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])
    K["attempt_summary"] = "connect_ctl -> %s" % K["error_verbatim"]
    fact("A/%s connect_ctl returned/raised: %s" % (which, K["error_verbatim"]))


def attempt_create_indicator(bed, K, row, d639, dtop, which):
    """A2: what create_indicator does when handed a NESTED Nodes[] index (the measurement, not the inference)."""
    ni = K.get("source_nodes_index_on_639")
    K["control_terminal_census_before"] = count_of(bed, "ControlTerminal")
    K["call_form"] = ("g.create_indicator(bed, node_index=%r, terminal_index=%r)   # %r is the source's index "
                      "on Diagram #639; the verb addresses the TOP-LEVEL Nodes[], so this is the measurement "
                      "of what it hits instead" % (ni, row["src_term"], ni))
    fact("A/%s CALL: %s" % (which, K["call_form"]))
    # what actually sits at that index in the TOP-LEVEL space, so the reading is interpretable
    try:
        toprows = g.node_labels(bed, dtop) if isinstance(dtop, int) else []
        K["top_level_node_at_that_index"] = toprows[ni] if (isinstance(ni, int) and ni < len(toprows)) else None
    except Exception as e:                                                         # noqa: BLE001
        K["top_level_node_at_that_index"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:150])
    fact("A/%s the TOP-LEVEL node sitting at Nodes[%r] is %r"
         % (which, ni, K.get("top_level_node_at_that_index")))
    try:
        new = g.create_indicator(bed, ni, row["src_term"])
        K["new_control_terminals"] = new
        K["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        K["new_control_terminals"] = None
        K["error_verbatim"] = "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])
    K["attempt_summary"] = "create_indicator -> new %r ; error %s" % (K.get("new_control_terminals"),
                                                                     K["error_verbatim"])
    fact("A/%s create_indicator returned %r ; error %s ; ControlTerminal census %r -> %r"
         % (which, K.get("new_control_terminals"), K["error_verbatim"],
            K.get("control_terminal_census_before"), count_of(bed, "ControlTerminal")))


def attempt_wire_indicators(bed, K, row, d639, dtop, which):
    """A3: wire_indicators from a now-BARE source onto the EXISTING indicator (its docstring warns it breaks)."""
    cls_rows = {}
    for cls in ("Function", "Node", "GObject"):
        try:
            u = [o["uid"] for o in g.report_all(bed, cls)]
            if row["src_uid"] in u:
                cls_rows[cls] = u.index(row["src_uid"])
        except Exception as e:                                                     # noqa: BLE001
            cls_rows[cls] = "ERROR %s: %s" % (type(e).__name__, str(e)[:100])
    K["source_class_membership"] = cls_rows
    fact("A/%s the source #%d in the Traverse class lists: %r" % (which, row["src_uid"], cls_rows))
    pick = next(((c, i) for c, i in cls_rows.items() if isinstance(i, int)), None)
    if pick is None or not isinstance(d639, int):
        K["attempt_summary"] = "NOT ATTEMPTED: no Traverse class index for the source, or #639 unresolved"
        fact("A/%s %s" % (which, K["attempt_summary"]))
        return
    K["call_form"] = ("g.wire_indicators(bed, node_index=%r, src_terms=[%r], indicator_names=[%r], "
                      "diagram_index=%r, node_class=%r)" % (pick[1], row["src_term_name"], row["old_label"],
                                                            d639, pick[0]))
    fact("A/%s CALL: %s" % (which, K["call_form"]))
    try:
        dt = g.wire_indicators(bed, pick[1], [row["src_term_name"]], [row["old_label"]],
                               diagram_index=d639, node_class=pick[0])
        K["error_verbatim"] = ""
        K["returned"] = dt
    except Exception as e:                                                         # noqa: BLE001
        K["returned"] = None
        K["error_verbatim"] = "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:500])
    K["attempt_summary"] = "wire_indicators -> %r ; error %s" % (K.get("returned"), K["error_verbatim"])
    fact("A/%s wire_indicators returned %r ; error %s" % (which, K.get("returned"), K["error_verbatim"]))


# ============================================================ the Local creator (the donor op, unchanged)
def donor_bool_label():
    """the op's direction control label, READ OFF THE MACHINE - never retyped."""
    try:
        fpl = g.fp_labels(DONOR)
    except Exception as e:                                                         # noqa: BLE001
        fact("donor fp_labels raised %s: %s" % (type(e).__name__, str(e)[:200]))
        return None, []
    cands = [t for (_i, t, ind) in fpl if (not ind) and t and "Write" in t]
    fact("OpCreateLocalRead_v0 front-panel labels READ OFF THE MACHINE: %r ; direction candidates %r"
         % (fpl, cands))
    return (cands[0] if len(cands) == 1 else None), fpl


def call_donor(target, fp_index, bool_label, rec, tag):
    """OpCreateLocalRead_v0 in READ mode (Write? = False) bound to Panel.Controls[fp_index]."""
    rd = {"tag": tag, "fp_index": fp_index, "bool_label": bool_label, "write_flag": False}
    try:
        before = {o["uid"] for o in g.report_all(target, "Local")}
    except Exception as e:                                                         # noqa: BLE001
        before = set()
        rd["local_uids_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    rd["local_census_before"] = count_of(target, "Local")
    vi = g.op(DONOR)
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
        vi.SetControlValue(bool_label, False)          # False = READ (Pre-decided 52(a)/52(e))
        rd["bool_set_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rd["bool_set_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    try:
        g._run(vi)
        rd["run_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rd["run_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    for ind, key in (("Text", "op_matched_label"), ("Indicator", "op_is_indicator")):
        try:
            rd[key] = vi.GetControlValue(ind)
        except Exception as e:                                                     # noqa: BLE001
            rd[key] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    try:
        rd["error_cluster_verbatim"] = repr(vi.GetControlValue("error out"))
    except Exception as e:                                                         # noqa: BLE001
        rd["error_cluster_verbatim"] = "NO 'error out' (%s)" % (type(e).__name__,)
    try:
        after = {o["uid"] for o in g.report_all(target, "Local")}
    except Exception:                                                              # noqa: BLE001
        after = set()
    rd["local_census_after"] = count_of(target, "Local")
    rd["local_uids_added"] = sorted(after - before)
    rec["donor_call"] = rd
    fact("%s OpCreateLocalRead_v0(Write?=False) on Panel.Controls[%r]: error cluster %s ; op walked to %r "
         "(indicator=%r) ; Local census %r -> %r ; new Local uid(s) %r"
         % (tag, fp_index, rd["error_cluster_verbatim"], rd.get("op_matched_label"), rd.get("op_is_indicator"),
            rd["local_census_before"], rd["local_census_after"], rd["local_uids_added"]))
    return rd


# ============================================================ one BUILD stage
def build_row(step, src_path, out_path, row):
    print("\n========== %s  ROW on #%d t%d  (source #%d t%d %r)"
          % (step, CASE_UID, row["sink_term"], row["src_uid"], row["src_term"], row["src_term_name"]),
          flush=True)
    K = R["stages"].setdefault(step, {"from": os.path.basename(src_path),
                                      "to": os.path.basename(out_path), "saved": False})
    shutil.copy2(src_path, out_path)
    g.open_panel(out_path)
    time.sleep(1.0)
    es0 = read_exec_state(K, "%s cold open of the bed" % step, out_path)
    gate("%s_a the bed opens COLD at ExecState 1" % step, es0 == 1, "%r" % (es0,))
    dd = diagrams(out_path, K)
    d639, dtop = dd.get(D639), dd.get(D536)

    K["local_census_before"] = count_of(out_path, "Local")
    K["control_terminal_census_before"] = count_of(out_path, "ControlTerminal")
    fp0, _e0 = panel_all(out_path, "%s BEFORE" % step)
    K["panel_rows_before_count"] = len(fp0)
    t637_0 = loop637_counts(out_path, K, "%s BEFORE" % step)

    case_rows, _cl = node_table(out_path, CASE_UID, "%s BEFORE #10407" % step)
    K["case_table_before"] = case_rows
    sink_row = next((r for r in case_rows if r["i"] == row["sink_term"]), None)
    K["sink_row_before"] = sink_row
    W = (sink_row or {}).get("wire")
    gate("%s_a2 #10407 t%d carries the wire this row replaces" % (step, row["sink_term"]),
         W == row["wire_pin"], "wire %r (the cycle-62 reading was %r)" % (W, row["wire_pin"]))

    src_rows, src_loc = node_table(out_path, row["src_uid"], "%s BEFORE source" % step)
    K["source_table_before"] = src_rows
    K["source_nodes_index_on_639"] = src_loc.get("nodes_index")
    src_row = next((r for r in src_rows if r["i"] == row["src_term"]), None)
    K["source_row_before"] = src_row
    gate("%s_a3 the source terminal's NAME reads off the machine as %r" % (step, row["src_term_name"]),
         (src_row or {}).get("name") == row["src_term_name"],
         "%r (hex %r)" % ((src_row or {}).get("name"), (src_row or {}).get("name_hex")))

    # ---- THE ROUTE'S ADDRESSING PRECONDITION (create_indicator addresses the TOP-LEVEL Nodes[])
    ti = top_level_index_of(out_path, row["src_uid"], dtop, K, "%s precondition" % step)
    K["precondition"] = ("create_indicator(target, node_index, terminal_index) drives OpCreateIndicator_v0, "
                         "whose ladder is VI -> Block Diagram -> Nodes[] (tools/gscript.py:2423-2439); the "
                         "route needs the SOURCE's index in THAT space")
    ok_pre = gate("%s_c THE ROUTE'S PRECONDITION: a TOP-LEVEL Nodes[] index exists for source #%d"
                  % (step, row["src_uid"]), isinstance(ti, int),
                  "top-level index %r ; the source sits on Diagram #639 at Nodes[%r]"
                  % (ti, K.get("source_nodes_index_on_639")))
    if not ok_pre:
        K["stopped_before_the_delete"] = True
        K["stop_reason"] = ("create_indicator cannot address the source: #%d is Nodes[%r] of Diagram #639 "
                            "(traverse index %r) and is absent from the TOP-LEVEL diagram's Nodes[] "
                            "(%r nodes listed). Per the brief, the stage STOPS: nothing saved, the copy "
                            "removed, no second construction, no cast, no splice."
                            % (row["src_uid"], K.get("source_nodes_index_on_639"), d639,
                               K.get("top_level_nodes_count")))
        fact("%s STOPPED: %s" % (step, K["stop_reason"]))
        for label, tbl in (("#10407", K.get("case_table_before")),
                           ("source #%d" % row["src_uid"], K.get("source_table_before"))):
            fact("%s STOP REPORT - the complete terminal table of %s: %r" % (step, label, tbl))
        read_exec_state(K, "%s at the stop (nothing was edited)" % step, out_path)
        close_quietly(out_path)
        if os.path.exists(out_path):
            os.remove(out_path)
        K["file_removed"] = not os.path.exists(out_path)
        dump()
        return None

    # ---- 1. delete the whole Wire object
    gone = delete_wire_uid(out_path, W, K, step)
    gate("%s_b the delete removed EXACTLY the wire uid targeted" % step, gone == [W],
         "gone %r, targeted %r" % (gone, W))
    read_exec_state(K, "%s after the delete (ExecState 0 is EXPECTED here)" % step, out_path)

    # ---- 2. create_indicator on the now-bare SOURCE terminal
    ti = top_level_index_of(out_path, row["src_uid"], dtop, K, "%s after the delete" % step)
    ct_before = count_of(out_path, "ControlTerminal")
    try:
        new_ct = g.create_indicator(out_path, ti, row["src_term"])
        K["create_indicator_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        new_ct = None
        K["create_indicator_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:500])
    K["new_control_terminals"] = new_ct
    ct_after = count_of(out_path, "ControlTerminal")
    fact("%s create_indicator(Nodes[%r].Terminals[%r]) -> %r ; error %r ; ControlTerminal census %r -> %r"
         % (step, ti, row["src_term"], new_ct, K["create_indicator_error_verbatim"], ct_before, ct_after))
    if not gate("%s_d create_indicator returned exactly ONE new ControlTerminal" % step,
                isinstance(new_ct, list) and len(new_ct) == 1, "%r" % (new_ct,)):
        return abandon(step, K, out_path, "create_indicator produced %r" % (new_ct,), row)
    read_exec_state(K, "%s after create_indicator" % step, out_path)

    # ---- the new indicator's LABEL, read off the machine
    fp1, _e1 = panel_all(out_path, "%s after create_indicator" % step)
    known = {r["uid"] for r in fp0}
    newrows = [r for r in fp1 if r["uid"] not in known]
    K["new_panel_rows"] = newrows
    fact("%s the panel row(s) that appeared: %r" % (step, newrows))
    try:
        fpl = g.fp_labels(out_path)
    except Exception as e:                                                         # noqa: BLE001
        fpl = []
        K["fp_labels_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    new_label = newrows[0]["label"] if len(newrows) == 1 else None
    K["new_indicator_label_read_off_the_machine"] = new_label
    K["new_indicator_label_hex"] = (new_label or "").encode("utf-8").hex()
    hits = [(i, t, ind) for (i, t, ind) in fpl if t == new_label]
    K["new_indicator_panel_rows"] = hits
    fact("%s the NEW indicator's label READ OFF THE MACHINE: %r (hex %r) ; fp_labels rows matching: %r"
         % (step, new_label, K["new_indicator_label_hex"], hits))
    if not gate("%s_d2 the new indicator has exactly one front-panel row and a label" % step,
                bool(new_label) and len(hits) == 1, "label %r rows %r" % (new_label, hits)):
        return abandon(step, K, out_path, "the new indicator's label/panel row is ambiguous", row)

    # ---- 3. the Local, in READ mode, bound to THAT new indicator
    bool_label, _fpl_donor = donor_bool_label()
    K["donor_direction_control_label"] = bool_label
    if not gate("%s_e0 the donor's direction control was identified on the machine" % step,
                bool(bool_label), "%r" % (bool_label,)):
        return abandon(step, K, out_path, "the donor's Write? control could not be identified", row)
    rd = call_donor(out_path, hits[0][0], bool_label, K, step)
    gate("%s_e the Local census went %r -> %r (want %r)"
         % (step, rd["local_census_before"], rd["local_census_after"], row["want_census"]),
         rd["local_census_after"] == row["want_census"],
         "added %r" % (rd["local_uids_added"],))
    if len(rd["local_uids_added"]) != 1:
        return abandon(step, K, out_path, "the donor added %r Locals" % (len(rd["local_uids_added"]),), row)
    local_uid = rd["local_uids_added"][0]
    read_exec_state(K, "%s after the Local was created (unwired: 0 is EXPECTED)" % step, out_path)

    # ---- 4. THE RULE-1a GATE (50(i)): read the Local back with node_terms
    lrows, lloc = node_table(out_path, local_uid, "%s the new Local" % step)
    K["local_readback"] = {"uid": local_uid, "loc": lloc, "terminal_rows_verbatim": lrows}
    one = lrows[0] if len(lrows) == 1 else {}
    fact("%s LOCAL READBACK VERBATIM: Local #%s -> %d terminal(s); NAME %r (hex %r), is_source %r, wire %r ; "
         "owner %r#%r diagram %r Nodes[%r]"
         % (step, local_uid, len(lrows), one.get("name"), one.get("name_hex"), one.get("is_source"),
            one.get("wire"), lloc.get("owner_class"), lloc.get("owner_uid"), lloc.get("diagram_index"),
            lloc.get("nodes_index")))
    gate("%s_f RULE-1a GATE (50(i)): ONE terminal, NAME == the label it was created from, is_source True "
         "(= READ)" % step,
         len(lrows) == 1 and one.get("name") == new_label and one.get("is_source") is True,
         "name %r (hex %r) vs label %r (hex %r) ; is_source %r"
         % (one.get("name"), one.get("name_hex"), new_label, K["new_indicator_label_hex"],
            one.get("is_source")))

    # ---- 5. connect the Local's SOURCE into the freed #10407 sink
    case_rows_n, case_loc = node_table(out_path, CASE_UID, "%s #10407 before the connect" % step)
    sink_i = case_loc.get("nodes_index")
    src_diag = lloc.get("diagram_index")
    src_i = lloc.get("nodes_index")
    K["connect_call"] = ("connect_nested_v1(target, sink_diag=%r, sink_node=%r, sink_term=%r, src_diag=%r, "
                         "src_node=%r, src_term=%r)" % (d639, sink_i, row["sink_term"], src_diag, src_i,
                                                        one.get("i", 0)))
    fact("%s CONNECT: %s" % (step, K["connect_call"]))
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es_c, err_c = CONNECT_V1(out_path, d639, sink_i, row["sink_term"], src_diag, src_i,
                                         one.get("i", 0), V1_LABELS)
        K["connect_result"] = {"wire_delta": dw, "exec_state_returned": es_c, "error_verbatim": err_c}
    except Exception as e:                                                         # noqa: BLE001
        K["connect_result"] = {"wire_delta": None, "exec_state_returned": None,
                               "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])}
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    fact("%s connect result: %r" % (step, K["connect_result"]))

    # ---- the readbacks
    case_rows2, _c2 = node_table(out_path, CASE_UID, "%s AFTER #10407" % step)
    K["case_table_after"] = case_rows2
    sink_after = next((r for r in case_rows2 if r["i"] == row["sink_term"]), None)
    K["sink_row_after"] = sink_after
    lrows2, _l2 = node_table(out_path, local_uid, "%s the Local AFTER" % step)
    K["local_table_after"] = lrows2
    far_ok = bool(sink_after and sink_after.get("wire")) and bool(lrows2 and lrows2[0].get("wire")) \
        and sink_after.get("wire") == lrows2[0].get("wire")
    K["new_sink_wire"] = (sink_after or {}).get("wire")
    K["far_end_owner_uid"] = local_uid
    K["far_end_terminal_name"] = (lrows2[0].get("name") if lrows2 else None)
    fact("%s #10407 t%d now carries wire %r ; the LOCAL #%s carries wire %r on terminal %r - far-end owner "
         "uid %r, terminal name %r"
         % (step, row["sink_term"], K["new_sink_wire"], local_uid,
            (lrows2[0].get("wire") if lrows2 else None), (lrows2[0].get("i") if lrows2 else None),
            local_uid, K["far_end_terminal_name"]))
    gate("%s_g #10407 t%d carries a NEW wire whose far end is the LOCAL, not #%d"
         % (step, row["sink_term"], row["src_uid"]), far_ok,
         "sink wire %r, local wire %r" % (K["new_sink_wire"], (lrows2[0].get("wire") if lrows2 else None)))

    src_rows2, _s2 = node_table(out_path, row["src_uid"], "%s AFTER source" % step)
    K["source_table_after"] = src_rows2
    sr2 = next((r for r in src_rows2 if r["i"] == row["src_term"]), None)
    K["source_row_after"] = sr2
    gate("%s_g2 the source #%d t%d now feeds the NEW indicator (a wire is present)"
         % (step, row["src_uid"], row["src_term"]), bool(sr2 and sr2.get("wire")), "%r" % (sr2,))

    t637_1 = loop637_counts(out_path, K, "%s AFTER" % step)
    gate("%s_h #637 terminal/wired counts UNCHANGED (no tunnel, no border object - 50(e)/37(e))" % step,
         t637_0 == t637_1, "%r -> %r" % (t637_0, t637_1))
    fp2, _e2 = panel_all(out_path, "%s AFTER" % step)
    K["panel_rows_after_count"] = len(fp2)
    K["control_terminal_census_after"] = count_of(out_path, "ControlTerminal")
    K["old_indicator_rows_after"] = [r for r in fp2 if r["uid"] in (row["old_control"],)]
    fact("%s panel rows %r -> %r ; ControlTerminal census %r -> %r ; the OLD indicator row (control uid %d) "
         "is still present: %r" % (step, K["panel_rows_before_count"], K["panel_rows_after_count"],
                                   K["control_terminal_census_before"], K["control_terminal_census_after"],
                                   row["old_control"], K["old_indicator_rows_after"]))

    # ---- 6. the SAVE, IFF ExecState == 1. NO `Is Broken?` IS READ ABOVE THIS POINT (52(f)).
    es_save = read_exec_state(K, "%s immediately before the save decision" % step, out_path)
    if es_save != 1:
        return abandon(step, K, out_path, "ExecState reads %r where 1 is required" % (es_save,), row)
    try:
        g.save(out_path)
        K["save_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        K["save_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    close_quietly(out_path)
    ff = D.file_facts("%s the saved artefact" % step, out_path)
    K["file_facts"] = ff
    K["saved"] = bool(ff.get("exists"))
    R["artefacts_on_disk"].append({"stage": step, "path": out_path, "md5": ff.get("md5"),
                                   "size": ff.get("size")})
    gate("%s_i *** THE STAGE'S ARTEFACT: ExecState 1 at the save and the file exists ***" % step,
         es_save == 1 and bool(ff.get("exists")) and not K["save_error_verbatim"],
         "md5 %r size %r error %r" % (ff.get("md5"), ff.get("size"), K["save_error_verbatim"]))
    K["local_uid"] = local_uid
    K["new_wire_uid"] = K["new_sink_wire"]
    K["sink_nodes_index"] = sink_i
    K["src_diag_of_local"] = src_diag
    K["src_nodes_index_of_local"] = src_i
    K["local_term_index"] = one.get("i", 0)
    dump()
    return out_path


def abandon(step, K, out_path, why, row):
    K["abandoned_because"] = why
    fact("%s STAGE STOPPED: %s - nothing saved for this stage, the copy is removed. No second construction, "
         "no cast, no splice (51(h))." % (step, why))
    read_exec_state(K, "%s at the stop" % step, out_path)
    for label, uid in (("#10407", CASE_UID), ("source #%d" % row["src_uid"], row["src_uid"])):
        rows, _l = node_table(out_path, uid, "%s STOP REPORT %s" % (step, label))
        K.setdefault("stop_report_tables", {})[label] = rows
    close_quietly(out_path)
    if os.path.exists(out_path):
        try:
            os.remove(out_path)
        except Exception as e:                                                     # noqa: BLE001
            fact("%s could not remove %s: %s" % (step, out_path, e))
    K["file_removed"] = not os.path.exists(out_path)
    dump()
    return None


# ============================================================ the ORDERED `Is Broken?` pass (42(b)) - LAST
def ordered_pass(target, step, K):
    P = R["stages"].setdefault(step, {}).setdefault("ordered_pass", {})
    need = ("sink_nodes_index", "local_term_index", "src_nodes_index_of_local", "src_diag_of_local")
    src = R["stages"].get(step, {})
    if not all(src.get(k) is not None for k in need):
        P["not_attempted_because"] = "the stage did not reach a wired state; %r" % ({k: src.get(k)
                                                                                     for k in need},)
        fact("%s ORDERED PASS NOT ATTEMPTED: %s" % (step, P["not_attempted_because"]))
        gate("E_%s the ORDERED `Is Broken?` reads False on the new #10407 wire" % step, False,
             "NOT ATTEMPTED: %s" % P["not_attempted_because"])
        return
    dd = diagrams(target, P)
    d639 = dd.get(D639)
    loc = node_table(target, CASE_UID, "%s ordered pass #10407" % step)[1]
    sink_i = loc.get("nodes_index")
    lrows, lloc = node_table(target, src["local_uid"], "%s ordered pass the Local" % step)
    P["call"] = ("connect_nested_v1(target, %r, %r, %r, %r, %r, %r) - IDEMPOTENT re-connect of an EXISTING "
                 "connection; wire_delta must be 0" % (d639, sink_i, ROWS[step]["sink_term"],
                                                       lloc.get("diagram_index"), lloc.get("nodes_index"),
                                                       (lrows[0]["i"] if lrows else 0)))
    fact("%s %s" % (step, P["call"]))
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, d639, sink_i, ROWS[step]["sink_term"],
                                     lloc.get("diagram_index"), lloc.get("nodes_index"),
                                     (lrows[0]["i"] if lrows else 0), V1_LABELS)
        P.update({"wire_delta": dw, "exec_state_returned": es, "error_verbatim": err})
    except Exception as e:                                                         # noqa: BLE001
        P.update({"wire_delta": None, "exec_state_returned": None,
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
    P["op_indicators"] = rd
    ib = rd.get("Is Broken?")
    P["is_broken_ordered"] = ib
    fact("%s ORDERED `Is Broken?` = %r on wire uid %r (wire_delta %r - expected 0, op error %r)"
         % (step, ib, rd.get("UID 2"), P.get("wire_delta"), P.get("error_verbatim")))
    gate("E_%s the ORDERED `Is Broken?` reads False on the new #10407 wire" % step, ib is False,
         "Is Broken? %r on wire %r ; wire_delta %r" % (ib, rd.get("UID 2"), P.get("wire_delta")))
    read_exec_state(None, "%s after the Is Broken? read (SUSPECT, NAMES.md:912-918; the saves are done)"
                    % step, target)


# ============================================================ MAIN
def main():
    print("=== diag_c62_s3b_rows  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== S3b's two rows, Pre-decided 53(d)'s delete-and-rebuild, staged saves", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 D1_s2_loops.vi", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 D1_s3a_focus_ind.vi (the beds' SOURCE, never a bed)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    dn = probe("T4 the donor OpCreateLocalRead_v0.vi", DONOR)
    gate("T4 OpCreateLocalRead_v0.vi md5 == %s" % DONOR_MD5, dn.get("md5") == DONOR_MD5, dn.get("md5", "?"))

    D.fresh("T5 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    row1 = ROWS["B1"]
    try:
        a_leg("A1", row1, "A1_connect_ctl", attempt_connect_ctl)
        a_leg("A2", row1, "A2_create_indicator_nested_index", attempt_create_indicator)
        a_leg("A3", row1, "A3_wire_indicators_bare_source", attempt_wire_indicators)
    except Exception as e:                                                         # noqa: BLE001
        fact("STAGE A raised %s: %s" % (type(e).__name__, str(e)[:400]))

    b1 = b2 = None
    try:
        b1 = build_row("B1", S3A_ARTEFACT, ROW1_PATH, ROWS["B1"])
    except Stop as s:
        fact("B1 STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        fact("B1 RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
        R["stages"].setdefault("B1", {})["raised"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        close_quietly(ROW1_PATH)
    if b1:
        try:
            D.fresh("B2 RESTART (a fresh LabVIEW before the next staged step)")
            b2 = build_row("B2", b1, ROW2_PATH, ROWS["B2"])
        except Stop as s:
            fact("B2 STOPPED: %s" % s)
        except Exception as e:                                                     # noqa: BLE001
            fact("B2 RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
            R["stages"].setdefault("B2", {})["raised"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            close_quietly(ROW2_PATH)
    else:
        gate("B2_skip B2 was NOT reached (it starts from the saved B1 file)", False,
             "B1 produced no file")
    dump()

    # ---- C: the COLD reopen in a freshly restarted LabVIEW, then E: the ordered pass, LAST
    if b2:
        print("\n========== C  COLD reopen of the B2 artefact in a freshly restarted LabVIEW", flush=True)
        D.fresh("C RESTART before the cold reopen")
        R["handles"]["after_c_restart"] = labview_handles()
        try:
            g.open_panel(b2)
            time.sleep(1.0)
        except Exception as e:                                                     # noqa: BLE001
            fact("C open_panel raised %s: %s" % (type(e).__name__, str(e)[:300]))
        es_cold = read_exec_state(None, "C COLD, freshly restarted LabVIEW", b2)
        R["cold_exec_state"] = es_cold
        gate("C_1 *** THE ARTEFACT'S PASS CRITERION: COLD ExecState == 1 ***", es_cold == 1,
             "%r" % (es_cold,))
        print("\n========== E  the ORDERED `Is Broken?` pass (42(b)) - LAST, after the cold reopen",
              flush=True)
        for step in ("B1", "B2"):
            ordered_pass(b2, step, R["stages"].get(step, {}))
        close_quietly(b2)
    else:
        gate("C_1 *** THE ARTEFACT'S PASS CRITERION: COLD ExecState == 1 ***", False,
             "NOT REACHED: no B2 artefact")
        for step in ("B1", "B2"):
            gate("E_%s the ORDERED `Is Broken?` reads False on the new #10407 wire" % step, False,
                 "NOT REACHED: no B2 artefact")
    dump()

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
    z3 = probe("Z1d D1_s3a_focus_ind.vi after everything", S3A_ARTEFACT)
    z4 = probe("Z1e the donor OpCreateLocalRead_v0.vi after everything", DONOR)
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    gate("Z_1b the donor OpCreateLocalRead_v0.vi is byte-unchanged", z4.get("md5") == DONOR_MD5,
         "%s" % (z4.get("md5"),))
    left = [p for p in R["scratches_removed"] if os.path.exists(os.path.join(g.CLAUDEDEV, p))]
    gate("Z_2 every STAGE-A scratch was deleted in the same run", not left, "still present: %r" % (left,))
    rc = R["ref_counts"] or {}
    gate("Z_1c refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    fact("THE COMPLETE ExecState TIMELINE: %r" % (R["exec_state_timeline"],))
    fact("THE ARTEFACTS ON DISK: %r" % (R["artefacts_on_disk"],))

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
