"""diag_c64_s3b_row1 - cycle 64 material #5. THE DELIVERABLE BUILD: S3b ROW 1 ONLY, WITH STAGED SAVES.

ROW 2 IS NOT IN THIS FILE. Nothing is re-chosen, no route is recommended, no plan document is edited.

WHAT CHANGED AND WHY THIS CAN NOW BE BUILT (judgement, cycle 64, from tools/bench/diag_c64_junkpurge.log,
34 pass / 0 fail): `OpConnectNested_v1` does NOT perturb the `ExecState` reading. It leaves an ORPHAN
`Invoke` node - six terminals, ZERO wired, errs [0,0,0,1055] - on the diagram it worked on, and THAT breaks
the VI. Measured on both beds: 1 -> 0 after the connect -> 1 after deleting the orphan BY UID, stable across
three re-reads, with the `Wire` and `ControlTerminal` censuses unchanged. It is the same junk `Invoke` that
cycle 62's `move_in` purged (#9317).
THEREFORE: EVERY op call in this build is followed by a whole-VI `Node` census diff, and any NEW unwired
orphan node is purged BY UID before the next step. No `allow_broken`, no `gui_save`, no GUI action, no new
op - `gscript.save` will accept a legal VI.

WHAT ALREADY EXISTS AND IS REUSED, NOT REBUILT (checked before writing a line of this file - CLAUDE.md
"before creating any new op, tool or recipe, check what already exists"):
  tools/bench/diag_c64_junkpurge.py     the gate/fact/probe/read_es/safe/counts/node_census/new_nodes/
                                        find-the-owning-diagram/terms/delete-by-uid/purge skeleton, the md5
                                        pin block and the NO-open_panel discipline - reused in structure
  tools/bench/diag_c62_s3b_movein.py    the row-1 route itself (delete wire -> donor Local -> move_in ->
                                        connect -> save -> wire_indicators -> save -> cold reopen ->
                                        ordered pass), the donor call, the T3 separator, the file rule.
                                        Its ONE failure was B1_f `ExecState == 1 after the connect` = 0,
                                        i.e. exactly the junk `Invoke` dispatch #4 has now identified
  tools/gscript.py                      :210 op :233 ref_counts :262 reset :341 _run :488 report_all
                                        :587 node_labels :826 panel_wiring :925 node_terms_uid :1005 count
                                        :1017 uids :1257 close_panel :1756 wire_indicators :1977 exec_state
                                        :2062 save :2275 delete_object :2475 fp_labels - NO new verb, NO
                                        edit to gscript.py
  tools/recipes/build_d1_v0.py:318 move_in (it calls g.ensure_loaded itself) / :357 diag_index
  tools/recipes/build_opconnectnested_v1.py:418 connect_nested_v1 (md5 b7a1bb56..., byte-unchanged)
  claudeDev\\OpCreateLocalRead_v0.vi     md5 f695d97a..., READ mode via `Write?` = False (52(a)/52(e))
  tools/hash_probe.py probe / tools/bench/bench_prep.py labview_handles / tools/bench/diag_s2_scaffold.py
                                        fresh + file_facts + the ORIGINAL/S1 pins

FORBIDDEN AND ABSENT, by inspection:
  NO `g.open_panel` CALL ANYWHERE IN THIS FILE and NO `g.ensure_loaded` call either (dispatch #2's poison;
  archive/peer/2026-09-21-c64-openpanel-cap.md). The first EDIT of the run is `delete_object`, which calls
  `ensure_loaded` INTERNALLY (gscript.py:2293), and every later mutator does the same (move_in
  build_d1_v0.py:321, wire_indicators gscript.py:1781, connect_nested_v1 through its own delete/create).
  No VI file LabVIEW may hold open is ever overwritten by a copy: `g.save` writes the WORKING copy in place,
  and each artefact is a fresh stamped path LabVIEW has never seen.
  No `allow_broken`, no `gui_save`, no `remove_bad_wires*`, no GUI action, no new op, no new gscript verb,
  no recipe, nothing written under tools/recipes/, no VI run (34(f) - OP VIs are run, the fleet's normal
  mechanism), no motor/ASI/camera (rig 조립/ASSEMBLED), no new process device. retrospective.py /
  audit_cycle.py / violations.py / doc_ingest.py / prior_art_review.py are NOT run (54(a)).
  docs/cycle27-plan.md and STATUS.md's `## NEXT` are not edited.

⚠️ ONE KNOWN CONTRADICTION INSIDE THE BRIEF, REPORTED NOT RESOLVED: the brief names the static gate
`tools/bench/c60c_astcheck.py`, whose GATE 7 is "move_in is neither imported nor called" (it encodes the
cycle-60 brief's prohibition), while THIS brief's step 4 MANDATES `move_in`. Gate 7 therefore FAILS by
construction, exactly as it did for the identical route in tools/bench/c62f_astcheck.log:11. It is reported
VERBATIM and nothing is edited to silence it: the gate file is not touched, no alias hides the call, and
CYCLE_GUARD_OFF is never set. Every OTHER gate of c60c_astcheck must be OK.

⚠️ ONE IMPLEMENTATION SAFETY NARROWING, STATED UP FRONT: the purge deletes a new node only when it is an
`Invoke` with ZERO wired terminals (the shape dispatch #4 measured) and is not a uid this build intends
(the new Local). Any OTHER new unwired node is REPORTED VERBATIM and NOT deleted - deleting an unrecognised
object would destroy the artefact this dispatch exists to produce.

VERIFICATION LEVEL: STRUCTURAL, NEVER FUNCTIONAL (34(f)). Nothing here runs the D1 artefact or the main VI;
no data flows through the edited diagram. `ExecState == 1` is the compiler's verdict, not a numeric check.

PREDICTION CONTRACT (a failed prediction is a REVIEW trigger, not a retry; a step whose ExecState is not
what the sequence expects STOPS the build and files already saved STAY SAVED)
  A0  the working copy of D1_s3a_focus_ind.vi opens COLD at ExecState 1 with Wire 1905 / Node 630 /
      ControlTerminal 116 / Local 8, and #637 reads 59 terminals / 48 wired
  A1  #10407 resolves on Diagram #639 (traverse index re-read live) at Nodes[24] with t0 carrying wire 10799;
      #10686 at Nodes[25] with t0 named 'x .and. y?'; panel control 23555 is front-panel row 115 and its
      label is read off the machine
  B   delete_object removes EXACTLY wire uid 10799; ExecState 0 is EXPECTED here (unwired Case selector)
  C   OpCreateLocalRead_v0(Write? = False) adds EXACTLY ONE Local, census 8 -> 9
  C2  RULE-1a GATE (50(i)): the new Local reads back with EXACTLY ONE terminal, NAME == the label read off
      the machine, is_source True (= READ)
  D   move_in leaves that Local owned by Diagram #639, still ONE terminal, still is_source True, census 9
  E   connect_nested_v1(46,24,0,46,<local>,0): wire_delta 1, ONE wire uid at BOTH ends, #637 back at 59/48
      (50(e) no-tunnel criterion), ControlTerminal 116, Local 9
  F   the census diff isolates the junk node; its uid, class, label and FULL terminal table are reported and
      it is deleted BY UID
  G   *** ExecState == 1 is REQUIRED here *** -> SAVE claudeDev\\D1_s3b_row1a_<stamp>.vi ; md5, size, mtime.
      A saved file byte-identical to the bed means THE IN-MEMORY EDITS DID NOT LAND - reported as a FAILURE,
      never as a pass (cycle 62's C_1 false pass)
  H   wire_indicators(node_index=<live 'Function' index of #10686, expected 102>, src_terms=['x .and. y?'],
      indicator_names=[<the label read off the machine>], diagram_index=<live #639>) re-feeds that SAME
      existing indicator. Its raise-on-exec_state!=1 (gscript.py:1794-1797) is a measured defect, NOT
      repaired here; a raise is reported VERBATIM as a READING and the machine is censused before any verdict
  I   T3 separator: exactly ONE source on the re-fed net and control 23555 among its sinks
  J   ExecState == 1 -> SAVE claudeDev\\D1_s3b_row1_<stamp>.vi ; md5, size
  K   RESTART, then COLD read of that final file: ExecState 1 is the artefact's pass criterion, plus md5,
      Wire / Node / ControlTerminal / Local censuses, and #10407 t0's wire uid with its far-end owner
  L   LAST, after the cold reopen only (42(b), 52(f)): the ORDERED `Wire.Is Broken?` pass on the new
      #10407 t0 wire. NOTHING is saved after this point; the in-memory VI is discarded
  Z   four md5 pins hold before AND after (ORIGINAL 2a78e17c / D1_s1_copy 3e3d23ce / D1_s2_loops 6ff19497 /
      D1_s3a_focus_ind eef91c1d); OpCreateLocalRead_v0.vi and OpConnectNested_v1.vi byte-unchanged; the
      working copy is removed; refs opened == closed == 0 live; handles reported either side
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
import build_opconnectnested_v1 as CN1                                             # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index, move_in                                        # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
DONOR = os.path.join(g.CLAUDEDEV, "OpCreateLocalRead_v0.vi")
DONOR_MD5 = "f695d97a36ae127cd2dd3ca6b1fc1089"
OP_V1 = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")
OP_V1_MD5_PREFIX = "b7a1bb56"

TOP = 0                                  # Traverse "Diagram" index 0 = the top-level diagram
CASE_UID = 10407                         # the CaseStructure on Diagram #639 - the SINK
SRC_UID = 10686                          # 'x .and. y?' - the SOURCE
D639 = 639
WIRE_PIN = 10799                         # the wire row 1 replaces
OLD_CONTROL = 23555                      # the EXISTING indicator's panel control uid
OLD_LABEL = "Automatic Error Handling"   # recorded; the LIVE label is read off the machine and used
FP_ROW_EXPECT = 115
SINK_TERM = 0
SRC_TERM = 0
SRC_TERM_NAME = "x .and. y?"
SRC_FUNCTION_INDEX_EXPECT = 102
EXPECT_SINK_IDX, EXPECT_SRC_IDX = 24, 25

NODE_BASE, WIRE_BASE, CT_BASE, LOCAL_BASE = 630, 1905, 116, 8
LOOP11_UID = 637
SIBLING_DIAG_UID = 686                   # the FlatSequenceFrame diagram that HOLDS WhileLoop #637
                                         # (diag_s2_scaffold.py:91) - the first hint for every #637 read,
                                         # so the bounded scan is one node_labels call, not a whole sweep
LOOP637_BASELINE = (59, 48)
MOVE_POSITION = (120, 4000)              # diag_s58_boolwire.py:193 - inside Diagram #639; cosmetic only
SCAN_BUDGET_S = 240.0
T3_SCAN_LIMIT = 140

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c64_s3b_row1.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

WORK = os.path.join(g.CLAUDEDEV, "WORK_C64R1_%s.vi" % STAMP)            # the working copy, removed at the end
STEP7_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_row1a_%s.vi" % STAMP)    # the step-7 artefact
STEP9_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_%s.vi" % STAMP)     # the step-9 artefact

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 64 material #5: S3b ROW 1 ONLY, the deliverable build, with staged saves and a "
             "node-census-and-purge after EVERY op call",
     "row2_attempted": False,
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "no_open_panel_call_in_this_file": True,
     "no_ensure_loaded_call_in_this_file": True,
     "edits_reach_the_load_through_the_wrappers": ("delete_object gscript.py:2293, move_in "
                                                   "build_d1_v0.py:321, wire_indicators gscript.py:1781 "
                                                   "call ensure_loaded INTERNALLY"),
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True, "no_gui_action": True,
     "allow_broken": "NEVER True", "gui_save": "NEVER called",
     "remove_bad_wires_scripted": "not imported, not called",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "astcheck_gate7_conflict": ("c60c_astcheck GATE 7 forbids move_in; this brief's step 4 mandates it. "
                                 "Reported verbatim, nothing edited to silence it."),
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "purges": [], "build": {}}
K = R["build"]


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        dump()
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


def safe(label, fn, default=None):
    """Run one read, record its error VERBATIM, never let it kill the run."""
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def read_es(tag, target):
    t0 = time.time()
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    row = {"step": len(R["exec_state_timeline"]) + 1, "tag": tag,
           "target": os.path.basename(target), "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    fact("ExecState [%02d %s] = %r   (+%.1f s, read cost %.2f s)"
         % (row["step"], tag, es, row["t_since_start_s"], row["read_cost_s"]))
    return es


def counts(path, tag, classes=("Node", "Wire", "ControlTerminal", "Local")):
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    fact("%s counts: %r" % (tag, rec))
    return rec


def node_census(path, tag):
    rows, err = safe("%s report_all('Node')" % tag, lambda: g.report_all(path, "Node"), [])
    out = [{"i": r["i"], "uid": r["uid"], "class": r["class"], "pos": r["pos"], "owner_class": r["owner"]}
           for r in (rows or [])]
    fact("%s node census: %d rows%s" % (tag, len(out), ("  [%s]" % err) if err else ""))
    return out, err


def new_nodes(before, after):
    seen = {n["uid"] for n in before}
    return [n for n in after if n["uid"] not in seen]


def find_node(path, uid, hints, tag, budget_s=SCAN_BUDGET_S):
    """Which DIAGRAM lists `uid` in its Nodes[] - answered by the census that finds it, NEVER by owner_of.

    owner_of is measured to answer with the PREVIOUS query's object, silently (Pre-decided 53(d8));
    tools/bench/diag_c64_junkpurge.py:240-270 is this helper's source.
    """
    t0 = time.time()
    rec = {"uid": uid, "hints": list(hints), "scanned": [], "found": None}
    diags, derr = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(path, "Diagram"), [])
    rec["diagram_rows"] = len(diags or [])
    rec["diagram_census_error"] = derr
    by_index = {d["i"]: d for d in (diags or [])}
    order = [i for i in hints if isinstance(i, int) and i in by_index]
    order += [i for i in sorted(by_index) if i not in order]
    for i in order:
        if time.time() - t0 > budget_s:
            rec["scan_stopped"] = "budget %.0f s reached after %d diagrams" % (budget_s, len(rec["scanned"]))
            break
        rows, err = safe("%s node_labels(%d)" % (tag, i), lambda k=i: g.node_labels(path, k), [])
        rec["scanned"].append({"diagram_index": i, "diagram_uid": by_index[i]["uid"],
                               "nodes": len(rows or []), "error": err})
        hit = next((k for k, r in enumerate(rows or []) if r["uid"] == uid), None)
        if hit is not None:
            rec["found"] = {"diagram_index": i, "diagram_uid": by_index[i]["uid"],
                            "diagram_class": by_index[i]["class"], "nodes_index": hit,
                            "nodes_on_diagram": len(rows), "label": rows[hit]["label"]}
            break
    rec["scan_cost_s"] = round(time.time() - t0, 1)
    fact("%s #%s lives at: %r  (%d diagram(s) scanned of %d, %.1f s)"
         % (tag, uid, rec["found"], len(rec["scanned"]), rec["diagram_rows"], rec["scan_cost_s"]))
    return rec


def terms_at(path, diagram_index, nodes_index, expect_uid, tag):
    """The FULL terminal table of one node, with the node's own uid echoed back before it is believed."""
    rec = {"diagram_index": diagram_index, "nodes_index": nodes_index, "expected_uid": expect_uid}
    try:
        echo, rows = g.node_terms_uid(path, int(diagram_index), int(nodes_index))
        rec["uid_echo"] = echo
        rec["ok"] = (expect_uid is None) or (echo == expect_uid)
        rec["terminals"] = [{"i": t["i"], "name": t["name"],
                             "name_hex": (t["name"] or "").encode("utf-8").hex(),
                             "is_source": t["is_source"], "wire": t["wire"], "has_wire": bool(t["wire"]),
                             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]}
                            for t in rows]
    except Exception as e:                                                         # noqa: BLE001
        rec["ok"] = False
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        rec["terminals"] = []
    fact("%s terminal table of #%s (Diagram idx %r, Nodes[%r], echo %r): %d terminal(s)"
         % (tag, expect_uid, diagram_index, nodes_index, rec.get("uid_echo"), len(rec["terminals"])))
    for t in rec["terminals"]:
        fact("    %s t%-2d %-34r is_source=%-5r wire=%-7r errs=%r"
             % (tag, t["i"], t["name"], t["is_source"], t["wire"], t["errs"]))
    return rec


def node_view(path, uid, hints, tag):
    """locate a node by uid (census scan) + read its full terminal table. Returns (loc, rows)."""
    loc = find_node(path, uid, hints, tag)
    f = loc.get("found") or {}
    if f.get("nodes_index") is None:
        return loc, []
    tt = terms_at(path, f["diagram_index"], f["nodes_index"], uid, tag)
    loc["uid_echo"] = tt.get("uid_echo")
    loc["terminal_table"] = tt
    return loc, tt.get("terminals", [])


def delete_by_uid(path, cls, uid, tag):
    """report_all(cls) -> .index(uid) -> delete_object(cls, idx). The shape cycle 58 used; no new verb."""
    rec = {"class": cls, "uid": uid}
    rows, err = safe("%s report_all(%r) before delete" % (tag, cls), lambda: g.report_all(path, cls), [])
    rec["census_before"] = len(rows or [])
    rec["census_error"] = err
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    rec["index"] = idx
    if idx is None:
        rec["result"] = "NOT IN THE %s CENSUS (%d rows) - nothing deleted" % (cls, len(rows or []))
        fact("%s delete %s #%s: %s" % (tag, cls, uid, rec["result"]))
        return rec
    t0 = time.time()
    try:
        gone = g.delete_object(path, cls, idx, verify=True)
        rec["gone"] = sorted(int(x) for x in (gone or []))
        rec["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["gone"] = None
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    rec["call_cost_s"] = round(time.time() - t0, 2)
    after, _ = safe("%s report_all(%r) after delete" % (tag, cls), lambda: g.report_all(path, cls), [])
    rec["census_after"] = len(after or [])
    rec["still_present"] = any(r["uid"] == uid for r in (after or []))
    fact("%s delete %s #%s at index %r: gone %r, error %r, census %r -> %r, still present %r (%.2f s)"
         % (tag, cls, uid, idx, rec.get("gone"), rec.get("error_verbatim"), rec["census_before"],
            rec["census_after"], rec["still_present"], rec.get("call_cost_s", 0.0)))
    return rec


def census_and_purge(path, nodes_before, tag, hints, keep_uids=()):
    """THE STEP THIS BUILD TURNS ON: after EVERY op call, diff the whole-VI Node census and purge the junk.

    A new node is DELETED only when it is an `Invoke` with ZERO wired terminals (the shape dispatch #4
    measured: six terminals, none wired, errs [0,0,0,1055]) and its uid is not one this build intends.
    Any other new node is REPORTED VERBATIM and left alone.
    """
    nodes_after, _ = node_census(path, "%s AFTER" % tag)
    fresh = new_nodes(nodes_before, nodes_after)
    rec = {"tag": tag, "node_count_before": len(nodes_before), "node_count_after": len(nodes_after),
           "new_uids": [(n["uid"], n["class"], n["pos"]) for n in fresh],
           "kept": list(keep_uids), "deleted": [], "reported_not_deleted": []}
    fact("%s CENSUS DIFF: Node %d -> %d ; %d new uid(s): %r"
         % (tag, len(nodes_before), len(nodes_after), len(fresh), rec["new_uids"]))
    for n in fresh:
        if n["uid"] in keep_uids:
            fact("%s new node #%s (%s) is INTENDED by this build - kept" % (tag, n["uid"], n["class"]))
            continue
        loc, rows = node_view(path, n["uid"], hints, "%s new #%s" % (tag, n["uid"]))
        wired = [t for t in rows if t.get("has_wire")]
        entry = {"uid": n["uid"], "class": n["class"], "pos": n["pos"],
                 "label": (loc.get("found") or {}).get("label"),
                 "diagram_index": (loc.get("found") or {}).get("diagram_index"),
                 "diagram_uid": (loc.get("found") or {}).get("diagram_uid"),
                 "terminals": rows, "n_terminals": len(rows), "n_wired": len(wired)}
        entry["terminal_table_was_actually_read"] = bool(rows)
        if n["class"] == "Invoke" and rows and not wired:
            entry["delete"] = delete_by_uid(path, "Node", n["uid"], "%s purge" % tag)
            rec["deleted"].append(entry)
            fact("%s PURGED junk %s #%s (label %r, %d terminals, %d wired) on Diagram idx %r"
                 % (tag, n["class"], n["uid"], entry["label"], entry["n_terminals"], entry["n_wired"],
                    entry["diagram_index"]))
        elif n["class"] == "Invoke" and not rows:
            # THE DEFECT THE FORCED REVIEW FOUND (archive/peer/2026-09-21-c64-astcheck-gate7-movein.md
            # section "Separate question"): `rows == []` also means THE TABLE COULD NOT BE READ - the locate
            # hit its budget, or node_labels/node_terms_uid raised and safe() swallowed it. Deleting then
            # would destroy an object never inspected, which is the exact failure this purge exists to
            # avoid. So: never delete an unread node. STOP instead and report.
            rec["reported_not_deleted"].append(entry)
            fact("%s AN `Invoke` NEW NODE #%s COULD NOT BE LOCATED OR READ (terminal table empty, loc %r) - "
                 "IT IS NOT DELETED. Deleting a node whose table was never read is the one branch that could "
                 "destroy the artefact." % (tag, n["uid"], loc.get("found")))
            stop_report("%s unreadable_junk_node" % tag,
                        "a new `Invoke` #%s appeared and its terminal table could not be read, so it was "
                        "NOT deleted and the build stops rather than guess" % (n["uid"],))
        else:
            rec["reported_not_deleted"].append(entry)
            fact("%s NEW NODE NOT DELETED (not the measured junk shape): #%s class %r label %r, %d "
                 "terminal(s), %d wired - REPORTED, left alone"
                 % (tag, n["uid"], n["class"], entry["label"], entry["n_terminals"], entry["n_wired"]))
    if rec["deleted"]:
        final, _ = node_census(path, "%s AFTER THE PURGE (the next step's baseline)" % tag)
    else:
        final = nodes_after
    rec["node_count_after_purge"] = len(final)
    R["purges"].append(rec)
    dump()
    return final, rec


def live_d639(tag):
    """RE-READ the Traverse 'Diagram' index of #639 off the machine. NEVER cached across a mutation."""
    v, err = safe("%s diag_index(#%d)" % (tag, D639), lambda: diag_index(WORK, D639))
    K.setdefault("d639_reresolved", []).append({"tag": tag, "value": v, "error_verbatim": err})
    fact("%s diag_index(#%d) RE-READ off the machine = %r%s"
         % (tag, D639, v, (" ; ERROR " + err) if err else ""))
    return v


def loop637(path, tag, hints):
    loc, rows = node_view(path, LOOP11_UID, hints, "%s #637" % tag)
    n_terms = len(rows)
    n_wired = sum(1 for r in rows if r.get("has_wire"))
    K.setdefault("loop637", []).append({"tag": tag, "n_terms": n_terms, "n_wired": n_wired,
                                        "found": loc.get("found")})
    fact("%s #637 (WhileLoop): %r terminals, %r WIRED" % (tag, n_terms, n_wired))
    return (n_terms, n_wired)


def panel_all(path, tag):
    rows, err = safe("%s panel_wiring" % tag, lambda: g.panel_wiring(path), [])
    fact("%s panel_wiring: %d rows%s" % (tag, len(rows or []), (" ; ERROR " + err) if err else ""))
    return rows or [], err


def close_quietly(path):
    safe("close_panel(%s)" % os.path.basename(path), lambda: g.close_panel(path))


# ============================================================ the donor call (OpCreateLocalRead_v0)
def donor_bool_label():
    """the op's direction control label, READ OFF THE MACHINE - never retyped."""
    fpl, err = safe("donor fp_labels", lambda: g.fp_labels(DONOR), [])
    cands = [t for (_i, t, ind) in (fpl or []) if (not ind) and t and "Write" in t]
    fact("OpCreateLocalRead_v0 front-panel labels READ OFF THE MACHINE: %r ; direction candidates %r"
         % (fpl, cands))
    return (cands[0] if len(cands) == 1 else None), (fpl or [])


def call_donor(target, fp_index, bool_label, tag):
    """OpCreateLocalRead_v0 in READ mode (Write? = False) bound to Panel.Controls[fp_index]."""
    rd = {"tag": tag, "fp_index": fp_index, "bool_label": bool_label, "write_flag": False}
    before, _ = safe("%s Local uids before" % tag,
                     lambda: {o["uid"] for o in g.report_all(target, "Local")}, set())
    rd["local_census_before"], _ = safe("%s count Local before" % tag, lambda: g.count(target, "Local"))
    vi = g.op(DONOR)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("index", int(fp_index))
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
    after, _ = safe("%s Local uids after" % tag,
                    lambda: {o["uid"] for o in g.report_all(target, "Local")}, set())
    rd["local_census_after"], _ = safe("%s count Local after" % tag, lambda: g.count(target, "Local"))
    rd["local_uids_added"] = sorted((after or set()) - (before or set()))
    K["donor_call"] = rd
    fact("%s OpCreateLocalRead_v0(Write?=False) on Panel.Controls[%r]: error cluster %s ; op walked to %r "
         "(indicator=%r) ; Local census %r -> %r ; new Local uid(s) %r"
         % (tag, fp_index, rd["error_cluster_verbatim"], rd.get("op_matched_label"),
            rd.get("op_is_indicator"), rd["local_census_before"], rd["local_census_after"],
            rd["local_uids_added"]))
    return rd


# ============================================================ the T3 separator (reverse census, read-only)
def t3_separator(target, wire_uid, d639, tag):
    """every terminal that carries `wire_uid`, from the TERMINAL side. No `Is Broken?` is read."""
    members, scanned = [], 0
    if isinstance(d639, int) and wire_uid:
        for i in range(T3_SCAN_LIMIT):
            try:
                u, tr = g.node_terms_uid(target, d639, i)
            except Exception:                                                      # noqa: BLE001
                break
            if not u:
                break
            scanned += 1
            for r in tr:
                if r["wire"] == wire_uid:
                    members.append({"where": "Diagram #639 Nodes[%d] = #%s" % (i, u), "node_uid": u,
                                    "terminal": r["i"], "name": r["name"], "is_source": r["is_source"]})
    prows, _e = panel_all(target, "%s T3" % tag)
    for r in prows:
        if r.get("wire") == wire_uid:
            members.append({"where": "panel control uid %s" % r.get("uid"), "node_uid": r.get("uid"),
                            "terminal": None, "name": r.get("label"), "is_source": r.get("is_source")})
    srcs = [m for m in members if m.get("is_source") is True]
    sinks = [m for m in members if m.get("is_source") is False]
    rec = {"wire": wire_uid, "nodes_scanned_on_639": scanned, "panel_rows_total": len(prows),
           "members": members, "source_count": len(srcs), "sources": srcs, "sinks": sinks}
    K["t3"] = rec
    fact("%s T3 SEPARATOR - the net of wire %r (%d nodes scanned on #639, %d panel rows): %r"
         % (tag, wire_uid, scanned, len(prows), members))
    fact("%s T3 SOURCES on that net: %d -> %r" % (tag, len(srcs), srcs))
    return rec


# ============================================================ the saves
def save_artefact(tag, dest):
    """g.save writes the WORKING copy in place; the artefact is a fresh path LabVIEW has never seen.

    A file byte-identical to the bed means THE IN-MEMORY EDITS DID NOT LAND. That is reported as a FAILURE,
    never as a pass (cycle 62's C_1 false pass).
    """
    rec = {"tag": tag, "dest": dest, "save_error_verbatim": ""}
    rec["exec_state_at_save"] = read_es("%s immediately before the save" % tag, WORK)
    try:
        rec["save_returned_size"] = g.save(WORK)
    except Exception as e:                                                         # noqa: BLE001
        rec["save_returned_size"] = None
        rec["save_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    try:
        shutil.copy2(WORK, dest)
        rec["copy_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["copy_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    ff = D.file_facts("%s the artefact" % tag, dest)
    rec.update({"exists": bool(ff.get("exists")), "md5": ff.get("md5"), "size": ff.get("size"),
                "version_candidates": ff.get("version_candidates")})
    rec["mtime"] = (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(dest)))
                    if rec["exists"] else None)
    rec["bytes_equal_to_the_bed"] = (ff.get("md5") == S3A_MD5)
    rec["carries_the_in_memory_edits"] = (bool(rec["exists"]) and not rec["save_error_verbatim"]
                                          and not rec["bytes_equal_to_the_bed"])
    R["artefacts_on_disk"].append(rec)
    fact("%s FILE ON DISK: %s  md5 %r  size %r  mtime %r  (ExecState at the save %r ; COM save error %r ; "
         "bytes equal to the bed %r ; carries the in-memory edits %r)"
         % (tag, dest, rec["md5"], rec["size"], rec["mtime"], rec["exec_state_at_save"],
            rec["save_error_verbatim"], rec["bytes_equal_to_the_bed"], rec["carries_the_in_memory_edits"]))
    gate("%s *** A FILE IS ON DISK at %s ***" % (tag, os.path.basename(dest)), bool(rec["exists"]),
         "md5 %r size %r mtime %r" % (rec["md5"], rec["size"], rec["mtime"]))
    gate("%s that file is NOT byte-identical to the bed (the in-memory edits LANDED)" % tag,
         bool(rec["exists"]) and not rec["bytes_equal_to_the_bed"] and not rec["save_error_verbatim"],
         "md5 %r vs bed %s ; save error %r" % (rec["md5"], S3A_MD5, rec["save_error_verbatim"]))
    dump()
    return rec


def stop_report(stage, why):
    """A step whose ExecState is not what the sequence expects STOPS the build. Files already saved STAY."""
    K["stopped_at"] = stage
    K["stopped_because"] = why
    fact("*** THE BUILD STOPS AT %s: %s ***" % (stage, why))
    read_es("at the stop", WORK)
    tables = K.setdefault("stop_report_tables", {})
    hints = [K.get("d639_last"), TOP]
    for label, uid in (("#10407 the sink", CASE_UID), ("#%d the source" % SRC_UID, SRC_UID),
                       ("the new Local", K.get("local_uid"))):
        if uid is None:
            continue
        _loc, rows = node_view(WORK, uid, hints, "STOP REPORT %s" % label)
        tables[label] = rows
    prows, _pe = panel_all(WORK, "STOP REPORT panel")
    tables["the indicator's panel row"] = [r for r in prows if r.get("uid") == OLD_CONTROL]
    fact("STOP REPORT - the indicator's panel row (control uid %d): %r"
         % (OLD_CONTROL, tables["the indicator's panel row"]))
    dump()
    raise Stop(why)


# ============================================================ THE BUILD - ROW 1 ONLY
def build_row1():
    print("\n========== ROW 1  sink #%d t%d  <-  source #%d t%d %r   (existing indicator %r, control uid %d)"
          % (CASE_UID, SINK_TERM, SRC_UID, SRC_TERM, SRC_TERM_NAME, OLD_LABEL, OLD_CONTROL), flush=True)
    K.update({"bed": os.path.basename(S3A_ARTEFACT), "working_copy": os.path.basename(WORK),
              "step7_artefact": os.path.basename(STEP7_PATH),
              "step9_artefact": os.path.basename(STEP9_PATH)})
    shutil.copy2(S3A_ARTEFACT, WORK)

    # ---------- [1] the cold reading and the baselines
    print("\n---------- [1] the cold reading and the baselines", flush=True)
    es0 = read_es("[1] the working copy, COLD (no open_panel call)", WORK)
    K["cold_exec_state"] = es0
    gate("A0 the working copy opens COLD at ExecState 1", es0 == 1, "%r" % (es0,), fatal=True)
    c0 = counts(WORK, "[1] baseline")
    K["counts_baseline"] = c0
    gate("A0b the baselines hold: Node %d / Wire %d / ControlTerminal %d / Local %d"
         % (NODE_BASE, WIRE_BASE, CT_BASE, LOCAL_BASE),
         c0.get("Node") == NODE_BASE and c0.get("Wire") == WIRE_BASE
         and c0.get("ControlTerminal") == CT_BASE and c0.get("Local") == LOCAL_BASE, "%r" % (c0,))
    nodes = node_census(WORK, "[1] baseline")[0]

    d639 = live_d639("[1]")
    K["d639_last"] = d639
    gate("A0c Diagram #%d resolves to a live Traverse index" % D639, isinstance(d639, int),
         "%r (the brief recorded 46)" % (d639,), fatal=True)
    hints = [d639, TOP]
    d686, _d6e = safe("[1] diag_index(#%d)" % SIBLING_DIAG_UID,
                      lambda: diag_index(WORK, SIBLING_DIAG_UID))
    K["d686_traverse_index"] = d686
    fact("[1] diag_index(#%d) (the diagram that holds #637) = %r" % (SIBLING_DIAG_UID, d686))
    loop_hints = [d686, TOP, d639]
    t637_0 = loop637(WORK, "[1] BEFORE", loop_hints)
    gate("A0d #637 baseline reads %r" % (LOOP637_BASELINE,), t637_0 == LOOP637_BASELINE, "%r" % (t637_0,))

    sink_loc, sink_rows = node_view(WORK, CASE_UID, hints, "[1] SINK #10407")
    K["sink_before"] = {"found": sink_loc.get("found"), "terminals": sink_rows}
    sink_i = (sink_loc.get("found") or {}).get("nodes_index")
    st0 = next((t for t in sink_rows if t["i"] == SINK_TERM), {})
    src_loc, src_rows = node_view(WORK, SRC_UID, hints, "[1] SOURCE #10686")
    K["source_before"] = {"found": src_loc.get("found"), "terminals": src_rows}
    src_i = (src_loc.get("found") or {}).get("nodes_index")
    sr0 = next((t for t in src_rows if t["i"] == SRC_TERM), {})
    gate("A1 #%d at Nodes[%d] and #%d at Nodes[%d] on Diagram #%d, each echoing its own uid"
         % (CASE_UID, EXPECT_SINK_IDX, SRC_UID, EXPECT_SRC_IDX, D639),
         sink_i == EXPECT_SINK_IDX and src_i == EXPECT_SRC_IDX
         and sink_loc.get("uid_echo") == CASE_UID and src_loc.get("uid_echo") == SRC_UID,
         "sink Nodes[%r] echo %r ; source Nodes[%r] echo %r"
         % (sink_i, sink_loc.get("uid_echo"), src_i, src_loc.get("uid_echo")), fatal=True)
    gate("A1b #%d t%d carries wire %d (the wire this row replaces)" % (CASE_UID, SINK_TERM, WIRE_PIN),
         st0.get("wire") == WIRE_PIN, "%r" % (st0,), fatal=True)
    src_name_live = sr0.get("name")
    K["source_terminal_name_read_off_the_machine"] = src_name_live
    gate("A1c the source terminal's NAME reads off the machine as %r" % SRC_TERM_NAME,
         src_name_live == SRC_TERM_NAME, "%r (hex %r)" % (src_name_live, sr0.get("name_hex")))

    fp0, _e0 = panel_all(WORK, "[1] BEFORE")
    K["panel_rows_before"] = len(fp0)
    prow = next((r for r in fp0 if r.get("uid") == OLD_CONTROL), None)
    K["existing_indicator_panel_row"] = prow
    live_label = (prow or {}).get("label")
    K["existing_indicator_label_read_off_the_machine"] = live_label
    K["existing_indicator_label_hex"] = (live_label or "").encode("utf-8").hex()
    fpl, _fe = safe("[1] fp_labels", lambda: g.fp_labels(WORK), [])
    hitsfp = [(i, t, ind) for (i, t, ind) in (fpl or []) if t == live_label]
    K["existing_indicator_fp_rows"] = hitsfp
    fact("the EXISTING indicator (control uid %d): panel row %r ; label READ OFF THE MACHINE %r (hex %r) ; "
         "front-panel rows carrying that label: %r"
         % (OLD_CONTROL, prow, live_label, K["existing_indicator_label_hex"], hitsfp))
    gate("A1d the EXISTING indicator is found by its own control uid and EXACTLY ONE front-panel row "
         "carries its label", bool(live_label) and len(hitsfp) == 1,
         "label %r rows %r (recorded %r)" % (live_label, hitsfp, OLD_LABEL), fatal=True)
    gate("A1e that front-panel row index is %d and the label equals the recorded one"
         % FP_ROW_EXPECT,
         hitsfp[0][0] == FP_ROW_EXPECT and live_label == OLD_LABEL,
         "row %r ; live label %r vs recorded %r" % (hitsfp[0][0], live_label, OLD_LABEL))

    # ---------- [2] delete the whole Wire object (ExecState 0 is EXPECTED here)
    print("\n---------- [2] delete Wire %d by uid - ExecState 0 is EXPECTED (unwired Case selector)"
          % WIRE_PIN, flush=True)
    dw = delete_by_uid(WORK, "Wire", WIRE_PIN, "[2]")
    K["wire_delete"] = dw
    gate("B the delete removed EXACTLY wire uid %d" % WIRE_PIN, dw.get("gone") == [WIRE_PIN],
         "gone %r ; error %r" % (dw.get("gone"), dw.get("error_verbatim")), fatal=True)
    es2 = read_es("[2] after the wire delete (0 is EXPECTED)", WORK)
    K["exec_state_after_wire_delete"] = es2
    gate("B2 ExecState after the delete is 0, as the sequence expects", es2 == 0, "%r" % (es2,))
    nodes, _p2 = census_and_purge(WORK, nodes, "[2] wire delete", hints)
    K["counts_after_wire_delete"] = counts(WORK, "[2] after")

    # ---------- [3] the Local, READ mode, bound to the EXISTING indicator
    print("\n---------- [3] OpCreateLocalRead_v0 (Write? = False = READ) bound to the EXISTING indicator",
          flush=True)
    bool_label, _dfpl = donor_bool_label()
    K["donor_direction_control_label"] = bool_label
    if not gate("C0 the donor's direction control was identified on the machine", bool(bool_label),
                "%r" % (bool_label,)):
        stop_report("C0_donor_label", "the donor's Write? control could not be identified")
    rd = call_donor(WORK, hitsfp[0][0], bool_label, "[3]")
    gate("C the Local census went %r -> %r (want %d)"
         % (rd["local_census_before"], rd["local_census_after"], LOCAL_BASE + 1),
         rd["local_census_after"] == LOCAL_BASE + 1 and len(rd["local_uids_added"]) == 1,
         "added %r" % (rd["local_uids_added"],))
    if len(rd["local_uids_added"]) != 1:
        stop_report("C_local", "the donor added %r Locals" % (len(rd["local_uids_added"]),))
    local_uid = rd["local_uids_added"][0]
    K["local_uid"] = local_uid
    read_es("[3] after the Local was created (still unwired)", WORK)
    lloc, lrows = node_view(WORK, local_uid, [TOP, d639], "[3] the new Local BEFORE move_in")
    K["local_before_move_in"] = {"found": lloc.get("found"), "terminals": lrows}
    one = lrows[0] if len(lrows) == 1 else {}
    fact("LOCAL READBACK VERBATIM (before move_in): Local #%s -> %d terminal(s); NAME %r (hex %r), "
         "is_source %r, wire %r ; lives at %r"
         % (local_uid, len(lrows), one.get("name"), one.get("name_hex"), one.get("is_source"),
            one.get("wire"), lloc.get("found")))
    gate("C2 RULE-1a GATE (50(i)): ONE terminal, NAME == the label read off the machine, is_source True "
         "(= READ)",
         len(lrows) == 1 and one.get("name") == live_label and one.get("is_source") is True,
         "name %r (hex %r) vs label %r (hex %r) ; is_source %r"
         % (one.get("name"), one.get("name_hex"), live_label, K["existing_indicator_label_hex"],
            one.get("is_source")))
    local_term_i = one.get("i", 0)
    nodes, _p3 = census_and_purge(WORK, nodes, "[3] donor", [TOP, d639], keep_uids=(local_uid,))
    c3 = counts(WORK, "[3] after the donor and its purge")
    K["counts_after_donor"] = c3
    # MEASURED, NEVER ASSUMED: whether a Local is counted inside the Traverse 'Node' class. The whole-VI
    # Node expectation for the rest of the build is this reading, not the 630 baseline plus a guess.
    R["node_expected_with_the_local"] = c3.get("Node")
    fact("[3] the whole-VI Node census with the new Local present = %r (baseline was %d; the difference IS "
         "the answer to 'does a Local count as a Node', measured not assumed)"
         % (c3.get("Node"), NODE_BASE))

    # ---------- [4] move_in the Local onto Diagram #639
    print("\n---------- [4] move_in the new Local onto Diagram #%d" % D639, flush=True)
    d639 = live_d639("[4] before move_in")
    K["d639_last"] = d639
    mv_ret, mv_err = None, "NOT ATTEMPTED: diag_index(#639) did not resolve (%r)" % (d639,)
    if isinstance(d639, int):
        try:
            mv_ret = move_in(WORK, local_uid, d639, MOVE_POSITION)
            mv_err = ""
        except Exception as e:                                                     # noqa: BLE001
            mv_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    K["move_in_call"] = {"call": "move_in(target, %r, %r, %r)  # build_d1_v0.py:318"
                                 % (local_uid, d639, MOVE_POSITION),
                         "returned": mv_ret, "error_verbatim": mv_err}
    fact("[4] move_in(Local #%r -> Diagram #%d at LIVE Traverse index %r, position %r) returned %r ; "
         "error VERBATIM %r" % (local_uid, D639, d639, MOVE_POSITION, mv_ret, mv_err))
    gate("D0 move_in returned without raising", mv_err == "", "returned %r ; error %r" % (mv_ret, mv_err))
    nodes, _p4 = census_and_purge(WORK, nodes, "[4] move_in", [d639, TOP], keep_uids=(local_uid,))
    lloc2, lrows2 = node_view(WORK, local_uid, [d639, TOP], "[4] the Local AFTER move_in")
    K["local_after_move_in"] = {"found": lloc2.get("found"), "terminals": lrows2}
    found2 = lloc2.get("found") or {}
    one2 = lrows2[0] if len(lrows2) == 1 else {}
    es4 = read_es("[4] after move_in and its purge", WORK)
    K["exec_state_after_move_in"] = es4
    gate("D *** move_in leaves the Local owned by Diagram #%d ***" % D639,
         found2.get("diagram_uid") == D639
         and found2.get("diagram_class") in ("Diagram", "TopLevelDiagram"),
         "lives at %r ; ExecState %r" % (found2, es4))
    if found2.get("nodes_index") is None:
        stop_report("D_placement", "the Local is not addressable in Diagram.Nodes[] after move_in")
    gate("D2 RULE-1a GATE RE-READ AFTER move_in: ONE terminal, NAME == %r, is_source True (= READ)"
         % (live_label,),
         len(lrows2) == 1 and one2.get("name") == live_label and one2.get("is_source") is True,
         "name %r (hex %r) ; is_source %r  [before the move: name %r is_source %r]"
         % (one2.get("name"), one2.get("name_hex"), one2.get("is_source"), one.get("name"),
            one.get("is_source")))
    local_term_i = one2.get("i", local_term_i)
    K["local_term_index"] = local_term_i
    cmv = counts(WORK, "[4] after move_in")
    K["counts_after_move_in"] = cmv
    gate("D3 the Local census is STILL %d after move_in (the move duplicated nothing)" % (LOCAL_BASE + 1,),
         cmv.get("Local") == LOCAL_BASE + 1, "%r" % (cmv,))

    # ---------- [5] the connect - both ends now on Diagram #639
    print("\n---------- [5] connect_nested_v1: the Local's SOURCE into the freed #%d sink" % CASE_UID,
          flush=True)
    d639 = live_d639("[5] before the connect")
    K["d639_last"] = d639
    sloc, _sr = node_view(WORK, CASE_UID, [d639, TOP], "[5] #10407 before the connect")
    sink_i = (sloc.get("found") or {}).get("nodes_index")
    lloc3 = find_node(WORK, local_uid, [d639, TOP], "[5] the Local before the connect")
    src_node_i = (lloc3.get("found") or {}).get("nodes_index")
    src_diag = (lloc3.get("found") or {}).get("diagram_index")
    K["connect_call"] = ("connect_nested_v1(target, sink_diag=%r, sink_node=%r, sink_term=%r, src_diag=%r, "
                         "src_node=%r, src_term=%r)"
                         % (d639, sink_i, SINK_TERM, src_diag, src_node_i, local_term_i))
    fact("[5] CONNECT: %s   (SAME diagram on both sides: %r == %r)" % (K["connect_call"], d639, src_diag))
    if sink_i is None or src_node_i is None or src_diag is None:
        stop_report("E_address", "the sink or the Local is not addressable before the connect")
    wire_before, _wb = safe("[5] count Wire before", lambda: g.count(WORK, "Wire"))
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            cdw, ces, cerr = CONNECT_V1(WORK, d639, sink_i, SINK_TERM, src_diag, src_node_i,
                                        local_term_i, V1_LABELS)
        K["connect_result"] = {"wire_delta": cdw, "exec_state_returned": ces, "op_error": cerr,
                               "error_verbatim": ""}
    except Exception as e:                                                         # noqa: BLE001
        K["connect_result"] = {"wire_delta": None, "exec_state_returned": None, "op_error": None,
                               "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])}
    K["connect_op_stdout_verbatim"] = [ln.strip() for ln in buf.getvalue().rstrip().splitlines()]
    for ln in K["connect_op_stdout_verbatim"]:
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    fact("[5] connect result: %r" % (K["connect_result"],))
    wire_after, _wa = safe("[5] count Wire after", lambda: g.count(WORK, "Wire"))
    K["wire_census_across_the_connect"] = [wire_before, wire_after]
    gate("E wire_delta == 1 (a NEW wire was made)", K["connect_result"].get("wire_delta") == 1,
         "wire_delta %r ; Wire census %r -> %r" % (K["connect_result"].get("wire_delta"),
                                                   wire_before, wire_after))

    sloc2, srows2 = node_view(WORK, CASE_UID, [d639, TOP], "[5] #10407 AFTER the connect")
    K["sink_after_connect"] = {"found": sloc2.get("found"), "terminals": srows2}
    st0b = next((t for t in srows2 if t["i"] == SINK_TERM), {})
    lloc4, lrows4 = node_view(WORK, local_uid, [d639, TOP], "[5] the Local AFTER the connect")
    K["local_after_connect"] = {"found": lloc4.get("found"), "terminals": lrows4}
    l0b = next((t for t in lrows4 if t["i"] == local_term_i), (lrows4[0] if lrows4 else {}))
    K["sink_end_wire_uid"] = st0b.get("wire")
    K["local_end_wire_uid"] = l0b.get("wire")
    same_uid = bool(K["sink_end_wire_uid"]) and K["sink_end_wire_uid"] == K["local_end_wire_uid"]
    K["both_ends_same_wire_uid"] = same_uid
    fact("[5] #%d t%d wire uid %r  |  the Local #%s t%r %r wire uid %r  ->  SAME uid: %r"
         % (CASE_UID, SINK_TERM, K["sink_end_wire_uid"], local_uid, l0b.get("i"), l0b.get("name"),
            K["local_end_wire_uid"], same_uid))
    gate("E2 *** ONE wire uid at BOTH ends (a same-diagram wire, no tunnel) ***", same_uid,
         "sink %r vs local %r" % (K["sink_end_wire_uid"], K["local_end_wire_uid"]))
    t637_1 = loop637(WORK, "[5] AFTER THE CONNECT", loop_hints)
    gate("E3 *** #637 is back at the %r baseline immediately after the connect (50(e): no tunnel, no "
         "border object) ***" % (LOOP637_BASELINE,), t637_1 == LOOP637_BASELINE,
         "%r -> %r" % (t637_0, t637_1))
    c5 = counts(WORK, "[5] after the connect")
    K["counts_after_connect"] = c5
    gate("E4 ControlTerminal is still %d and Local still %d after the connect" % (CT_BASE, LOCAL_BASE + 1),
         c5.get("ControlTerminal") == CT_BASE and c5.get("Local") == LOCAL_BASE + 1, "%r" % (c5,))
    es5a = read_es("[5] immediately after the connect, BEFORE the purge", WORK)
    K["exec_state_after_connect_before_purge"] = es5a

    # ---------- [6] THE PURGE
    print("\n---------- [6] the census diff and the purge of the op's junk node", flush=True)
    nodes, purge6 = census_and_purge(WORK, nodes, "[6] connect", [d639, TOP],
                                     keep_uids=(local_uid,))
    K["purge_after_connect"] = purge6
    gate("F the census diff isolated the junk node and it was deleted BY UID",
         len(purge6["deleted"]) == 1 and not purge6["reported_not_deleted"]
         and purge6["deleted"][0]["delete"].get("gone") == [purge6["deleted"][0]["uid"]],
         "deleted %r ; reported-not-deleted %r"
         % ([(d["uid"], d["class"], d["n_terminals"], d["n_wired"]) for d in purge6["deleted"]],
            [(d["uid"], d["class"], d["n_terminals"], d["n_wired"])
             for d in purge6["reported_not_deleted"]]))
    c6 = counts(WORK, "[6] after the purge")
    K["counts_after_purge"] = c6
    gate("F2 after the purge: Node %r (the reading taken with the Local present), Wire %d, "
         "ControlTerminal %d, Local %d"
         % (R.get("node_expected_with_the_local"), WIRE_BASE, CT_BASE, LOCAL_BASE + 1),
         c6.get("Node") == R.get("node_expected_with_the_local") and c6.get("Wire") == WIRE_BASE
         and c6.get("ControlTerminal") == CT_BASE and c6.get("Local") == LOCAL_BASE + 1, "%r" % (c6,))

    # ---------- [7] ExecState 1 is REQUIRED -> the first saved artefact
    es7 = read_es("[7] after the purge - 1 is REQUIRED here", WORK)
    K["exec_state_after_purge"] = es7
    if not gate("G *** ExecState == 1 after the purge (REQUIRED) ***", es7 == 1, "%r" % (es7,)):
        stop_report("G_execstate", "ExecState read %r after the purge, not 1 - nothing further is saved"
                    % (es7,))
    print("\n---------- [7] SAVE the row's guaranteed artefact", flush=True)
    sv7 = save_artefact("STEP7", STEP7_PATH)
    K["step7_save"] = sv7

    # ---------- [8] wire_indicators re-feeds that SAME existing indicator
    print("\n---------- [8] wire_indicators re-feeds the EXISTING indicator %r" % live_label, flush=True)
    d639 = live_d639("[8] before wire_indicators")
    K["d639_last"] = d639
    fidx, ferr = safe("[8] report_all('Function')",
                      lambda: [o["uid"] for o in g.report_all(WORK, "Function")], [])
    fn_index = (fidx.index(SRC_UID) if (fidx and SRC_UID in fidx) else None)
    K["source_function_index_read_off_the_machine"] = fn_index
    K["source_function_index_error"] = ferr
    fact("[8] the source #%d in the Traverse 'Function' list: index %r (the brief recorded %d)"
         % (SRC_UID, fn_index, SRC_FUNCTION_INDEX_EXPECT))
    gate("H0 the source's live 'Function' Traverse index is %d" % SRC_FUNCTION_INDEX_EXPECT,
         fn_index == SRC_FUNCTION_INDEX_EXPECT, "%r" % (fn_index,))
    K["wire_indicators_call"] = ("g.wire_indicators(target, node_index=%r, src_terms=[%r], "
                                 "indicator_names=[%r], diagram_index=%r, node_class='Function')"
                                 % (fn_index, src_name_live, live_label, d639))
    fact("[8] CALL: %s" % K["wire_indicators_call"])
    if not isinstance(fn_index, int) or not isinstance(d639, int):
        K["wire_indicators_returned"] = None
        K["wire_indicators_error_verbatim"] = ("NOT ATTEMPTED: function index %r, d639 %r"
                                               % (fn_index, d639))
        fact("[8] %s" % K["wire_indicators_error_verbatim"])
    else:
        try:
            K["wire_indicators_returned"] = g.wire_indicators(WORK, fn_index, [src_name_live],
                                                              [live_label], diagram_index=d639,
                                                              node_class="Function")
            K["wire_indicators_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            K["wire_indicators_returned"] = None
            K["wire_indicators_error_verbatim"] = "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:500])
    fact("[8] wire_indicators returned %r ; raised %r  -- a raise here is a READING, not a verdict: the "
         "wrapper tests exec_state ABSOLUTELY (gscript.py:1794-1797), a MEASURED defect NOT repaired here"
         % (K["wire_indicators_returned"], K["wire_indicators_error_verbatim"]))
    es8 = read_es("[8] after wire_indicators", WORK)
    K["exec_state_after_wire_indicators"] = es8
    nodes, purge8 = census_and_purge(WORK, nodes, "[8] wire_indicators", [d639, TOP],
                                     keep_uids=(local_uid,))
    K["purge_after_wire_indicators"] = purge8

    sloc3, srows3 = node_view(WORK, SRC_UID, [d639, TOP], "[8] the source AFTER wire_indicators")
    K["source_after_wire_indicators"] = {"found": sloc3.get("found"), "terminals": srows3}
    sr3 = next((t for t in srows3 if t["i"] == SRC_TERM), {})
    IND_W = sr3.get("wire")
    K["indicator_wire_uid_read_off_the_machine"] = IND_W
    gate("H wire_indicators left a NON-ZERO wire on the source #%d t%d" % (SRC_UID, SRC_TERM),
         bool(IND_W), "wire %r ; row %r" % (IND_W, sr3))
    t3 = t3_separator(WORK, IND_W, d639, "[8]")
    sink_uids = [m.get("node_uid") for m in t3.get("sinks", [])]
    gate("I *** THE T3 SEPARATOR: EXACTLY ONE source on wire %r, and control %d is among its sinks ***"
         % (IND_W, OLD_CONTROL),
         t3.get("source_count") == 1 and OLD_CONTROL in sink_uids,
         "sources %r -> %r ; sinks %r" % (t3.get("source_count"), t3.get("sources"), sink_uids))
    t637_2 = loop637(WORK, "[8] AFTER wire_indicators", loop_hints)
    gate("I2 #637 is still at the %r baseline after wire_indicators" % (LOOP637_BASELINE,),
         t637_2 == LOOP637_BASELINE, "%r" % (t637_2,))
    c8 = counts(WORK, "[8] after wire_indicators")
    K["counts_after_wire_indicators"] = c8
    fp2, _e2 = panel_all(WORK, "[8] AFTER")
    K["panel_rows_after"] = len(fp2)
    gate("I3 ControlTerminal is still %d and the panel row count is unchanged" % CT_BASE,
         c8.get("ControlTerminal") == CT_BASE and len(fp2) == K["panel_rows_before"],
         "%r ; panel rows %r -> %r" % (c8, K["panel_rows_before"], len(fp2)))

    # ---------- [9] ExecState 1 -> the final artefact
    es9 = read_es("[9] before the final save - 1 is REQUIRED here", WORK)
    K["exec_state_before_final_save"] = es9
    if not gate("J *** ExecState == 1 after wire_indicators (REQUIRED) ***", es9 == 1, "%r" % (es9,)):
        stop_report("J_execstate", "ExecState read %r after wire_indicators, not 1 - the step-7 artefact "
                                   "stays saved, nothing further is written" % (es9,))
    print("\n---------- [9] SAVE the final row-1 artefact", flush=True)
    sv9 = save_artefact("STEP9", STEP9_PATH)
    K["step9_save"] = sv9
    gate("J2 the two artefacts differ from each other (the wire_indicators step changed the file)",
         bool(sv9.get("md5")) and sv9.get("md5") != sv7.get("md5"),
         "step7 %r vs step9 %r" % (sv7.get("md5"), sv9.get("md5")))
    return STEP9_PATH


# ============================================================ the ORDERED `Is Broken?` pass (42(b)) - LAST
def ordered_pass(target):
    P = K.setdefault("ordered_pass", {})
    P["target"] = target
    P["note"] = ("LAST, after the cold reopen only (42(b), 52(f)). NOTHING is saved after this point; "
                 "the in-memory VI is discarded. The idempotent re-connect is how the op's `Is Broken?` "
                 "indicator is made to answer about the EXISTING wire.")
    d639, derr = safe("[11] diag_index(#639) on the reopened file", lambda: diag_index(target, D639))
    P["d639"] = d639
    P["d639_error"] = derr
    sloc = find_node(target, CASE_UID, [d639, TOP], "[11] #10407")
    lloc = find_node(target, K.get("local_uid"), [d639, TOP], "[11] the Local")
    sink_i = (sloc.get("found") or {}).get("nodes_index")
    src_i = (lloc.get("found") or {}).get("nodes_index")
    src_d = (lloc.get("found") or {}).get("diagram_index")
    lt = terms_at(target, src_d, src_i, K.get("local_uid"), "[11] the Local") if src_i is not None else {}
    term_i = (lt.get("terminals") or [{}])[0].get("i", 0)
    P["call"] = ("connect_nested_v1(target, %r, %r, %r, %r, %r, %r) - IDEMPOTENT re-connect of an EXISTING "
                 "connection; wire_delta must be 0" % (d639, sink_i, SINK_TERM, src_d, src_i, term_i))
    fact(P["call"])
    if sink_i is None or src_i is None:
        P["not_attempted_because"] = "the sink or the Local is not addressable on the reopened file"
        gate("L the ORDERED `Is Broken?` reads False on the new #10407 t0 wire", False,
             "NOT ATTEMPTED: %s" % P["not_attempted_because"])
        return
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            odw, oes, oerr = CONNECT_V1(target, d639, sink_i, SINK_TERM, src_d, src_i, term_i, V1_LABELS)
        P.update({"wire_delta": odw, "exec_state_returned": oes, "op_error": oerr, "error_verbatim": ""})
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
    fact("ORDERED `Is Broken?` = %r on wire uid %r (wire_delta %r - expected 0 ; op error %r)"
         % (ib, rd.get("UID 2"), P.get("wire_delta"), P.get("error_verbatim")))
    gate("L the ORDERED `Is Broken?` reads False on the new #%d t%d wire" % (CASE_UID, SINK_TERM),
         ib is False, "Is Broken? %r on wire %r ; wire_delta %r"
         % (ib, rd.get("UID 2"), P.get("wire_delta")))
    read_es("[11] after the Is Broken? read (SUSPECT, NAMES.md:912-918; every save is already done)",
            target)


# ============================================================ MAIN
def main():
    print("=== diag_c64_s3b_row1  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== cycle 64 material #5: THE DELIVERABLE BUILD - S3b ROW 1 ONLY, staged saves, a node census "
          "diff and a junk purge after EVERY op call. ROW 2 IS NOT IN THIS RUN.", flush=True)
    print("=== NO g.open_panel and NO g.ensure_loaded call appears in this file; the edits reach the load "
          "only inside the wrappers. VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)).", flush=True)

    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])
    R["ref_counts_before"] = g.ref_counts()
    fact("tracked VI Server refs BEFORE: %r" % (R["ref_counts_before"],))

    o = probe("Z0 ORIGINAL (read-only probe)", ORIGINAL)
    gate("Z_0 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("Z0b D1_s1_copy.vi", S1_ARTEFACT)
    gate("Z_0b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("Z0c D1_s2_loops.vi", S2_ARTEFACT)
    gate("Z_0c D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("Z0d D1_s3a_focus_ind.vi (the BED, FATAL pin, never written)", S3A_ARTEFACT)
    gate("Z_0d D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    dn = probe("Z0e the donor OpCreateLocalRead_v0.vi", DONOR)
    gate("Z_0e OpCreateLocalRead_v0.vi md5 == %s" % DONOR_MD5, dn.get("md5") == DONOR_MD5,
         dn.get("md5", "?"))
    v1 = probe("Z0f OpConnectNested_v1.vi", OP_V1)
    R["op_v1_md5_before"] = v1.get("md5")
    gate("Z_0f OpConnectNested_v1.vi md5 starts with %s" % OP_V1_MD5_PREFIX,
         str(v1.get("md5", "")).startswith(OP_V1_MD5_PREFIX), v1.get("md5", "?"))
    gate("Z_0g neither artefact path exists before this run",
         not os.path.exists(STEP7_PATH) and not os.path.exists(STEP9_PATH)
         and not os.path.exists(WORK),
         "%s / %s / %s" % (os.path.basename(STEP7_PATH), os.path.basename(STEP9_PATH),
                           os.path.basename(WORK)))

    D.fresh("Z_R RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    final = None
    try:
        final = build_row1()
    except Stop as s:
        fact("THE BUILD STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        K["raised_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("THE BUILD RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
        try:
            stop_report("raise", "an exception escaped the build: %s" % (str(e)[:200],))
        except Stop:
            pass
        except Exception as e2:                                                    # noqa: BLE001
            fact("the stop report itself raised %s: %s" % (type(e2).__name__, str(e2)[:300]))
    dump()

    close_quietly(WORK)
    if os.path.exists(WORK):
        try:
            os.remove(WORK)
        except Exception as e:                                                     # noqa: BLE001
            fact("could not remove the working copy: %s" % (e,))
    K["working_copy_removed"] = not os.path.exists(WORK)
    gate("Z_2 the working copy is removed in the same run", K["working_copy_removed"],
         os.path.basename(WORK))

    saved = [a for a in R["artefacts_on_disk"] if a.get("exists")]
    if final is None:
        final = saved[-1]["dest"] if saved else None
    R["final_file"] = final
    fact("THE FILES THIS RUN LEFT ON DISK: %r"
         % ([(os.path.basename(a["dest"]), a.get("md5"), a.get("size")) for a in saved],))

    # ---------- [10] the COLD reopen in a freshly restarted LabVIEW
    print("\n========== [10] RESTART, then COLD-open the final artefact", flush=True)
    if final and os.path.exists(final):
        D.fresh("[10] RESTART before the cold reopen")
        R["handles"]["after_cold_restart"] = labview_handles()
        es_cold = read_es("[10] COLD, freshly restarted LabVIEW, %s" % os.path.basename(final), final)
        R["cold_exec_state"] = es_cold
        gate("K *** THE COLD READING of %s: ExecState 1 is the artefact's pass criterion ***"
             % os.path.basename(final), es_cold == 1, "ExecState %r" % (es_cold,))
        cf = probe("[10] the final artefact, re-read", final)
        R["cold_md5"] = cf.get("md5")
        cc = counts(final, "[10] COLD")
        R["cold_counts"] = cc
        gate("K2 the COLD censuses: Node %r (the in-memory reading with the Local present), Wire %d, "
             "ControlTerminal %d, Local %d"
             % (R.get("node_expected_with_the_local"), WIRE_BASE, CT_BASE, LOCAL_BASE + 1),
             cc.get("Node") == R.get("node_expected_with_the_local") and cc.get("Wire") == WIRE_BASE
             and cc.get("ControlTerminal") == CT_BASE and cc.get("Local") == LOCAL_BASE + 1,
             "%r" % (cc,))
        cd639, _ce = safe("[10] diag_index(#639) COLD", lambda: diag_index(final, D639))
        cloc, crows = node_view(final, CASE_UID, [cd639, TOP], "[10] COLD #10407")
        ct0 = next((t for t in crows if t["i"] == SINK_TERM), {})
        R["cold_sink_t0"] = ct0
        lloc_c, lrows_c = (node_view(final, K.get("local_uid"), [cd639, TOP], "[10] COLD the Local")
                           if K.get("local_uid") else ({}, []))
        far = lrows_c[0] if lrows_c else {}
        R["cold_far_end"] = {"local_uid": K.get("local_uid"), "found": (lloc_c or {}).get("found"),
                             "terminal": far}
        gate("K3 COLD: #%d t%d carries a wire and the SAME uid appears on the Local (the far end)"
             % (CASE_UID, SINK_TERM),
             bool(ct0.get("wire")) and ct0.get("wire") == far.get("wire"),
             "sink t0 %r ; far end (Local #%r, %r) %r"
             % (ct0, K.get("local_uid"), (lloc_c or {}).get("found"), far))
        print("\n========== [11] the ORDERED `Wire.Is Broken?` pass (42(b), 52(f)) - LAST, nothing is "
              "saved after this point", flush=True)
        ordered_pass(final)
        close_quietly(final)
    else:
        gate("K *** THE COLD READING ***", False, "NOT REACHED: no artefact on disk")
        gate("L the ORDERED `Is Broken?` reads False on the new #10407 t0 wire", False,
             "NOT REACHED: no artefact on disk")
    dump()

    print("\n--- Z: the closing facts", flush=True)
    R["ref_counts"] = g.ref_counts()
    fact("tracked VI Server refs AFTER: %r" % (R["ref_counts"],))
    safe("g.reset", g.reset)
    R["handles"]["after"] = labview_handles()
    fact("LabVIEW handles AFTER everything: %r" % R["handles"]["after"])

    zo = probe("Z1 ORIGINAL after everything", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after everything", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after everything", S2_ARTEFACT)
    z3 = probe("Z1d D1_s3a_focus_ind.vi after everything", S3A_ARTEFACT)
    z4 = probe("Z1e the donor OpCreateLocalRead_v0.vi after everything", DONOR)
    z5 = probe("Z1f OpConnectNested_v1.vi after everything", OP_V1)
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    gate("Z_1b OpCreateLocalRead_v0.vi is byte-unchanged", z4.get("md5") == DONOR_MD5, "%s" % (z4.get("md5"),))
    gate("Z_1c OpConnectNested_v1.vi is byte-unchanged", z5.get("md5") == R.get("op_v1_md5_before"),
         "%r -> %r" % (R.get("op_v1_md5_before"), z5.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z_1d refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))

    print("\n=== THE COMPLETE TIMESTAMPED ExecState TIMELINE", flush=True)
    print("  %-4s %-72s %-12s %-10s" % ("step", "tag", "ExecState", "wall"), flush=True)
    for row in R["exec_state_timeline"]:
        print(("  %-4d %-72s %-12r %-10s" % (row["step"], row["tag"][:72], row["exec_state"],
                                             row["wall_clock"]))
              .encode("ascii", "replace").decode("ascii"), flush=True)

    print("\n=== THE FILES THIS RUN LEFT ON DISK", flush=True)
    for a in R["artefacts_on_disk"]:
        print(("  %-10s %-46s md5 %r  size %r  mtime %r  ES-at-save %r  carries the edits %r"
               % (a["tag"], os.path.basename(a["dest"]), a.get("md5"), a.get("size"), a.get("mtime"),
                  a.get("exec_state_at_save"), a.get("carries_the_in_memory_edits")))
              .encode("ascii", "replace").decode("ascii"), flush=True)

    print("\n=== THE PURGES (one census diff per op call)", flush=True)
    for p in R["purges"]:
        print(("  %-22s Node %r -> %r -> %r ; new %r ; deleted %r ; reported-not-deleted %r"
               % (p["tag"], p["node_count_before"], p["node_count_after"], p["node_count_after_purge"],
                  p["new_uids"], [d["uid"] for d in p["deleted"]],
                  [d["uid"] for d in p["reported_not_deleted"]]))
              .encode("ascii", "replace").decode("ascii"), flush=True)

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
