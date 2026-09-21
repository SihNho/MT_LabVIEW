"""diag_c65_s3b_row2b - cycle 65 material #2 part B: feed S3b ROW 2's EXISTING 'index' indicator.

WHAT ALREADY EXISTS, CHECKED BEFORE A LINE OF THIS FILE WAS WRITTEN (CLAUDE.md: most of this project's cost
has been rebuilding what it already owned):
  - `grep "^def " tools/gscript.py`: 90 verbs. Every verb this file needs is already there - `exec_state`,
    `count`, `report_all`, `node_labels`, `node_terms_uid`, `panel_wiring`, `delete_object`, `save`,
    `close_panel`, `ref_counts`, `reset`, `op`. NO new verb, NO new op, NO edit to tools/gscript.py.
  - `tools/recipes/build_opconnectnested_v1.py:418` `connect_nested_v1` - the nested-diagram connect verb,
    already built and already used by row 1 (tools/bench/diag_c64_s3b_row1.py) and by row 2's first half
    (tools/bench/diag_c65_s3b_row2.py). Reused verbatim, donor OpConnectNested_v1.vi md5 b7a1bb56...
  - `tools/bench/diag_c65_s3b_row2.py` - THIS FILE'S DIRECT PREDECESSOR. Its helpers (gate/fact/probe/dump/
    safe/read_es/counts/node_census/new_nodes/terms_at/delete_by_uid/census_and_purge/save_artefact) are
    reused in shape; nothing new was invented for them.
  - `tools/bench/c60c_astcheck.py` - the static gate, run on THIS file before launch. Not edited.
  - No recipe is written, nothing under tools/recipes/ is touched. This is a diagnostic under tools/bench/
    (48(n)).

WHY THIS RUN EXISTS. `tools/bench/diag_c65_s3b_row2.log` (BGRUN END rc=1) saved
claudeDev\\D1_s3b_row2_20260921_151221.vi with the Case selector #10407 t2 fed from the new Local #23523
through wire 23540, but its last step - `wire_indicators(node_class='Function')` - did not run, because
#10757 is an `Index Array` primitive and is absent from all 183 'Function' rows. The EXISTING 'index'
indicator (panel control uid 23525) is therefore fed by nothing and the transport chain is open at its head.

THE ROUTE (given, not chosen here): connect #10757 t1 'element' (SOURCE, bare) DIRECTLY to the EXISTING
'index' indicator's block-diagram terminal (SINK) with connect_nested_v1, both endpoints on Diagram #639,
then purge the junk `Invoke` node by uid (Pre-decided 55(c)) before reading ExecState.

PREDICTION CONTRACT (machine-checkable; a failed prediction is reported, never explained away)
  B1  MEASURE FIRST, and report whatever comes back:
      (i)   the FULL Nodes[] census of Diagram #639 - index, uid, class, label, EVERY entry
      (ii)  #10757's class as the machine reports it, and which Traverse class censuses contain it
      (iii) the EXISTING 'index' indicator's block-diagram terminal: uid, owning diagram, and its Nodes[]
            index on Diagram #639 if it has one
      (iv)  the current terminal tables of #10407 (t2 expected on wire 23540) and #10757 (t1 expected bare)
  B2  ONLY IF B1(iii) yields an addressable Nodes[] index on Diagram #639:
      connect_nested_v1(sink_diag=46, sink_node=<that index>, sink_term=<the SINK terminal, read off the
      machine>, src_diag=46, src_node=<#10757's Nodes[] index, expected 27>, src_term=1); wire_delta 1;
      then the census diff finds exactly ONE new `Invoke` node, its full terminal table shows ZERO wired,
      it is deleted BY UID, and ExecState reads 1.
      IF B1(iii) gives no addressable index: STOP after B1, report the censuses, change nothing. No other
      verb is substituted, nothing is built, no retry under a different addressing.
  B3  IFF ExecState == 1: save claudeDev\\D1_s3b_row2_<stamp>.vi (a NEW stamp), md5 + size recorded and NOT
      byte-equal to the bed; then a LabVIEW RESTART and a COLD reopen of that file:
        K   ExecState == 1                                        <- THE PASS CRITERION
        K2  Wire == 1907  (bed 1906 + 1 = C0 1906 - 1 + 2, 55(f))
        K2b Node == 632, ControlTerminal == 116, Local == 10
        K2c #637 at 59/48 (no tunnel, 50(e))
        K3  ONE wire uid at BOTH ends of #10757 t1 -> the indicator terminal
        K4  the reverse census over EVERY node of Diagram #639 and ALL 116 panel rows finds EXACTLY ONE
            source on the new net, and its sink is panel control 23525
        K5  #10407 t2 still carries wire 23540 with the Local #23523 at the far end
        L   the ordered `Broken?` pass, LAST, after the cold reopen (42(b)); the ITEM terminal is `Broken?`
            (`Is Broken?` is only the panel label - 55(d))
  Z   md5 pins hold BEFORE and AFTER: ORIGINAL 2a78e17c / D1_s1_copy 3e3d23ce / D1_s2_loops 6ff19497 /
      D1_s3a_focus_ind eef91c1d / row 1 c7094f98 and 72f0d47d / row 2's TWO 151221 files 7a11818387fe /
      the donor OpCreateLocalRead_v0.vi f695d97a / OpConnectNested_v1.vi b7a1bb56; every scratch removed;
      refs opened == closed == 0 live; handles either side.

A step whose ExecState is not what the sequence expects STOPS the build: nothing further is saved, files
already saved STAY SAVED, the working copy is removed, and the full ExecState timeline plus the complete
terminal tables of #10407, #10757, the Local and the indicator's panel row are reported. No second
construction, no cast, no splice (51(h)), no allow_broken, no gui_save, no route change.
VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)). Rig 조립/ASSEMBLED: no motor, no ASI, no camera.
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
from build_d1_v0 import diag_index                                                 # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
ROW1A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_row1a_20260921_135932.vi")
ROW1A_MD5 = "c7094f98324af3bb53755fef718f8e28"
ROW1_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_20260921_135932.vi")
ROW1_MD5 = "72f0d47d0b1cbd0834d50f1483e558c1"
ROW2A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_row2a_20260921_151221.vi")
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_151221.vi")
BED_MD5 = "7a11818387fe44a764c2ff169b1dd6f7"
BED_SIZE = 476690
DONOR = os.path.join(g.CLAUDEDEV, "OpCreateLocalRead_v0.vi")
DONOR_MD5 = "f695d97a36ae127cd2dd3ca6b1fc1089"
OP_V1 = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")
OP_V1_MD5_PREFIX = "b7a1bb56"

TOP = 0                                  # Traverse index 0 = the top-level diagram
D639 = 639                               # the nested diagram both endpoints live on
D639_RECORDED = 46                       # recorded; the LIVE index is RE-READ off the machine and used
CASE_UID = 10407                         # the CaseStructure whose t2 the Local now feeds (row 2's first half)
CASE_T2 = 2
CASE_T2_WIRE = 23540                     # the wire row 2's first half minted
LOCAL_UID = 23523                        # the Local the first half created
SRC_UID = 10757                          # row 2's SOURCE node - an `Index Array` primitive
SRC_TERM = 1                             # #10757 t1 'element', a SOURCE, currently BARE
SRC_TERM_NAME = "element"
SRC_NODES_INDEX_RECORDED = 27            # recorded; the LIVE index is READ off the machine and used
IND_CONTROL_UID = 23525                  # the EXISTING 'index' indicator's PANEL control uid
IND_LABEL_RECORDED = "index"             # recorded; the LIVE label is READ off the machine and used
LOOP11_UID = 637
SIBLING_DIAG_UID = 686                   # the FlatSequenceFrame diagram that HOLDS WhileLoop #637
LOOP637_BASELINE = (59, 48)

# the BED's recorded censuses (tools/bench/diag_c65_s3b_row2.json "cold_counts") - RECORDED, never assumed:
# every gate below is computed from the values MEASURED at step [1] of THIS run.
NODE_RECORDED, WIRE_RECORDED, CT_RECORDED, LOCAL_RECORDED = 632, 1906, 116, 10

CLASS_CENSUSES = ("IndexArray", "Function", "GrowableFunction", "Node", "GObject", "ControlTerminal",
                  "Primitive", "Constant")
SCAN_BUDGET_S = 240.0
REVERSE_SCAN_LIMIT = 140
RUN_DEADLINE_S = 30 * 60.0               # the bgrun --max-min this file is launched under
RESERVE_S = 420.0                        # held back for the restart, the cold reopen and the ordered pass
REVERSE_MAX_BUDGET_S = 420.0

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c65_s3b_row2b.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

WORK = os.path.join(g.CLAUDEDEV, "WORK_C65R2B_%s.vi" % STAMP)          # working copy, removed at the end
FINAL_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_%s.vi" % STAMP)    # the artefact this run owes

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 65 material #2 part B: feed S3b ROW 2's EXISTING 'index' indicator from #10757 t1 with "
             "connect_nested_v1, purge the junk Invoke by uid, save, restart, cold-verify",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "no_open_panel_call_in_this_file": True,
     "no_ensure_loaded_call_in_this_file": True,
     "never_overwrites_a_loaded_path": ("WORK and the artefact are fresh stamped names LabVIEW has never "
                                        "seen; the BED is only ever READ (55(j))"),
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True, "no_astcheck_gate_file_edited": True, "no_gui_action": True,
     "wire_indicators": "NOT imported, NOT called - the route it belongs to was abandoned for this row",
     "allow_broken": "NEVER True", "gui_save": "NEVER called",
     "remove_bad_wires_scripted": "not imported, not called",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
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


def find_node(path, uid, hints, tag, budget_s=SCAN_BUDGET_S):
    """Which DIAGRAM lists `uid` in its Nodes[] - answered by the census that finds it, NEVER by owner_of.

    owner_of is measured to answer with the PREVIOUS query's object, silently (Pre-decided 53(d8));
    tools/bench/diag_c65_s3b_row2.py:284 is this helper's source.
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
    """55(c): after EVERY op call, diff the whole-VI Node census and purge the junk BY UID.

    A new node is DELETED only when it is an `Invoke` with ZERO wired terminals (the shape
    tools/bench/diag_c64_junkpurge.log measured: six terminals, none wired, errs [0,0,0,1055]) and its uid is
    not one this build intends. Any other new node is REPORTED VERBATIM and left alone; an `Invoke` whose
    terminal table could NOT be read is never deleted and stops the build instead.
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
        entry["zero_terminals_wired"] = bool(rows) and not wired
        if n["class"] == "Invoke" and rows and not wired:
            fact("%s THE JUNK NODE'S FULL TERMINAL TABLE IS PRINTED ABOVE; %d terminal(s), %d WIRED - the "
                 "purge precondition (ZERO wired) HOLDS" % (tag, len(rows), len(wired)))
            entry["delete"] = delete_by_uid(path, "Node", n["uid"], "%s purge" % tag)
            rec["deleted"].append(entry)
            fact("%s PURGED junk %s #%s (label %r, %d terminals, %d wired) on Diagram idx %r"
                 % (tag, n["class"], n["uid"], entry["label"], entry["n_terminals"], entry["n_wired"],
                    entry["diagram_index"]))
        elif n["class"] == "Invoke" and not rows:
            rec["reported_not_deleted"].append(entry)
            fact("%s AN `Invoke` NEW NODE #%s COULD NOT BE LOCATED OR READ (terminal table empty, loc %r) - "
                 "IT IS NOT DELETED. Deleting a node whose table was never read is the one branch that could "
                 "destroy the artefact." % (tag, n["uid"], loc.get("found")))
            R["purges"].append(rec)
            dump()
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


def live_d639(tag, path=None):
    """RE-READ the Traverse index of #639 off the machine. NEVER cached across a mutation."""
    p = path or WORK
    v, err = safe("%s diag_index(#%d)" % (tag, D639), lambda: diag_index(p, D639))
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


def reverse_budget_s():
    left = RUN_DEADLINE_S - (time.time() - T_START) - RESERVE_S
    return max(30.0, min(REVERSE_MAX_BUDGET_S, left))


def reverse_census(target, wire_uid, d639, tag, store="reverse"):
    """K4: every terminal carrying `wire_uid`, from the TERMINAL side, over EVERY node of #639 and EVERY
    panel row. No `Broken?` is read. Scoped to ONE diagram, which is where a wire's terminals live."""
    t0 = time.time()
    budget = reverse_budget_s()
    members, scanned, per_call = [], 0, []
    h_before = labview_handles()
    stopped = ""
    # archive/peer/2026-09-21-c65-row2-indicator.md, "two smaller things": the predecessor's gate I walked
    # "the net of wire 0", and 0 means NO WIRE, so it collected eight unrelated BARE terminals and called
    # them sources. A census of wire uid 0 is refused here instead of being reported as a net.
    if not wire_uid:
        rec0 = {"wire": wire_uid, "refused": ("a wire uid of 0/None is NOT a net - 0 means the terminal is "
                                              "BARE; no reverse census is taken (peer c65-row2-indicator)"),
                "members": [], "source_count": None, "sources": [], "sinks": [],
                "nodes_scanned_on_639": 0, "panel_rows_total": None, "scan_stopped": "not attempted"}
        K[store] = rec0
        fact("%s REVERSE CENSUS NOT TAKEN: %s" % (tag, rec0["refused"]))
        dump()
        return rec0
    if isinstance(d639, int) and wire_uid:
        for i in range(REVERSE_SCAN_LIMIT):
            if time.time() - t0 > budget:
                stopped = "wall-clock-derived budget %.0f s reached after %d node(s)" % (budget, scanned)
                break
            c0 = time.time()
            try:
                u, tr = g.node_terms_uid(target, d639, i)
            except Exception:                                                      # noqa: BLE001
                break
            per_call.append(round(time.time() - c0, 3))
            if not u:
                break
            scanned += 1
            for r in tr:
                if r["wire"] == wire_uid:
                    members.append({"where": "Diagram #639 Nodes[%d] = #%s" % (i, u), "node_uid": u,
                                    "terminal": r["i"], "name": r["name"], "is_source": r["is_source"]})
    h_after = labview_handles()
    prows, _e = panel_all(target, "%s reverse" % tag)
    for r in prows:
        if r.get("wire") == wire_uid:
            members.append({"where": "panel control uid %s" % r.get("uid"), "node_uid": r.get("uid"),
                            "terminal": None, "name": r.get("label"), "is_source": r.get("is_source"),
                            "panel_row": True})
    srcs = [m for m in members if m.get("is_source") is True]
    sinks = [m for m in members if m.get("is_source") is False]
    rec = {"wire": wire_uid, "nodes_scanned_on_639": scanned, "panel_rows_total": len(prows),
           "members": members, "source_count": len(srcs), "sources": srcs, "sinks": sinks,
           "budget_s": round(budget, 1), "scan_stopped": stopped,
           "scan_cost_s": round(time.time() - t0, 1), "per_call_first5": per_call[:5],
           "per_call_last5": per_call[-5:], "handles_before": h_before, "handles_after": h_after,
           "scoped_to": "Diagram #%d only, plus every panel row" % D639}
    K[store] = rec
    fact("%s REVERSE CENSUS of wire %r (%d nodes scanned on #639, %d panel rows, %.1f s of a %.0f s "
         "budget%s): %r" % (tag, wire_uid, scanned, len(prows), rec["scan_cost_s"], budget,
                            ("; " + stopped) if stopped else "", members))
    fact("%s REVERSE SOURCES on that net: %d -> %r ; SINKS: %d -> %r"
         % (tag, len(srcs), srcs, len(sinks), sinks))
    dump()
    return rec


def save_artefact(tag, dest, not_equal_to, not_equal_label):
    """g.save writes the WORKING copy in place; the artefact is a fresh path LabVIEW has never seen.

    A file byte-identical to its predecessor means THE IN-MEMORY EDITS DID NOT LAND. That is reported as a
    FAILURE, never as a pass (cycle 62's C_1 false pass).
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
    rec["compared_against"] = not_equal_label
    rec["bytes_equal_to_the_predecessor"] = (ff.get("md5") == not_equal_to)
    rec["carries_the_in_memory_edits"] = (bool(rec["exists"]) and not rec["save_error_verbatim"]
                                          and not rec["bytes_equal_to_the_predecessor"])
    R["artefacts_on_disk"].append(rec)
    fact("%s FILE ON DISK: %s  md5 %r  size %r  mtime %r  (ExecState at the save %r ; COM save error %r ; "
         "bytes equal to %s %r ; carries the in-memory edits %r)"
         % (tag, dest, rec["md5"], rec["size"], rec["mtime"], rec["exec_state_at_save"],
            rec["save_error_verbatim"], not_equal_label, rec["bytes_equal_to_the_predecessor"],
            rec["carries_the_in_memory_edits"]))
    gate("%s *** A FILE IS ON DISK at %s ***" % (tag, os.path.basename(dest)), bool(rec["exists"]),
         "md5 %r size %r mtime %r" % (rec["md5"], rec["size"], rec["mtime"]))
    gate("%s that file is NOT byte-identical to %s (the in-memory edits LANDED)" % (tag, not_equal_label),
         bool(rec["exists"]) and not rec["bytes_equal_to_the_predecessor"]
         and not rec["save_error_verbatim"],
         "md5 %r vs %s %r ; save error %r"
         % (rec["md5"], not_equal_label, not_equal_to, rec["save_error_verbatim"]))
    dump()
    return rec


def stop_report(stage, why):
    """A step whose ExecState is not what the sequence expects STOPS the row. Files already saved STAY."""
    K["stopped_at"] = stage
    K["stopped_because"] = why
    fact("*** THE BUILD STOPS AT %s: %s ***" % (stage, why))
    read_es("at the stop", WORK)
    tables = K.setdefault("stop_report_tables", {})
    hints = [K.get("d639_last"), TOP]
    for label, uid in (("#10407 the Case", CASE_UID), ("#%d the source" % SRC_UID, SRC_UID),
                       ("the Local #23523", LOCAL_UID),
                       ("the indicator terminal", K.get("indicator_terminal_uid"))):
        if uid is None:
            continue
        _loc, rows = node_view(WORK, uid, hints, "STOP REPORT %s" % label)
        tables[label] = rows
    prows, _pe = panel_all(WORK, "STOP REPORT panel")
    tables["the indicator's panel row"] = [r for r in prows if r.get("uid") == IND_CONTROL_UID]
    fact("STOP REPORT - the indicator's panel row (control uid %d): %r"
         % (IND_CONTROL_UID, tables["the indicator's panel row"]))
    dump()
    raise Stop(why)


# ============================================================ B1 - MEASURE FIRST
def b1_measure():
    print("\n---------- [B1] MEASURE FIRST - the three censuses the route is conditional on", flush=True)
    d639 = live_d639("[B1]")
    K["d639_last"] = d639
    gate("A1 Diagram #%d resolves to a live Traverse index" % D639, isinstance(d639, int),
         "%r (the brief recorded %d)" % (d639, D639_RECORDED), fatal=True)
    gate("A1b that index equals the recorded %d" % D639_RECORDED, d639 == D639_RECORDED, "%r" % (d639,))
    hints = [d639, TOP]

    # ---- (i) THE FULL Nodes[] CENSUS OF #639
    whole, _werr = node_census(WORK, "[B1] whole-VI")
    by_uid = {n["uid"]: n for n in whole}
    labs, lerr = safe("[B1] node_labels(#639)", lambda: g.node_labels(WORK, d639), [])
    rows = []
    for i, r in enumerate(labs or []):
        cls = (by_uid.get(r["uid"]) or {}).get("class")
        rows.append({"nodes_index": i, "uid": r["uid"], "class": cls, "label": r["label"],
                     "in_whole_vi_node_census": r["uid"] in by_uid})
    K["d639_nodes_census"] = {"diagram_index": d639, "diagram_uid": D639, "n": len(rows),
                              "node_labels_error": lerr, "rows": rows}
    print("\n=== (i) THE FULL Nodes[] CENSUS OF Diagram #%d (Traverse index %r): %d entries"
          % (D639, d639, len(rows)), flush=True)
    print("  %-5s %-8s %-22s %s" % ("idx", "uid", "class", "label"), flush=True)
    for r in rows:
        print(("  %-5d %-8s %-22s %r" % (r["nodes_index"], r["uid"], r["class"], r["label"]))
              .encode("ascii", "replace").decode("ascii"), flush=True)
    gate("A2 (i) the Nodes[] census of #%d came back non-empty" % D639, bool(rows),
         "%d entries ; node_labels error %r" % (len(rows), lerr), fatal=True)
    dump()

    # ---- (ii) #10757's CLASS, AND WHICH CLASS CENSUSES CONTAIN IT
    src_row = next((r for r in rows if r["uid"] == SRC_UID), None)
    K["src_row"] = src_row
    fact("[B1] (ii) #%d in the #639 Nodes[] census: %r" % (SRC_UID, src_row))
    gate("A3 (ii) #%d appears in Diagram #%d's Nodes[] list" % (SRC_UID, D639), src_row is not None,
         "%r" % (src_row,), fatal=True)
    src_idx = src_row["nodes_index"]
    K["src_nodes_index_live"] = src_idx
    gate("A3b (ii) its Nodes[] index is the recorded %d" % SRC_NODES_INDEX_RECORDED,
         src_idx == SRC_NODES_INDEX_RECORDED, "live %r vs recorded %r" % (src_idx, SRC_NODES_INDEX_RECORDED))
    memberships = {}
    for cls in CLASS_CENSUSES:
        crows, cerr = safe("[B1] report_all(%r)" % cls, lambda c=cls: g.report_all(WORK, c), None)
        if crows is None:
            memberships[cls] = {"n": None, "contains_10757": None, "error_verbatim": cerr}
        else:
            memberships[cls] = {"n": len(crows), "contains_10757": any(x["uid"] == SRC_UID for x in crows),
                                "error_verbatim": cerr}
        fact("[B1] (ii) census %-18s n=%-6r contains #%d: %r%s"
             % (cls, memberships[cls]["n"], SRC_UID, memberships[cls]["contains_10757"],
                ("  ERROR " + cerr) if cerr else ""))
    K["class_memberships_of_10757"] = memberships
    K["src_class_as_the_machine_reports_it"] = src_row["class"]
    fact("[B1] (ii) *** #%d's class AS THE MACHINE REPORTS IT = %r ; label %r ; the censuses that CONTAIN "
         "it: %r ***" % (SRC_UID, src_row["class"], src_row["label"],
                         [c for c, v in memberships.items() if v.get("contains_10757")]))
    dump()

    # ---- (iii) WHERE THE EXISTING 'index' INDICATOR'S BLOCK-DIAGRAM TERMINAL LIVES
    prows, perr = panel_all(WORK, "[B1] (iii)")
    prow = next((r for r in prows if r.get("uid") == IND_CONTROL_UID), None)
    K["indicator_panel_row"] = prow
    K["panel_rows_total"] = len(prows)
    fact("[B1] (iii) the indicator's PANEL row (control uid %d): %r" % (IND_CONTROL_UID, prow))
    gate("A4 (iii) panel control uid %d is present in the panel census" % IND_CONTROL_UID, prow is not None,
         "%d panel rows ; error %r" % (len(prows), perr), fatal=True)
    live_label = prow.get("label")
    K["indicator_live_label"] = live_label
    gate("A4b (iii) it is an INDICATOR and its LIVE label is %r" % IND_LABEL_RECORDED,
         bool(prow.get("indicator")) and live_label == IND_LABEL_RECORDED,
         "indicator=%r label=%r (hex %s)"
         % (prow.get("indicator"), live_label, (live_label or "").encode("utf-8").hex()))
    fact("[B1] (iii) the indicator's terminal is currently wired to %r (0 = bare ; term_err %r wire_err %r)"
         % (prow.get("wire"), prow.get("term_err"), prow.get("wire_err")))

    ct_all, cterr = safe("[B1] report_all('ControlTerminal')",
                         lambda: g.report_all(WORK, "ControlTerminal"), [])
    K["control_terminal_census_n"] = len(ct_all or [])
    ct_on_639 = [r for r in rows if r["class"] == "ControlTerminal"]
    K["control_terminals_on_d639"] = ct_on_639
    print("\n=== (iii) EVERY ControlTerminal ON Diagram #%d (%d of the %d in the whole VI)"
          % (D639, len(ct_on_639), len(ct_all or [])), flush=True)
    for r in ct_on_639:
        print(("  Nodes[%-4d] uid %-8s label %r" % (r["nodes_index"], r["uid"], r["label"]))
              .encode("ascii", "replace").decode("ascii"), flush=True)
    # THE REVIEW'S CENTRAL CLAIM, MEASURED RATHER THAN ASSUMED (archive/peer/2026-09-21-c65-row2-indicator.md
    # point 1, citing docs/d1-route-b-plan.md:239 "a ControlTerminal, which Diagram.Nodes[] does not list (R3)"
    # and tools/gscript.py:1342-1343 "Control/indicator terminals are class Terminal, not Node"): does the
    # whole-VI ControlTerminal census intersect Diagram #639's Nodes[] list AT ALL?
    ct_uids = {r["uid"] for r in (ct_all or [])}
    d639_uids = {r["uid"] for r in rows}
    inter = sorted(ct_uids & d639_uids)
    K["control_terminal_uids_present_in_d639_nodes"] = inter
    fact("[B1] (iii) *** THE WHOLE-VI ControlTerminal CENSUS (%d uids, census error %r) INTERSECTED WITH "
         "Diagram #%d's Nodes[] LIST (%d uids) = %d uid(s): %r ***"
         % (len(ct_uids), cterr, D639, len(d639_uids), len(inter), inter[:20]))
    gate("A4c (iii) MEASURED: the ControlTerminal census and Diagram #%d's Nodes[] list intersect at all "
         "(if this FAILS, the review's R3 is confirmed on this machine and B2 is not attempted)" % D639,
         bool(inter), "%d common uid(s): %r" % (len(inter), inter[:20]))
    matches = [r for r in ct_on_639 if r["label"] == live_label]
    K["control_terminal_label_matches"] = matches
    fact("[B1] (iii) ControlTerminal rows on #%d whose label == %r: %r" % (D639, live_label, matches))
    for m in matches:
        tt = terms_at(WORK, d639, m["nodes_index"], m["uid"], "[B1] candidate CT #%s" % m["uid"])
        m["terminal_table"] = tt
    good = [m for m in matches
            if any((t.get("is_source") is False) for t in (m.get("terminal_table") or {}).get("terminals", []))]
    K["indicator_terminal_candidates_with_a_sink"] = [
        {"uid": m["uid"], "nodes_index": m["nodes_index"], "label": m["label"]} for m in good]
    ok3 = len(good) == 1
    gate("A5 (iii) *** EXACTLY ONE ControlTerminal on Diagram #%d carries the indicator's label %r AND has a "
         "SINK terminal - it is ADDRESSABLE by a Nodes[] index ***" % (D639, live_label), ok3,
         "%d label match(es), %d with a sink: %r"
         % (len(matches), len(good), K["indicator_terminal_candidates_with_a_sink"]))
    if ok3:
        chosen = good[0]
        K["indicator_terminal_uid"] = chosen["uid"]
        K["indicator_terminal_nodes_index"] = chosen["nodes_index"]
        sink_terms = [t for t in chosen["terminal_table"]["terminals"] if t.get("is_source") is False]
        K["indicator_terminal_sink_index"] = sink_terms[0]["i"]
        K["indicator_terminal_sink_row"] = sink_terms[0]
        fact("[B1] (iii) *** THE INDICATOR'S BLOCK-DIAGRAM TERMINAL: uid %s, owning diagram #%d (Traverse "
             "index %r), Nodes[%d], SINK terminal index %d, currently wired to %r ***"
             % (chosen["uid"], D639, d639, chosen["nodes_index"], sink_terms[0]["i"],
                sink_terms[0]["wire"]))
        gate("A5b (iii) that SINK terminal is currently BARE (the indicator is fed by nothing)",
             not sink_terms[0]["wire"], "wire %r" % (sink_terms[0]["wire"],))
    else:
        K["indicator_terminal_uid"] = None
        fact("[B1] (iii) *** THE INDICATOR'S TERMINAL IS NOT ADDRESSABLE BY A Nodes[] INDEX ON Diagram #%d. "
             "B2 IS NOT ATTEMPTED; NOTHING IS SUBSTITUTED, NOTHING IS BUILT, NOTHING IS SAVED. ***" % D639)
    dump()

    # ---- (iv) THE CURRENT TERMINAL TABLES OF #10407 AND #10757
    print("\n=== (iv) THE CURRENT TERMINAL TABLES", flush=True)
    cloc, crows = node_view(WORK, CASE_UID, hints, "[B1] (iv) #%d" % CASE_UID)
    K["case_before"] = {"found": cloc.get("found"), "terminals": crows}
    ct2 = next((t for t in crows if t["i"] == CASE_T2), {})
    gate("A6 (iv) #%d t%d carries the first half's wire %d" % (CASE_UID, CASE_T2, CASE_T2_WIRE),
         ct2.get("wire") == CASE_T2_WIRE, "t%d %r" % (CASE_T2, ct2))
    sloc, srows = node_view(WORK, SRC_UID, hints, "[B1] (iv) #%d" % SRC_UID)
    K["src_before"] = {"found": sloc.get("found"), "terminals": srows}
    st1 = next((t for t in srows if t["i"] == SRC_TERM), {})
    K["src_t1_before"] = st1
    gate("A7 (iv) #%d t%d is named %r, is a SOURCE, and is BARE"
         % (SRC_UID, SRC_TERM, SRC_TERM_NAME),
         st1.get("name") == SRC_TERM_NAME and st1.get("is_source") is True and not st1.get("wire"),
         "t%d %r" % (SRC_TERM, st1))
    lloc, lrows = node_view(WORK, LOCAL_UID, hints, "[B1] (iv) the Local #%d" % LOCAL_UID)
    K["local_before"] = {"found": lloc.get("found"), "terminals": lrows}
    dump()
    return d639, hints, src_idx, ok3


# ============================================================ THE BUILD
def build():
    print("\n========== ROW 2's INDICATOR:  #%d t%d %r (SOURCE)  ->  the EXISTING %r indicator "
          "(panel control uid %d)" % (SRC_UID, SRC_TERM, SRC_TERM_NAME, IND_LABEL_RECORDED,
                                      IND_CONTROL_UID), flush=True)
    K.update({"bed": os.path.basename(BED), "working_copy": os.path.basename(WORK),
              "artefact": os.path.basename(FINAL_PATH)})
    shutil.copy2(BED, WORK)

    # ---------- [1] the cold reading and the baselines - C0 IS MEASURED HERE
    print("\n---------- [1] the BED's cold reading and the baselines (C0 is measured, never remembered)",
          flush=True)
    es0 = read_es("[1] the working copy of the BED, COLD (no open_panel call)", WORK)
    K["bed_cold_exec_state"] = es0
    gate("A0 the working copy of the BED opens COLD at ExecState 1", es0 == 1, "%r" % (es0,), fatal=True)
    c0 = counts(WORK, "[1] the BED baseline")
    K["counts_baseline"] = c0
    C0 = c0.get("Wire")
    R["C0_wire_census_of_the_bed"] = C0
    NODE0, CT0, LOCAL0 = c0.get("Node"), c0.get("ControlTerminal"), c0.get("Local")
    K["bed_censuses_measured"] = {"Wire_C0": C0, "Node": NODE0, "ControlTerminal": CT0, "Local": LOCAL0}
    fact("[1] *** C0 (the BED's Wire census, MEASURED) = %r ; Node %r ; ControlTerminal %r ; Local %r ; the "
         "final cold Wire gate is therefore C0 + 1 = %r (55(f): bed 1906 + 1 = C0 1906 - 1 + 2) ***"
         % (C0, NODE0, CT0, LOCAL0, (C0 + 1) if isinstance(C0, int) else None))
    gate("A0b the BED's censuses equal the recorded ones: Node %d / Wire %d / ControlTerminal %d / Local %d"
         % (NODE_RECORDED, WIRE_RECORDED, CT_RECORDED, LOCAL_RECORDED),
         NODE0 == NODE_RECORDED and C0 == WIRE_RECORDED and CT0 == CT_RECORDED
         and LOCAL0 == LOCAL_RECORDED, "%r" % (c0,))
    if not isinstance(C0, int):
        stop_report("A0_C0", "the BED's Wire census did not read as an integer (%r)" % (C0,))

    d686, _d6e = safe("[1] diag_index(#%d)" % SIBLING_DIAG_UID,
                      lambda: diag_index(WORK, SIBLING_DIAG_UID))
    K["d686_traverse_index"] = d686
    d639_probe = live_d639("[1] pre-B1")
    loop_hints = [d686, TOP, d639_probe]
    t637_0 = loop637(WORK, "[1] BEFORE", loop_hints)
    K["loop637_baseline_measured"] = list(t637_0)
    gate("A0c #%d is at the recorded %r baseline BEFORE anything is edited (50(e))"
         % (LOOP11_UID, list(LOOP637_BASELINE)), tuple(t637_0) == LOOP637_BASELINE, "%r" % (t637_0,))
    dump()

    # ---------- [B1]
    d639, hints, src_idx, addressable = b1_measure()

    # ---------- [B2] THE CONNECT - conditional on B1(iii)
    if not addressable:
        K["b2_not_attempted_because"] = ("B1(iii) did not yield an addressable Nodes[] index on Diagram "
                                         "#%d for the indicator's block-diagram terminal" % D639)
        gate("B *** THE CONNECT ***", False,
             "NOT ATTEMPTED (by design): %s - the three censuses are reported in full above and NOTHING "
             "was changed" % K["b2_not_attempted_because"])
        for nm in ("C the junk `Invoke` is purged by uid", "D ExecState == 1 after the purge"):
            gate(nm, False, "NOT REACHED: B2 was not attempted")
        raise Stop("B1(iii): the indicator terminal is not addressable - stopped after B1 as instructed")

    sink_node = K["indicator_terminal_nodes_index"]
    sink_term = K["indicator_terminal_sink_index"]
    print("\n---------- [B2] connect_nested_v1: #%d t%d %r (SOURCE) -> the %r indicator's terminal #%s "
          "(SINK), both on Diagram #%d"
          % (SRC_UID, SRC_TERM, SRC_TERM_NAME, K.get("indicator_live_label"),
             K.get("indicator_terminal_uid"), D639), flush=True)
    K["connect_call"] = ("connect_nested_v1(target, sink_diag=%r, sink_node=%r, sink_term=%r, src_diag=%r, "
                         "src_node=%r, src_term=%r)" % (d639, sink_node, sink_term, d639, src_idx, SRC_TERM))
    fact("[B2] THE CALL: %s" % K["connect_call"])
    nodes_before, _ = node_census(WORK, "[B2] before the connect")
    w_before = g.count(WORK, "Wire")
    K["wire_before_connect"] = w_before
    buf = io.StringIO()
    t0 = time.time()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es_ret, oerr = CONNECT_V1(WORK, d639, sink_node, sink_term, d639, src_idx, SRC_TERM,
                                          V1_LABELS)
        K.update({"connect_wire_delta": dw, "connect_exec_state_returned": es_ret,
                  "connect_op_error": oerr, "connect_error_verbatim": ""})
    except Exception as e:                                                         # noqa: BLE001
        K.update({"connect_wire_delta": None, "connect_exec_state_returned": None,
                  "connect_op_error": None,
                  "connect_error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
    K["connect_cost_s"] = round(time.time() - t0, 2)
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    fact("[B2] connect returned wire_delta %r, ExecState %r, op error %r (%.2f s) ; python error %r"
         % (K.get("connect_wire_delta"), K.get("connect_exec_state_returned"), K.get("connect_op_error"),
            K["connect_cost_s"], K.get("connect_error_verbatim")))
    gate("B *** the connect added EXACTLY ONE Wire object ***", K.get("connect_wire_delta") == 1,
         "wire_delta %r ; op error %r ; python error %r"
         % (K.get("connect_wire_delta"), K.get("connect_op_error"), K.get("connect_error_verbatim")))
    K["counts_after_connect"] = counts(WORK, "[B2] after the connect (before the purge)")
    K["exec_state_after_connect_before_purge"] = read_es("[B2] after the connect, BEFORE the purge", WORK)
    dump()

    # ---------- [B2b] THE PURGE (55(c))
    print("\n---------- [B2b] the census diff and the junk purge (55(c)) - BY UID", flush=True)
    _after, prec = census_and_purge(WORK, nodes_before, "[B2] connect", hints)
    K["purge_after_connect"] = prec
    gate("C *** exactly ONE new `Invoke` node appeared, showed ZERO wired terminals, and was deleted BY "
         "UID ***", len(prec["deleted"]) == 1 and not prec["reported_not_deleted"],
         "deleted %r ; reported-not-deleted %r ; new %r"
         % ([d["uid"] for d in prec["deleted"]], [d["uid"] for d in prec["reported_not_deleted"]],
            prec["new_uids"]))
    es1 = read_es("[B2b] after the purge", WORK)
    K["exec_state_after_purge"] = es1
    K["counts_after_purge"] = counts(WORK, "[B2b] after the purge")
    gate("D *** ExecState == 1 after the purge ***", es1 == 1, "%r" % (es1,))
    if es1 != 1:
        stop_report("D_exec_state_after_purge",
                    "ExecState is %r after the connect and the purge, not 1; nothing is saved" % (es1,))

    # ---------- the in-memory readback
    sink_tt = terms_at(WORK, d639, sink_node, K.get("indicator_terminal_uid"), "[B2c] the indicator terminal")
    K["indicator_terminal_after"] = sink_tt
    srow = next((t for t in sink_tt.get("terminals", []) if t["i"] == sink_term), {})
    src_tt = terms_at(WORK, d639, src_idx, SRC_UID, "[B2c] #%d the source" % SRC_UID)
    K["src_after"] = src_tt
    st1 = next((t for t in src_tt.get("terminals", []) if t["i"] == SRC_TERM), {})
    K["new_wire_uid"] = srow.get("wire")
    fact("[B2c] the new wire: indicator terminal t%d wire %r  |  #%d t%d wire %r  ->  SAME uid: %r"
         % (sink_term, srow.get("wire"), SRC_UID, SRC_TERM, st1.get("wire"),
            bool(srow.get("wire")) and srow.get("wire") == st1.get("wire")))
    gate("E ONE wire uid at BOTH ends (in memory): #%d t%d and the indicator terminal"
         % (SRC_UID, SRC_TERM), bool(srow.get("wire")) and srow.get("wire") == st1.get("wire"),
         "sink %r ; source %r" % (srow, st1))
    dump()

    # ---------- [B3] SAVE
    print("\n---------- [B3] SAVE the finished row", flush=True)
    sv = save_artefact("B3", FINAL_PATH, BED_MD5, "the BED D1_s3b_row2_20260921_151221.vi")
    if not sv.get("exists"):
        stop_report("B3_save", "the save left no file on disk")
    return FINAL_PATH


# ============================================================ the ORDERED `Broken?` pass (42(b)) - LAST
def ordered_pass(target, d639):
    P = K.setdefault("ordered_pass", {})
    P["target"] = target
    P["note"] = ("LAST, after the cold reopen only (42(b), 52(f)). NOTHING is saved after this point; the "
                 "in-memory VI is discarded. The idempotent re-connect is how the op's `Broken?` read is "
                 "made to answer about the EXISTING wire. The ITEM terminal is `Broken?`; `Is Broken?` is "
                 "only the panel label (55(d)).")
    sink_loc = find_node(target, K.get("indicator_terminal_uid"), [d639, TOP], "[L] the indicator terminal")
    src_loc = find_node(target, SRC_UID, [d639, TOP], "[L] #%d" % SRC_UID)
    sink_i = (sink_loc.get("found") or {}).get("nodes_index")
    sink_d = (sink_loc.get("found") or {}).get("diagram_index")
    src_i = (src_loc.get("found") or {}).get("nodes_index")
    src_d = (src_loc.get("found") or {}).get("diagram_index")
    sink_term = K.get("indicator_terminal_sink_index")
    P["call"] = ("connect_nested_v1(target, %r, %r, %r, %r, %r, %r) - IDEMPOTENT re-connect of an EXISTING "
                 "connection; wire_delta must be 0" % (sink_d, sink_i, sink_term, src_d, src_i, SRC_TERM))
    fact(P["call"])
    if sink_i is None or src_i is None or sink_term is None:
        P["not_attempted_because"] = "an endpoint is not addressable on the reopened file"
        gate("L the ORDERED `Broken?` reads False on the new indicator wire", False,
             "NOT ATTEMPTED: %s" % P["not_attempted_because"])
        return
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            odw, oes, oerr = CONNECT_V1(target, sink_d, sink_i, sink_term, src_d, src_i, SRC_TERM, V1_LABELS)
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
    P["broken_ordered"] = ib
    fact("ORDERED `Broken?` = %r on wire uid %r (wire_delta %r - expected 0 ; error %r)"
         % (ib, rd.get("UID 2"), P.get("wire_delta"), P.get("error_verbatim")))
    gate("L *** the ORDERED `Broken?` reads False on the new indicator wire ***", ib is False,
         "Broken? %r on wire %r ; wire_delta %r" % (ib, rd.get("UID 2"), P.get("wire_delta")))
    read_es("[L] after the Broken? read (SUSPECT, NAMES.md:912-918; every save is already done)", target)


# ============================================================ MAIN
def main():
    print("=== diag_c65_s3b_row2b  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== cycle 65 material #2 part B: feed S3b ROW 2's EXISTING 'index' indicator from #10757 t1 "
          "'element' with connect_nested_v1, purge the junk Invoke by uid (55(c)), save, cold-verify.",
          flush=True)
    print("=== NO g.open_panel, NO g.ensure_loaded, NO wire_indicators, NO move_in call appears in this "
          "file. VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)).", flush=True)

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
    s3 = probe("Z0d D1_s3a_focus_ind.vi", S3A_ARTEFACT)
    gate("Z_0d D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"))
    r1a = probe("Z0e D1_s3b_row1a", ROW1A_ARTEFACT)
    gate("Z_0e D1_s3b_row1a md5 == %s" % ROW1A_MD5, r1a.get("md5") == ROW1A_MD5, r1a.get("md5", "?"))
    r1 = probe("Z0f D1_s3b_row1", ROW1_ARTEFACT)
    gate("Z_0f D1_s3b_row1 md5 == %s" % ROW1_MD5, r1.get("md5") == ROW1_MD5, r1.get("md5", "?"))
    r2a = probe("Z0g D1_s3b_row2a (the 151221 step-6 file)", ROW2A_ARTEFACT)
    gate("Z_0g D1_s3b_row2a md5 == %s" % BED_MD5, r2a.get("md5") == BED_MD5, r2a.get("md5", "?"))
    bd = probe("Z0h THE BED D1_s3b_row2 (FATAL pin, never written)", BED)
    gate("Z_0h the BED's md5 == %s and its size == %d" % (BED_MD5, BED_SIZE),
         bd.get("md5") == BED_MD5 and int(bd.get("size", -1)) == BED_SIZE,
         "md5 %r size %r" % (bd.get("md5"), bd.get("size")), fatal=True)
    dn = probe("Z0i the donor OpCreateLocalRead_v0.vi", DONOR)
    gate("Z_0i OpCreateLocalRead_v0.vi md5 == %s" % DONOR_MD5, dn.get("md5") == DONOR_MD5,
         dn.get("md5", "?"))
    v1 = probe("Z0j OpConnectNested_v1.vi", OP_V1)
    R["op_v1_md5_before"] = v1.get("md5")
    gate("Z_0j OpConnectNested_v1.vi md5 starts with %s" % OP_V1_MD5_PREFIX,
         str(v1.get("md5", "")).startswith(OP_V1_MD5_PREFIX), v1.get("md5", "?"))
    gate("Z_0k neither the artefact path nor the working name exists before this run",
         not os.path.exists(FINAL_PATH) and not os.path.exists(WORK),
         "%s / %s" % (os.path.basename(FINAL_PATH), os.path.basename(WORK)))

    D.fresh("Z_R RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    final = None
    try:
        final = build()
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

    # ---------- [B3b] the COLD reopen in a freshly restarted LabVIEW
    print("\n========== [B3b] RESTART, then COLD-open the artefact", flush=True)
    C0 = R.get("C0_wire_census_of_the_bed")
    if final and os.path.exists(final):
        D.fresh("[B3b] RESTART before the cold reopen")
        R["handles"]["after_cold_restart"] = labview_handles()
        es_cold = read_es("[B3b] COLD, freshly restarted LabVIEW, %s" % os.path.basename(final), final)
        R["cold_exec_state"] = es_cold
        gate("K *** THE COLD READING of %s: ExecState 1 is the artefact's pass criterion ***"
             % os.path.basename(final), es_cold == 1, "ExecState %r" % (es_cold,))
        cf = probe("[B3b] the artefact, re-read", final)
        R["cold_md5"] = cf.get("md5")
        cc = counts(final, "[B3b] COLD")
        R["cold_counts"] = cc
        dump()
        want_wire = (C0 + 1) if isinstance(C0, int) else None
        gate("K2 *** THE COLD Wire census is C0 + 1 = %r (55(f): bed 1906 + 1 = C0 1906 - 1 + 2) ***"
             % (want_wire,), cc.get("Wire") == want_wire,
             "Wire %r ; C0 %r ; full counts %r" % (cc.get("Wire"), C0, cc))
        base = K.get("bed_censuses_measured", {})
        gate("K2b the other COLD censuses are unchanged from the bed: Node %r, ControlTerminal %r, Local %r"
             % (base.get("Node"), base.get("ControlTerminal"), base.get("Local")),
             cc.get("Node") == base.get("Node") and cc.get("ControlTerminal") == base.get("ControlTerminal")
             and cc.get("Local") == base.get("Local"), "%r" % (cc,))
        cd639, _ce = safe("[B3b] diag_index(#639) COLD", lambda: diag_index(final, D639))
        cd686, _ce2 = safe("[B3b] diag_index(#686) COLD", lambda: diag_index(final, SIBLING_DIAG_UID))
        R["cold_d639"] = cd639
        t637_cold = loop637(final, "[B3b] COLD", [cd686, TOP, cd639])
        gate("K2c #%d is at the %r baseline on the COLD artefact (no tunnel, 50(e))"
             % (LOOP11_UID, K.get("loop637_baseline_measured")),
             list(t637_cold) == K.get("loop637_baseline_measured"), "%r" % (t637_cold,))

        # the two far ends, read off the COLD file
        sloc_c, srows_c = node_view(final, SRC_UID, [cd639, TOP], "[B3b] COLD #%d" % SRC_UID)
        st1_c = next((t for t in srows_c if t["i"] == SRC_TERM), {})
        iloc_c, irows_c = (node_view(final, K.get("indicator_terminal_uid"), [cd639, TOP],
                                     "[B3b] COLD the indicator terminal")
                           if K.get("indicator_terminal_uid") else ({}, []))
        it_c = next((t for t in irows_c if t["i"] == K.get("indicator_terminal_sink_index")), {})
        R["cold_far_ends"] = {"src_t1": st1_c, "src_found": (sloc_c or {}).get("found"),
                              "indicator_terminal": it_c, "indicator_found": (iloc_c or {}).get("found")}
        fact("[B3b] COLD FAR END: #%d t%d %r wire %r  <->  the indicator terminal #%r t%r %r wire %r "
             "(owner diagram %r)"
             % (SRC_UID, SRC_TERM, st1_c.get("name"), st1_c.get("wire"),
                K.get("indicator_terminal_uid"), K.get("indicator_terminal_sink_index"), it_c.get("name"),
                it_c.get("wire"), (iloc_c or {}).get("found")))
        new_wire = st1_c.get("wire")
        R["cold_new_wire_uid"] = new_wire
        gate("K3 *** COLD: ONE wire uid at BOTH ends of #%d t%d -> the indicator terminal ***"
             % (SRC_UID, SRC_TERM),
             bool(new_wire) and new_wire == it_c.get("wire"),
             "source %r ; indicator terminal %r" % (st1_c, it_c))

        cloc_c, crows_c = node_view(final, CASE_UID, [cd639, TOP], "[B3b] COLD #%d" % CASE_UID)
        ct2_c = next((t for t in crows_c if t["i"] == CASE_T2), {})
        lloc_c, lrows_c = node_view(final, LOCAL_UID, [cd639, TOP], "[B3b] COLD the Local #%d" % LOCAL_UID)
        lfar = lrows_c[0] if lrows_c else {}
        R["cold_case_t2"] = {"case_t2": ct2_c, "local_terminal": lfar,
                             "local_found": (lloc_c or {}).get("found")}
        fact("[B3b] COLD: #%d t%d wire %r  |  the Local #%d t0 %r wire %r (owner uid %d)"
             % (CASE_UID, CASE_T2, ct2_c.get("wire"), LOCAL_UID, lfar.get("name"), lfar.get("wire"),
                LOCAL_UID))
        gate("K5 COLD: row 2's FIRST half still holds - #%d t%d carries wire %d and the Local #%d is at the "
             "far end" % (CASE_UID, CASE_T2, CASE_T2_WIRE, LOCAL_UID),
             ct2_c.get("wire") == CASE_T2_WIRE and lfar.get("wire") == CASE_T2_WIRE,
             "case t%d %r ; local %r" % (CASE_T2, ct2_c, lfar))
        dump()

        # K4 - the reverse census
        print("\n---------- [B3c] the REVERSE CENSUS of the new net (every node of #%d, every panel row)"
              % D639, flush=True)
        rc = reverse_census(final, new_wire, cd639, "[B3c]")
        one_src = rc["source_count"] == 1
        sink_rows = [m for m in rc["sinks"] if m.get("panel_row")]
        sink_is_ctl = len(sink_rows) == 1 and sink_rows[0]["node_uid"] == IND_CONTROL_UID
        gate("K4 *** the reverse census finds EXACTLY ONE source on the new net, and its sink is panel "
             "control %d ***" % IND_CONTROL_UID, one_src and sink_is_ctl and not rc["scan_stopped"],
             "sources %d %r ; panel sinks %r ; scan_stopped %r"
             % (rc["source_count"], rc["sources"], sink_rows, rc["scan_stopped"]))
        gate("K4b that one source is #%d t%d %r" % (SRC_UID, SRC_TERM, SRC_TERM_NAME),
             one_src and rc["sources"][0].get("node_uid") == SRC_UID
             and rc["sources"][0].get("terminal") == SRC_TERM,
             "%r" % (rc["sources"],))
        cp, _cpe = panel_all(final, "[B3c] COLD panel")
        R["cold_panel_rows"] = len(cp)
        iprow = next((r for r in cp if r.get("uid") == IND_CONTROL_UID), None)
        R["cold_indicator_panel_row"] = iprow
        fact("[B3c] COLD the indicator's panel row (control uid %d): %r" % (IND_CONTROL_UID, iprow))
        gate("K4c COLD: all %d panel rows read back and the indicator's own row carries the new wire %r"
             % (CT_RECORDED, new_wire),
             len(cp) == CT_RECORDED and bool(iprow) and iprow.get("wire") == new_wire,
             "%d panel rows ; row %r" % (len(cp), iprow))
        dump()

        print("\n========== [L] the ORDERED `Wire.Broken?` pass (42(b), 55(d)) - LAST, nothing is saved "
              "after this point", flush=True)
        ordered_pass(final, cd639)
        close_quietly(final)
    else:
        for nm in ("K *** THE COLD READING ***", "K2 the COLD Wire census", "K3 ONE wire uid at both ends",
                   "K4 the reverse census", "L the ORDERED `Broken?` read"):
            gate(nm, False, "NOT REACHED: no artefact on disk")
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
    z4 = probe("Z1e D1_s3b_row1a after everything", ROW1A_ARTEFACT)
    z5 = probe("Z1f D1_s3b_row1 after everything", ROW1_ARTEFACT)
    z6 = probe("Z1g D1_s3b_row2a after everything", ROW2A_ARTEFACT)
    z7 = probe("Z1h THE BED D1_s3b_row2 after everything", BED)
    z8 = probe("Z1i the donor OpCreateLocalRead_v0.vi after everything", DONOR)
    z9 = probe("Z1j OpConnectNested_v1.vi after everything", OP_V1)
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    gate("Z_1a row 1's TWO artefacts are byte-unchanged", z4.get("md5") == ROW1A_MD5
         and z5.get("md5") == ROW1_MD5, "row1a %s ; row1 %s" % (z4.get("md5"), z5.get("md5")))
    gate("Z_1b row 2's TWO 151221 files (the BED included) are byte-unchanged",
         z6.get("md5") == BED_MD5 and z7.get("md5") == BED_MD5,
         "row2a %s ; BED %s" % (z6.get("md5"), z7.get("md5")))
    gate("Z_1c OpCreateLocalRead_v0.vi is byte-unchanged", z8.get("md5") == DONOR_MD5,
         "%s" % (z8.get("md5"),))
    gate("Z_1d OpConnectNested_v1.vi is byte-unchanged", z9.get("md5") == R.get("op_v1_md5_before"),
         "%r -> %r" % (R.get("op_v1_md5_before"), z9.get("md5")))
    rcs = R["ref_counts"] or {}
    gate("Z_1e refs opened == closed, 0 live",
         isinstance(rcs, dict) and rcs.get("live", rcs.get("open", 1)) in (0, None), repr(rcs))

    print("\n=== THE COMPLETE TIMESTAMPED ExecState TIMELINE", flush=True)
    print("  %-4s %-72s %-12s %-10s" % ("step", "tag", "ExecState", "wall"), flush=True)
    for row in R["exec_state_timeline"]:
        print(("  %-4d %-72s %-12r %-10s" % (row["step"], row["tag"][:72], row["exec_state"],
                                             row["wall_clock"]))
              .encode("ascii", "replace").decode("ascii"), flush=True)

    print("\n=== THE FILES THIS RUN LEFT ON DISK", flush=True)
    for a in R["artefacts_on_disk"]:
        print(("  %-6s %-46s md5 %r  size %r  mtime %r  ES-at-save %r  carries the edits %r"
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

    print("\n=== THE WIRE ARITHMETIC (55(f))", flush=True)
    print("  C0 (bed) %r -> after the connect %r -> after the purge %r -> COLD %r  (want C0 + 1 = %r)"
          % (C0, (K.get("counts_after_connect") or {}).get("Wire"),
             (K.get("counts_after_purge") or {}).get("Wire"),
             (R.get("cold_counts") or {}).get("Wire"), (C0 + 1) if isinstance(C0, int) else None),
          flush=True)

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
