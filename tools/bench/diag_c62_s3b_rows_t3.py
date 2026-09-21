"""diag_c62_s3b_rows_t3 - the ONE discriminating test the forced hypothesis review named. PURE MEASUREMENT.

WHY THIS EXISTS (it is not a retry of diag_c62_s3b_rows and it builds nothing)
  diag_c62_s3b_rows.log:76-84 showed that `wire_indicators` called on a BARE source DID make a wire:
  `#10686` t0 0 -> 23499 and the old panel indicator's row 0 -> 23499, while the wrapper RAISED because
  gscript.py:1794 tests `exec_state != 1` ABSOLUTELY and `ExecState` was already 0 (the Case selector
  `#10407` t0 was bare at that moment). Two readings survive that log and it cannot separate them:
    H_good  23499 is a proper source -> indicator wire and the bare selector alone explains ExecState 0
    H_bad   23499 is a TWO-SOURCE wire ("connects more than one data source", gscript.py:1765-1767,
            docs/NAMES.md:935-936)
  archive/peer/2026-09-21-c62-row1-precond.md (claude/hypothesis, opus max, ANSWERED 402s) names the
  separator, T3: reproduce the leg and, BEFORE any save and WITHOUT touching `Is Broken?`, enumerate every
  terminal carrying that wire and count how many report `is_source` True. Exactly one => H_bad is dead.
  It also asks (T2) whether "the TOP-LEVEL diagram lists 0 nodes" is real or a reader artefact; that is two
  extra read-only calls and they are made here.

WHAT THIS IS NOT
  Nothing is built, nothing is saved (`save` never called), no op, no new `gscript` verb, no edit to
  tools/gscript.py, no recipe, no VI run (34(f)), no GUI action, no motor / ASI / camera (rig 조립), no new
  process device. `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` neither imported nor called;
  `allow_broken` never True; `move_in` neither imported nor called. **No `Wire.Is Broken?` is read anywhere**
  (52(f) / docs/NAMES.md:912-918). ONE throwaway scratch duplicate of claudeDev\\D1_s3a_focus_ind.vi, deleted
  in the same run (49(e)). NO ROUTE IS CHOSEN OR RECOMMENDED; docs/cycle27-plan.md and `## NEXT` untouched.

PREDICTION CONTRACT
  T_*  four md5 pins BEFORE (ORIGINAL FATAL, s1, s2 FATAL, s3a FATAL)
  P_1  the scratch opens COLD at ExecState 1 and `#10686` t0 carries wire 10799
  P_2  T2: len(node_labels(top)) , len(node_info) and count('Node') are all reported side by side
  P_3  the delete removes exactly 10799 and bares `#10686` t0
  P_4  wire_indicators leaves a NON-ZERO wire on `#10686` t0 (the uid is read off the machine)
  P_5  *** THE SEPARATOR: exactly ONE terminal on that wire reports is_source True ***
  Z_*  four md5 pins PASS after; the scratch exists=False; refs/handles reported
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

ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_c62_s3b_rows_t3.json")
CASE_UID, D639, D536 = 10407, 639, 536
SRC_UID, SRC_TERM, SRC_NAME = 10686, 0, "x .and. y?"
OLD_LABEL, OLD_CONTROL = "Automatic Error Handling", 23555
WIRE_PIN = 10799
SCAN_LIMIT = 120

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "T3 from archive/peer/2026-09-21-c62-row1-precond.md: how many SOURCES sit on the wire that "
             "wire_indicators made from a bare source? PURE MEASUREMENT.",
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "nothing_saved": True, "gscript_not_edited": True, "is_broken_read_anywhere": False,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's normal mechanism",
     "no_gui_action": True,
     "rig_state": "조립 / ASSEMBLED - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True, "edits_no_plan_document": True,
     "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "gui_save": "NEVER called", "allow_broken": "NEVER True", "move_in": "not imported, not called",
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "leg": {}}


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        raise RuntimeError(name)
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


def read_exec_state(tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    R["exec_state_timeline"].append({"step": len(R["exec_state_timeline"]) + 1, "tag": tag, "value": es})
    fact("ExecState [%d %s] = %r" % (len(R["exec_state_timeline"]), tag, es))
    return es


def term_rows(terms):
    return [{"i": t["i"], "name": t["name"], "is_source": t["is_source"], "wire": t["wire"],
             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]} for t in terms]


def node_table(target, uid, tag):
    loc = {"uid": uid}
    for strict in (True, False):
        try:
            cls, ouid = owner_of(target, uid, strict=strict)
            loc.update({"owner_class": cls, "owner_uid": ouid})
            break
        except Exception as e:                                                     # noqa: BLE001
            loc.update({"owner_class": None, "owner_uid": None,
                        "owner_error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:200])})
    if loc.get("owner_class") not in ("Diagram", "TopLevelDiagram"):
        return [], loc
    try:
        loc["diagram_index"] = diag_index(target, loc["owner_uid"])
        rows_l = g.node_labels(target, int(loc["diagram_index"]))
    except Exception as e:                                                         # noqa: BLE001
        loc["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        return [], loc
    n = next((i for i, r in enumerate(rows_l) if r["uid"] == uid), None)
    loc["nodes_index"] = n
    loc["node_own_label"] = next((r["label"] for r in rows_l if r["uid"] == uid), None)
    rows = []
    if n is not None:
        try:
            u, tr = g.node_terms_uid(target, int(loc["diagram_index"]), n)
            loc["node_uid_echo"] = u
            rows = term_rows(tr) if u == uid else []
        except Exception as e:                                                     # noqa: BLE001
            loc["terms_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    fact("%s #%s: owner %r#%r diagram %r Nodes[%r] label %r ; TABLE %r"
         % (tag, uid, loc.get("owner_class"), loc.get("owner_uid"), loc.get("diagram_index"),
            loc.get("nodes_index"), loc.get("node_own_label"), rows))
    return rows, loc


def main():
    print("=== diag_c62_s3b_rows_t3  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== T3: how many SOURCES sit on the wire wire_indicators made from a BARE source?", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 unchanged", s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 D1_s2_loops.vi", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 unchanged", s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 D1_s3a_focus_ind.vi (the bed's SOURCE, never the bed)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 unchanged", s3.get("md5") == S3A_MD5, s3.get("md5", "?"), fatal=True)

    D.fresh("T5 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    bed = os.path.join(g.CLAUDEDEV, "SCRATCH_C62T3_%s.vi" % STAMP)
    K = R["leg"]
    try:
        shutil.copy2(S3A_ARTEFACT, bed)
        g.open_panel(bed)
        time.sleep(1.0)
        gate("P_1a the bed opens COLD at ExecState 1", read_exec_state("cold open", bed) == 1)

        d639 = diag_index(bed, D639)
        dtop = diag_index(bed, D536)
        K["diagram_indices"] = {"639": d639, "536(top)": dtop}
        fact("live diagram indices: #639 -> %r, #536 (top level) -> %r" % (d639, dtop))

        # ---- T2 from the review: is "the top level lists 0 nodes" real, or a reader artefact?
        t2 = {}
        try:
            t2["node_labels_top_len"] = len(g.node_labels(bed, dtop))
        except Exception as e:                                                     # noqa: BLE001
            t2["node_labels_top_len"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
        try:
            ni = g.node_info(bed, max_n=40)
            t2["node_info_len"] = len(ni)
            t2["node_info_rows"] = ni[:10]
        except Exception as e:                                                     # noqa: BLE001
            t2["node_info_len"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
        try:
            t2["count_Node_whole_vi"] = g.count(bed, "Node")
        except Exception as e:                                                     # noqa: BLE001
            t2["count_Node_whole_vi"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
        try:
            t2["owner_of_diagram_686"] = owner_of(bed, 686, strict=False)
        except Exception as e:                                                     # noqa: BLE001
            t2["owner_of_diagram_686"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
        K["T2_top_level_cross_check"] = t2
        fact("T2 CROSS-CHECK of the TOP-LEVEL reading: node_labels(top=%r) -> %r rows ; node_info(max_n=40) "
             "-> %r rows %r ; count('Node') whole VI -> %r ; owner_of(#686) -> %r"
             % (dtop, t2.get("node_labels_top_len"), t2.get("node_info_len"), t2.get("node_info_rows"),
                t2.get("count_Node_whole_vi"), t2.get("owner_of_diagram_686")))
        gate("P_2 the three top-level readers were all read and reported side by side", True,
             "node_labels %r / node_info %r / count('Node') %r"
             % (t2.get("node_labels_top_len"), t2.get("node_info_len"), t2.get("count_Node_whole_vi")))

        src0, _l0 = node_table(bed, SRC_UID, "BEFORE source")
        K["source_row_before"] = next((r for r in src0 if r["i"] == SRC_TERM), None)
        gate("P_1b #10686 t0 carries wire %d before the delete" % WIRE_PIN,
             (K["source_row_before"] or {}).get("wire") == WIRE_PIN,
             "%r" % (K["source_row_before"],))

        wires = g.report_all(bed, "Wire")
        idx = [w["i"] for w in wires if w["uid"] == WIRE_PIN]
        gone = g.delete_object(bed, "Wire", idx[0]) if len(idx) == 1 else None
        K["uids_gone"] = sorted(gone) if gone else gone
        fact("delete_object(Wire[%r] = uid %d) -> gone %r" % (idx[0] if idx else None, WIRE_PIN,
                                                              K["uids_gone"]))
        gate("P_3 the delete removed exactly wire %d" % WIRE_PIN, K["uids_gone"] == [WIRE_PIN],
             "%r" % (K["uids_gone"],))
        read_exec_state("after the delete (0 is EXPECTED)", bed)

        fn = [w["uid"] for w in g.report_all(bed, "Function")]
        ni_f = fn.index(SRC_UID) if SRC_UID in fn else None
        K["source_function_index"] = ni_f
        K["call_form"] = ("g.wire_indicators(bed, node_index=%r, src_terms=[%r], indicator_names=[%r], "
                          "diagram_index=%r, node_class='Function')" % (ni_f, SRC_NAME, OLD_LABEL, d639))
        fact("CALL: %s" % K["call_form"])
        try:
            K["wire_indicators_returned"] = g.wire_indicators(bed, ni_f, [SRC_NAME], [OLD_LABEL],
                                                              diagram_index=d639, node_class="Function")
            K["wire_indicators_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            K["wire_indicators_returned"] = None
            K["wire_indicators_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        fact("wire_indicators returned %r ; raised %r  (gscript.py:1794 tests exec_state ABSOLUTELY, and "
             "ExecState was already 0 before the call)"
             % (K["wire_indicators_returned"], K["wire_indicators_error_verbatim"]))
        es_after = read_exec_state("after wire_indicators", bed)
        K["exec_state_after_wire_indicators"] = es_after

        src1, _l1 = node_table(bed, SRC_UID, "AFTER source")
        K["source_row_after"] = next((r for r in src1 if r["i"] == SRC_TERM), None)
        NEW = (K["source_row_after"] or {}).get("wire")
        K["new_wire_uid_read_off_the_machine"] = NEW
        gate("P_4 wire_indicators left a NON-ZERO wire on #10686 t0", bool(NEW), "wire %r" % (NEW,),
             fatal=True)

        # ---- THE SEPARATOR: every terminal on that wire, from the TERMINAL side (reverse census)
        members, scanned = [], 0
        for i in range(SCAN_LIMIT):
            try:
                u, tr = g.node_terms_uid(bed, d639, i)
            except Exception:                                                      # noqa: BLE001
                break
            if not u:
                break
            scanned += 1
            for r in term_rows(tr):
                if r["wire"] == NEW:
                    members.append({"where": "Diagram #639 Nodes[%d] = #%s" % (i, u), "node_uid": u,
                                    "terminal": r["i"], "name": r["name"], "is_source": r["is_source"]})
        K["nodes_scanned_on_639"] = scanned
        try:
            prows = g.panel_wiring(bed)
        except Exception as e:                                                     # noqa: BLE001
            prows = []
            K["panel_wiring_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        K["panel_rows_total"] = len(prows)
        for r in prows:
            if r.get("wire") == NEW:
                members.append({"where": "panel control uid %s" % r.get("uid"), "node_uid": r.get("uid"),
                                "terminal": None, "name": r.get("label"),
                                "is_source": r.get("is_source")})
        K["members_of_the_new_net"] = members
        srcs = [m for m in members if m.get("is_source") is True]
        K["source_count_on_the_new_net"] = len(srcs)
        fact("THE NET OF WIRE %r, every terminal that carries it (%d nodes scanned on #639, %d panel rows): "
             "%r" % (NEW, scanned, len(prows), members))
        fact("SOURCES on that net: %d -> %r" % (len(srcs), srcs))
        gate("P_5 *** THE SEPARATOR: EXACTLY ONE terminal on wire %r reports is_source True "
             "(1 => H_bad 'two data sources' is DEAD; >=2 => H_bad confirmed) ***" % (NEW,),
             len(srcs) == 1, "%d source(s): %r" % (len(srcs), srcs))
        K["reading"] = ("EXACTLY ONE SOURCE - the two-source hypothesis is dead" if len(srcs) == 1
                        else "%d SOURCES - reported as measured, not interpreted" % len(srcs))
        fact("READING: %s. ExecState after wire_indicators was %r, with #10407 t0 still BARE."
             % (K["reading"], es_after))
        case1, _cl = node_table(bed, CASE_UID, "AFTER #10407")
        K["case_table_after"] = case1
    except Exception as e:                                                         # noqa: BLE001
        R["raised"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
    finally:
        try:
            g.close_panel(bed)
        except Exception:                                                          # noqa: BLE001
            pass
        if os.path.exists(bed):
            try:
                os.remove(bed)
            except Exception as e:                                                 # noqa: BLE001
                fact("could not remove the scratch: %s" % e)
    gate("Z_2 the scratch was DELETED in the same run", not os.path.exists(bed),
         "exists=%r" % (os.path.exists(bed),))

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
         "docs/NAMES.md:912-918")
    fact("THE COMPLETE ExecState TIMELINE: %r" % (R["exec_state_timeline"],))
    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
