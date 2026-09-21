"""diag_c65_s3b_row2c - cycle 65 material #3 part B: feed S3b ROW 2's EXISTING 'index' indicator with
`wire_indicators`, and SAVE the finished row.

WHAT ALREADY EXISTS, CHECKED BEFORE A LINE OF THIS FILE WAS WRITTEN (CLAUDE.md: most of this project's cost
has been rebuilding what it already owned):
  - `grep "^def " tools/gscript.py`: every verb this file needs is ALREADY THERE - `wire_indicators`
    (tools/gscript.py:1756), `exec_state`, `count`, `report_all`, `node_labels`, `node_terms_uid`,
    `panel_wiring`, `delete_object`, `save`, `close_panel`, `ref_counts`, `reset`, `op`. NO new verb, NO new
    op, NO edit to tools/gscript.py, NO edit to any *_astcheck.py gate file.
  - `tools/bench/diag_c65_s3b_row2b.py` - THIS FILE'S DIRECT PREDECESSOR. Its helpers (gate/fact/probe/dump/
    safe/read_es/counts/node_census/new_nodes/terms_at/find_node/node_view/delete_by_uid/census_and_purge/
    live_d639/loop637/panel_all/reverse_census/save_artefact/stop_report) are reused in shape; nothing new
    was invented for them.
  - `tools/bench/c60c_astcheck.py` - the static gate, run on THIS file before launch. NOT edited. This file
    calls no `move_in`, so all 12 of its gates are expected to pass.
  - `tools/recipes/build_opconnectnested_v1.py:418` `connect_nested_v1` - reused ONLY for the ordered
    `Broken?` pass at the very end (its embedded 6371004 readback is the fleet's only ordered reader).
  - No recipe is written; nothing under tools/recipes/ is written to. This is a diagnostic (48(n)).

WHY THIS RUN EXISTS. `tools/bench/diag_c65_s3b_row2.log` built and saved
claudeDev\\D1_s3b_row2_20260921_151221.vi with the Case selector #10407 t2 fed from the new Local #23523
through wire 23540, but the run's last step never happened; `tools/bench/diag_c65_s3b_row2b.log:208` then
MEASURED why the substitute route is dead: the whole-VI ControlTerminal census (116 uids) intersected with
Diagram #639's Nodes[] list (75 uids) is EMPTY, so `connect_nested_v1` - whose only addressing is
Diagram[d].Nodes[n].Terminals[t] - cannot reach a front-panel terminal at all. A ControlTerminal is class
`Terminal`, not `Node`, and Nodes[] never lists one.

THE ROUTE (given by judgement, not chosen here): the verb S3a's own cycle-59 recipe already ran SUCCESSFULLY
on this very indicator - `wire_indicators`, which names the indicator BY LABEL and does not use Nodes[]
addressing for it at all - under the class the machine actually reports for #10757, `IndexArray`, not
`Function`.
  precedent 1  tools/bench/cycle59_s3a_recipe.log:119-131 - the SAME node #10757, the SAME terminal
               'element', the SAME label 'index', diagram_index=46, IndexArray[20] of 47: error '',
               indicator wire 0 -> 10990, ExecState 1. There the SOURCE was WIRED, so it BRANCHED (delta 0).
  precedent 2  tools/bench/diag_c64_s3b_row1.log:299-313 - ROW 1, BOTH ends BARE (step [2] deleted wire
               10799, the single net feeding BOTH #10686 t0 and control 23555 - :108,:112,:115,:120, a
               correction the peer made to my own framing): it MINTED a new wire (Wire 1905 -> 1906),
               ExecState 1, and the T3 reverse census found EXACTLY ONE source and the sink was PANEL
               CONTROL 23555 - even though a co-labelled Local sat on the same diagram at Nodes[73].
               Row 2 is precedent 2's case, so the wire arithmetic here is +1.
  NOT a check   `error VERBATIM ''` proves nothing on this verb - a swallowed 5001 is a silent no-op
               (tools/gscript.py:1773), so the WIRE UID is the evidence, never the error column.

PREDICTION CONTRACT (machine-checkable; a failed prediction is reported, never explained away)
  B1  MEASURE FIRST, and report whatever comes back, before any edit:
      (i)   the BED read COLD: ExecState 1, Wire 1906, Node 632, ControlTerminal 116, Local 10, #637 59/48
      (ii)  HOW `wire_indicators` RESOLVES `indicator_names` - the wrapper's own source lines, echoed off
            disk, and the stated conclusion about whether a diagram Local named 'index' can satisfy it
      (iii) `node_index` resolved OFF THE MACHINE: the index of uid 10757 in report_all('IndexArray'),
            with the member count
      (iv)  panel row for control 23525 (expect label 'index', indicator, wire 0 = BARE), #10757 t1
            (expect 'element', is_source True, wire 0), #10407 t2 (expect wire 23540), and the Local
            #23523's own row on #639 - the LABEL-COLLISION suspect
      (v)   THE PEER'S OWN DISCRIMINATING TEST (archive/peer/2026-09-21-c65-row2-wireind.md §4.1): WHO
            OWNS the indicator's ControlTerminal? diag_c65_s3b_row2b.log:208 cannot answer it - a
            ControlTerminal never appears in ANY diagram's Nodes[], so "0 on #639" is an IDENTITY, not an
            observation. The owning diagram is the property that decides whether cycle 59's move_in still
            holds (docs/NAMES.md:899-901). Reported as a gate; NOT fatal.
      (vi)  the 'index' LABEL CENSUS (peer §4.2): every terminal on every node of #639 and every panel row
            whose label case-folds to 'index' - control 23525, #10757 t2, #10407 t2 and the Local #23523
            all carry it. Re-read identically AFTER the call; EXACTLY ONE row may change and it must be
            control 23525 (gate E5), which names a mis-binding at the instant it happens.
  B2  g.wire_indicators(target, node_index=<(iii)>, src_terms=['element'], indicator_names=['index'],
      diagram_index=46, node_class='IndexArray').
      A RAISE FROM THE WRAPPER IS A READING, NOT A VERDICT (it tests exec_state != 1 ABSOLUTELY,
      tools/gscript.py:1794-1797, a measured defect that raised a false failure in cycle 62): it is caught,
      printed VERBATIM, and the machine is then measured. Nothing is reverted on the raise alone.
  B2b PURGE (55(c)): census-diff the Node census across B2; any NEW unwired `Invoke` gets its full terminal
      table printed, zero-wired confirmed, and is deleted BY UID. Only then is ExecState read. Expect 1.
      (Row 1's census diff after `wire_indicators` was `Node 631 -> 631 ; 0 new uid(s): []`, so the expected
      number of purges here is ZERO; the purge is armed anyway and reports what it finds.)
  B3  IFF ExecState == 1: save claudeDev\\D1_s3b_row2_<new stamp>.vi (the 151221 files stay untouched),
      md5 + size recorded, gated NOT byte-equal to the bed.
  K   LabVIEW RESTART, then a COLD reopen of that file:
        K    ExecState == 1                                   <- THE PASS CRITERION
        K2   Wire == C0 + 1 == 1907  (55(f)'s baseline - 1 + 2)
        K2b  Node == 632, ControlTerminal == 116, Local == 10
        K2c  #637 at 59/48 (no tunnel, 50(e))
        K3   ONE wire uid at BOTH ends: #10757 t1 and panel control 23525's own row
        K4   THE LABEL-COLLISION GATE - a reverse census over EVERY node of Diagram #639 and ALL 116 panel
             rows finds EXACTLY ONE source on the new net, its sink is panel control 23525, and the Local
             #23523 is NOT on it
        K5   #10407 t2 still carries wire 23540 with the Local #23523 at the far end
        L    the ordered `Broken?` pass, LAST, after the cold reopen (42(b)); the ITEM terminal is `Broken?`
             (`Is Broken?` is only the panel label - 55(d))
  Z   md5 pins hold BEFORE and AFTER: ORIGINAL 2a78e17c / D1_s1_copy 3e3d23ce / D1_s2_loops 6ff19497 /
      D1_s3a_focus_ind eef91c1d / row 1 c7094f98 and 72f0d47d / row 2's TWO 151221 files 7a11818387fe /
      the donor OpCreateLocalRead_v0.vi f695d97a / OpConnectNested_v1.vi b7a1bb56; every scratch removed;
      refs opened == closed == 0 live; handles either side.

A step whose ExecState is not what the sequence expects STOPS the build: nothing further is saved, the
working copy is removed, and the full ExecState timeline plus the complete terminal tables of #10757,
#10407, the Local #23523 and panel row 114 are reported. No second construction, no cast, no splice (51(h)),
no allow_broken, no gui_save, no third route.
VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)). Rig ASSEMBLED: no motor, no ASI, no camera.
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
from build_d1_v0 import diag_index, owner_of                                       # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
GSCRIPT_SRC = os.path.join(ROOT, "tools", "gscript.py")
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
D639 = 639                               # the nested diagram the source lives on
D639_RECORDED = 46                       # recorded; the LIVE index is RE-READ off the machine and used
CASE_UID = 10407                         # the CaseStructure whose t2 the Local feeds (row 2's first half)
CASE_T2 = 2
CASE_T2_WIRE = 23540                     # the wire row 2's first half minted
LOCAL_UID = 23523                        # the Local the first half created - THE LABEL-COLLISION SUSPECT
SRC_UID = 10757                          # row 2's SOURCE node - an `Index Array` primitive
SRC_TERM = 1                             # #10757 t1 'element', a SOURCE, currently BARE
SRC_TERM_NAME = "element"
SRC_NODES_INDEX_RECORDED = 27            # recorded; the LIVE index is READ off the machine and used
SRC_CLASS = "IndexArray"                 # measured 2026-09-21, diag_c65_s3b_row2b.log:200 - NOT `Function`
IND_CONTROL_UID = 23525                  # the EXISTING 'index' indicator's PANEL control uid (panel row 114)
IND_LABEL_RECORDED = "index"             # recorded; the LIVE label is READ off the machine and used
IND_PANEL_ROW_RECORDED = 114
LOOP11_UID = 637
SIBLING_DIAG_UID = 686                   # the FlatSequenceFrame diagram that HOLDS WhileLoop #637
LOOP637_BASELINE = (59, 48)

# the BED's recorded censuses (tools/bench/diag_c65_s3b_row2b.json) - RECORDED, never assumed: every gate
# below is computed from the values MEASURED at step [1] of THIS run.
NODE_RECORDED, WIRE_RECORDED, CT_RECORDED, LOCAL_RECORDED = 632, 1906, 116, 10
WIRE_FINAL_EXPECTED = 1907               # C0 + 1 (55(f)'s baseline - 1 + 2)
LOOPTUNNEL_RECORDED = 135                # cycle59_s3a_recipe.log:115 - a move of this number means a
#                                          structure boundary was crossed and a tunnel was minted
COLLIDING_LABEL = "index"                # the label EVERY object below shares - peer c65-row2-wireind §2

CLASS_CENSUSES = ("IndexArray", "GrowableFunction", "Function", "Node", "GObject", "ControlTerminal",
                  "Local")
SCAN_BUDGET_S = 240.0
REVERSE_SCAN_LIMIT = 140
RUN_DEADLINE_S = 30 * 60.0               # the bgrun --max-min this file is launched under
RESERVE_S = 420.0                        # held back for the restart, the cold reopen and the ordered pass
REVERSE_MAX_BUDGET_S = 420.0

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c65_s3b_row2c.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

WORK = os.path.join(g.CLAUDEDEV, "WORK_C65R2C_%s.vi" % STAMP)          # working copy, removed at the end
FINAL_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_%s.vi" % STAMP)    # the artefact this run owes

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 65 material #3 part B: feed S3b ROW 2's EXISTING 'index' indicator (panel control "
             "23525) from #10757 t1 'element' with wire_indicators(node_class='IndexArray'), purge, save, "
             "restart, cold-verify, ordered Broken? LAST",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "route_given_by_judgement": "wire_indicators under node_class='IndexArray' - the verb cycle 59 ran "
                                 "successfully on THIS indicator (cycle59_s3a_recipe.log:119)",
     "no_open_panel_call_in_this_file": True,
     "no_move_in_call_in_this_file": True,
     "never_overwrites_a_loaded_path": ("WORK and the artefact are fresh stamped names LabVIEW has never "
                                        "seen; the BED is only ever READ (55(j))"),
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True, "no_astcheck_gate_file_edited": True, "no_gui_action": True,
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


def counts(path, tag, classes=("Node", "Wire", "ControlTerminal", "Local", "LoopTunnel")):
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

    owner_of is measured to answer with the PREVIOUS query's object, silently (Pre-decided 53(d8)).
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
    tools/bench/diag_c64_junkpurge.log measured: six terminals, none wired). Any other new node is REPORTED
    VERBATIM and left alone; an `Invoke` whose terminal table could NOT be read is never deleted and stops
    the build instead.
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


def panel_row(rows, uid):
    return next((r for r in rows if r.get("uid") == uid), None)


def wire_uid_set(path, tag):
    """The SET of Wire uids, not just the count. peer c65-row2-wireind §5: `1906 -> 1907` is satisfied by a
    tunnel-crossing build too, so the identity of the new object is what must be checked."""
    rows, err = safe("%s report_all('Wire')" % tag, lambda: g.report_all(path, "Wire"), [])
    s = {r["uid"] for r in (rows or [])}
    fact("%s Wire uid SET: %d uid(s)%s" % (tag, len(s), (" ; ERROR " + err) if err else ""))
    return s, err


def label_census(path, d639, tag, limit=REVERSE_SCAN_LIMIT):
    """peer c65-row2-wireind §4.2: EVERY object whose label case-folds to 'index' - every terminal of every
    node on Diagram #639, plus every front-panel row - each with uid / is_source / wire. Read BEFORE and
    AFTER the call; exactly ONE row may change, and it must be panel control 23525."""
    t0 = time.time()
    rows = []
    if isinstance(d639, int):
        for i in range(limit):
            try:
                u, tr = g.node_terms_uid(path, d639, i)
            except Exception:                                                      # noqa: BLE001
                break
            if not u:
                break
            for r in tr:
                if (r["name"] or "").casefold() == COLLIDING_LABEL:
                    rows.append({"where": "Diagram #%d Nodes[%d] = #%s t%d" % (D639, i, u, r["i"]),
                                 "node_uid": u, "terminal": r["i"], "name": r["name"],
                                 "is_source": r["is_source"], "wire": r["wire"]})
    prows, _e = panel_all(path, "%s label census" % tag)
    for r in prows:
        if (r.get("label") or "").casefold() == COLLIDING_LABEL:
            rows.append({"where": "panel control uid %s" % r.get("uid"), "node_uid": r.get("uid"),
                         "terminal": None, "name": r.get("label"), "is_source": r.get("is_source"),
                         "wire": r.get("wire"), "panel_row": True})
    fact("%s *** THE %r LABEL CENSUS: %d row(s) in %.1f s ***" % (tag, COLLIDING_LABEL, len(rows),
                                                                  time.time() - t0))
    for r in rows:
        fact("    %s  %-44s uid %-7r t%-5r is_source=%-5r wire=%r"
             % (tag, r["where"], r["node_uid"], r["terminal"], r["is_source"], r["wire"]))
    return rows


def label_census_key(rows):
    return {(r["node_uid"], r["terminal"]): r["wire"] for r in rows}


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
    # a wire uid of 0 is NOT a net - 0 means the terminal is BARE (peer c65-row2-indicator).
    if not wire_uid:
        rec0 = {"wire": wire_uid, "refused": ("a wire uid of 0/None is NOT a net - 0 means the terminal is "
                                              "BARE; no reverse census is taken"),
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
           "local_23523_on_this_net": any(m.get("node_uid") == LOCAL_UID for m in members),
           "scan_cost_s": round(time.time() - t0, 1), "per_call_first5": per_call[:5],
           "per_call_last5": per_call[-5:], "handles_before": h_before, "handles_after": h_after,
           "scoped_to": "Diagram #%d only, plus every panel row" % D639}
    K[store] = rec
    fact("%s REVERSE CENSUS of wire %r (%d nodes scanned on #639, %d panel rows, %.1f s of a %.0f s "
         "budget%s): %r" % (tag, wire_uid, scanned, len(prows), rec["scan_cost_s"], budget,
                            ("; " + stopped) if stopped else "", members))
    fact("%s REVERSE SOURCES on that net: %d -> %r ; SINKS: %d -> %r ; the Local #%d on this net: %r"
         % (tag, len(srcs), srcs, len(sinks), sinks, LOCAL_UID, rec["local_23523_on_this_net"]))
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
    for label, uid in (("#%d the source" % SRC_UID, SRC_UID), ("#10407 the Case", CASE_UID),
                       ("the Local #23523", LOCAL_UID)):
        _loc, rows = node_view(WORK, uid, hints, "STOP REPORT %s" % label)
        tables[label] = rows
    prows, _pe = panel_all(WORK, "STOP REPORT panel")
    tables["the indicator's panel row"] = [r for r in prows if r.get("uid") == IND_CONTROL_UID]
    fact("STOP REPORT - the indicator's panel row (control uid %d): %r"
         % (IND_CONTROL_UID, tables["the indicator's panel row"]))
    dump()
    raise Stop(why)


# ================================================ B1 - MEASURE FIRST, AND READ THE WRAPPER OFF DISK
def report_how_wire_indicators_resolves():
    """The brief's step 2: READ off tools/gscript.py and REPORT, BEFORE the call, how `wire_indicators`
    resolves its `indicator_names` argument. This is a READ of a source file, never an edit."""
    print("\n---------- [B1-ii] HOW `wire_indicators` RESOLVES `indicator_names` - read off disk, not "
          "remembered", flush=True)
    rec = {"source": "tools/gscript.py:1756-1798"}
    try:
        with open(GSCRIPT_SRC, encoding="utf-8") as f:
            lines = f.read().splitlines()
        body = lines[1780:1798]            # the wrapper's executable body, 1-indexed 1781..1798
        rec["wrapper_body_verbatim"] = body
        for i, ln in enumerate(body, start=1781):
            print(("      [gscript.py:%d] %s" % (i, ln)).encode("ascii", "replace").decode("ascii"),
                  flush=True)
    except Exception as e:                                                         # noqa: BLE001
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        fact("[B1-ii] could not read tools/gscript.py: %s" % rec["error_verbatim"])
    rec["answer"] = (
        "THE WRAPPER ITSELF RESOLVES NOTHING. It only sets four panel controls on OpWireInd_v0.vi: "
        "`Class Name`/`index` select the SOURCE NODE by index within the traversed class census "
        "(docs/NAMES.md:506 - for OpWireInd `index` means the index WITHIN `Class Name`, not a Nodes[] "
        "position), `Names` names the source TERMINALS, and `Class Name 2`='Diagram' + `index 2`="
        "diagram_index + `Names 2`=indicator_names are handed to erdosmiller's `Wire Indicators.vi` as "
        "`Diagram in` + `Indicator Names`. The RESOLUTION happens inside that library VI, and its own "
        "Context Help - recorded at .claude/skills/labview-automation/references/com-driving.md:155-170 - "
        "says it 'selects EXISTING indicators by label ... on Diagram in'. So the search domain is the "
        "objects reachable from Diagram[46] = #639, matched BY LABEL.")
    rec["can_a_local_satisfy_it"] = (
        "IN PRINCIPLE YES, AND THAT IS HAZARD 1: the Local #%d sits on that very diagram (#639) and its "
        "terminal is ALSO labelled 'index'. NOT RESOLVED BY THIS READ. The one MEASUREMENT that bears on it "
        "is row 1, where the identical collision existed (Local at #639 Nodes[73], label "
        "'Automatic Error Handling', same as panel control 23555) and the reverse census afterwards "
        "(diag_c64_s3b_row1.log:311-313) found the sink to be PANEL CONTROL 23555 with the Local NOT on the "
        "net. This run's K4 gate is what decides it here, on this file." % LOCAL_UID)
    K["how_wire_indicators_resolves"] = rec
    fact("[B1-ii] %s" % rec["answer"])
    fact("[B1-ii] CAN A DIAGRAM LOCAL NAMED 'index' SATISFY `indicator_names`? %s"
         % rec["can_a_local_satisfy_it"])
    dump()
    return rec


def b1_measure():
    print("\n---------- [B1] MEASURE FIRST - every address is resolved OFF THE MACHINE", flush=True)
    d639 = live_d639("[B1]")
    K["d639_last"] = d639
    gate("A1 Diagram #%d resolves to a live Traverse index" % D639, isinstance(d639, int),
         "%r (the brief recorded %d)" % (d639, D639_RECORDED), fatal=True)
    gate("A1b that index equals the recorded %d" % D639_RECORDED, d639 == D639_RECORDED, "%r" % (d639,))
    hints = [d639, TOP]

    # ---- (ii) how the verb resolves the indicator name  (printed BEFORE the call, as the brief requires)
    report_how_wire_indicators_resolves()

    # ---- (iii) node_index RESOLVED OFF THE MACHINE
    print("\n---------- [B1-iii] `node_index` resolved off the machine: uid %d in report_all(%r)"
          % (SRC_UID, SRC_CLASS), flush=True)
    memberships = {}
    for cls in CLASS_CENSUSES:
        rows, err = safe("[B1] report_all(%r)" % cls, lambda c=cls: g.report_all(WORK, c), [])
        idx = next((r["i"] for r in (rows or []) if r["uid"] == SRC_UID), None)
        memberships[cls] = {"members": len(rows or []), "index_of_%d" % SRC_UID: idx, "error": err}
        fact("[B1-iii] census %-16r %4d member(s) ; index of #%d = %r%s"
             % (cls, len(rows or []), SRC_UID, idx, (" ; ERROR " + err) if err else ""))
    K["class_memberships"] = memberships
    src_idx_in_class = memberships.get(SRC_CLASS, {}).get("index_of_%d" % SRC_UID)
    n_members = memberships.get(SRC_CLASS, {}).get("members")
    K["node_index_for_wire_indicators"] = src_idx_in_class
    K["indexarray_member_count"] = n_members
    fact("[B1-iii] *** node_index = the index of uid %d in report_all(%r) = %r ; that census has %r "
         "member(s) ***" % (SRC_UID, SRC_CLASS, src_idx_in_class, n_members))
    gate("A2 *** uid %d IS in the %r census and yields a node_index ***" % (SRC_UID, SRC_CLASS),
         isinstance(src_idx_in_class, int),
         "index %r of %r member(s)" % (src_idx_in_class, n_members), fatal=True)
    gate("A2b uid %d is ABSENT from the 'Function' census (the c65 #1 finding, re-measured)" % SRC_UID,
         memberships.get("Function", {}).get("index_of_%d" % SRC_UID) is None,
         "Function index %r of %r rows" % (memberships.get("Function", {}).get("index_of_%d" % SRC_UID),
                                           memberships.get("Function", {}).get("members")))

    # ---- (iv) the three terminal tables + the panel row + the collision suspect
    print("\n---------- [B1-iv] the terminal tables, the panel row and the LABEL-COLLISION suspect",
          flush=True)
    sloc, srows = node_view(WORK, SRC_UID, hints, "[B1-iv] #%d the source" % SRC_UID)
    K["src_before"] = {"found": sloc.get("found"), "terminals": srows}
    st1 = next((t for t in srows if t["i"] == SRC_TERM), {})
    fact("[B1-iv] #%d t%d = %r ; is_source %r ; wire %r (0 = BARE)"
         % (SRC_UID, SRC_TERM, st1.get("name"), st1.get("is_source"), st1.get("wire")))
    gate("A3 #%d t%d is named %r, IS a source, and is BARE" % (SRC_UID, SRC_TERM, SRC_TERM_NAME),
         st1.get("name") == SRC_TERM_NAME and st1.get("is_source") is True and not st1.get("wire"),
         "%r" % (st1,))
    gate("A3b #%d's live Nodes[] position equals the recorded %d" % (SRC_UID, SRC_NODES_INDEX_RECORDED),
         (sloc.get("found") or {}).get("nodes_index") == SRC_NODES_INDEX_RECORDED,
         "%r" % ((sloc.get("found") or {}).get("nodes_index"),))

    cloc, crows = node_view(WORK, CASE_UID, hints, "[B1-iv] #%d the Case" % CASE_UID)
    ct2 = next((t for t in crows if t["i"] == CASE_T2), {})
    K["case_before"] = {"found": cloc.get("found"), "t2": ct2}
    gate("A3c #%d t%d still carries row 2's first-half wire %d" % (CASE_UID, CASE_T2, CASE_T2_WIRE),
         ct2.get("wire") == CASE_T2_WIRE, "%r" % (ct2,))

    lloc, lrows = node_view(WORK, LOCAL_UID, hints, "[B1-iv] the Local #%d (collision suspect)" % LOCAL_UID)
    lrow = lrows[0] if lrows else {}
    K["local_before"] = {"found": lloc.get("found"), "terminals": lrows}
    fact("[B1-iv] *** THE LABEL-COLLISION SUSPECT: the Local #%d is at %r ; its terminal is %r (hex %r), "
         "is_source %r, wire %r ***"
         % (LOCAL_UID, lloc.get("found"), lrow.get("name"), lrow.get("name_hex"), lrow.get("is_source"),
            lrow.get("wire")))
    gate("A3d the Local #%d IS on Diagram #%d and its terminal label collides with the indicator's %r"
         % (LOCAL_UID, D639, IND_LABEL_RECORDED),
         (lloc.get("found") or {}).get("diagram_uid") == D639
         and lrow.get("name") == IND_LABEL_RECORDED,
         "found %r ; terminal %r" % (lloc.get("found"), lrow))

    prows, _pe = panel_all(WORK, "[B1-iv]")
    K["panel_rows_before"] = len(prows)
    irow = panel_row(prows, IND_CONTROL_UID)
    K["indicator_panel_row_before"] = irow
    K["indicator_live_label"] = (irow or {}).get("label")
    fact("[B1-iv] the indicator's PANEL row (control uid %d): %r ; label hex %r"
         % (IND_CONTROL_UID, irow, ((irow or {}).get("label") or "").encode("utf-8").hex()))
    gate("A4 panel control uid %d is present, IS an indicator, its LIVE label is %r, and it is BARE"
         % (IND_CONTROL_UID, IND_LABEL_RECORDED),
         bool(irow) and irow.get("indicator") is True and irow.get("label") == IND_LABEL_RECORDED
         and not irow.get("wire"), "%r" % (irow,), fatal=True)
    gate("A4b the panel census has the recorded %d rows" % CT_RECORDED, len(prows) == CT_RECORDED,
         "%d rows" % len(prows))

    # ---- (v) THE PEER'S OWN DISCRIMINATING TEST (c65-row2-wireind §4.1): does the indicator's
    #          ControlTerminal still SIT ON #639, i.e. is cycle 59's move_in still in force on this bed?
    #          diag_c65_s3b_row2b.log:208 CANNOT answer this - a ControlTerminal never appears in ANY
    #          diagram's Nodes[] list, so "0 on #639" is an identity, not an observation. The owning
    #          DIAGRAM is the property that decides it (docs/NAMES.md:899-901).
    print("\n---------- [B1-v] the peer's discriminating test: WHO OWNS the indicator's ControlTerminal?",
          flush=True)
    panel_i = next((i for i, r in enumerate(prows) if r.get("uid") == IND_CONTROL_UID), None)
    ctrows, cterr = safe("[B1-v] report_all('ControlTerminal')",
                         lambda: g.report_all(WORK, "ControlTerminal"), [])
    K["control_terminal_census_rows"] = len(ctrows or [])
    fact("[B1-v] panel row index of control uid %d = %r (gates use the UID, never this index - peer §5)"
         % (IND_CONTROL_UID, panel_i))
    window = [r for r in (ctrows or []) if panel_i is not None and abs(r["i"] - panel_i) <= 2]
    for r in window:
        fact("[B1-v] ControlTerminal census row i=%r uid=%r owner_class=%r pos=%r"
             % (r["i"], r["uid"], r.get("owner"), r.get("pos")))
    ct_row = next((r for r in (ctrows or []) if r["i"] == panel_i), None)
    ct_uid = (ct_row or {}).get("uid")
    K["indicator_control_terminal_uid_by_index_alignment"] = ct_uid
    own, ownerr = safe("[B1-v] owner_of(#%r)" % ct_uid,
                       lambda: owner_of(WORK, int(ct_uid)) if ct_uid else None)
    K["indicator_control_terminal_owner"] = {"uid": ct_uid, "owner": own, "error_verbatim": ownerr,
                                             "caveat": ("owner_of is measured to answer with the PREVIOUS "
                                                        "query's object silently (53(d8)) - this reading is "
                                                        "reported alongside the census `owner` column, not "
                                                        "instead of it")}
    fact("[B1-v] *** the indicator's ControlTerminal (uid %r, by census-index alignment with panel row %r): "
         "census owner_class %r ; owner_of -> %r %s***"
         % (ct_uid, panel_i, (ct_row or {}).get("owner"), own, ("; ERROR " + ownerr + " ") if ownerr else ""))
    owner_uid = own[1] if isinstance(own, (list, tuple)) and len(own) > 1 else None
    gate("A5 *** the indicator's ControlTerminal is owned by Diagram #%d - cycle 59's move_in still holds "
         "on this bed (peer c65-row2-wireind §4.1; NOT fatal, the brief's abort clauses are ExecState-based)"
         " ***" % D639, owner_uid == D639,
         "uid %r ; owner_of %r ; census owner_class %r" % (ct_uid, own, (ct_row or {}).get("owner")))

    # ---- (vi) the 'index' LABEL CENSUS, BEFORE (peer §4.2)
    print("\n---------- [B1-vi] the %r LABEL CENSUS, BEFORE the call (peer c65-row2-wireind §4.2)"
          % COLLIDING_LABEL, flush=True)
    before_rows = label_census(WORK, d639, "[B1-vi] BEFORE")
    K["label_census_before"] = before_rows
    gate("A6 the %r label census found MORE THAN ONE candidate (the hazard is real and now enumerated)"
         % COLLIDING_LABEL, len(before_rows) > 1, "%d row(s)" % len(before_rows))
    dump()
    return d639, hints, src_idx_in_class, (sloc.get("found") or {}).get("nodes_index"), before_rows


# ============================================================ THE BUILD
def build():
    print("\n========== ROW 2's INDICATOR:  #%d t%d %r (SOURCE, bare)  ->  the EXISTING %r indicator "
          "(panel control uid %d, bare)   via wire_indicators(node_class=%r)"
          % (SRC_UID, SRC_TERM, SRC_TERM_NAME, IND_LABEL_RECORDED, IND_CONTROL_UID, SRC_CLASS), flush=True)
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
         "final cold Wire gate is therefore C0 + 1 = %r (the brief's 1907) ***"
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
    d639, hints, node_index, src_nodes_index, label_before = b1_measure()

    # ---------- [B2] THE CALL
    print("\n---------- [B2] wire_indicators: #%d t%d %r (SOURCE) -> the %r indicator, node_class=%r"
          % (SRC_UID, SRC_TERM, SRC_TERM_NAME, IND_LABEL_RECORDED, SRC_CLASS), flush=True)
    # peer c65-row2-wireind §5: re-read the diagram index IMMEDIATELY before the call (row 1 did,
    # diag_c64_s3b_row1.log:296) rather than trusting the literal 46, and echo back the uid the op will
    # actually resolve from IndexArray[node_index] - an ordinal into a traversal the wrapper does not own.
    d639 = live_d639("[B2] IMMEDIATELY before the call")
    K["d639_last"] = d639
    ia_rows, _iaerr = safe("[B2] report_all(%r) re-read" % SRC_CLASS,
                           lambda: g.report_all(WORK, SRC_CLASS), [])
    ia_echo = next((r["uid"] for r in (ia_rows or []) if r["i"] == node_index), None)
    K["indexarray_uid_at_node_index"] = ia_echo
    fact("[B2] *** ECHO: report_all(%r)[%r].uid = %r (must be %d - the ordinal the op will resolve) ***"
         % (SRC_CLASS, node_index, ia_echo, SRC_UID))
    gate("A7 the ordinal node_index=%r still resolves to uid %d immediately before the call"
         % (node_index, SRC_UID), ia_echo == SRC_UID, "%r" % (ia_echo,), fatal=True)
    wset_before, _wsb = wire_uid_set(WORK, "[B2] BEFORE")
    K["wire_indicators_call"] = ("g.wire_indicators(target, node_index=%r, src_terms=[%r], "
                                 "indicator_names=[%r], diagram_index=%r, node_class=%r)"
                                 % (node_index, SRC_TERM_NAME, IND_LABEL_RECORDED, d639, SRC_CLASS))
    fact("[B2] THE CALL: %s" % K["wire_indicators_call"])
    fact("[B2] a RAISE from this wrapper is a READING, not a verdict - it tests exec_state != 1 ABSOLUTELY "
         "(tools/gscript.py:1794-1797), a MEASURED defect that raised a FALSE failure in cycle 62. It is "
         "caught, printed verbatim, and the machine is measured afterwards. Nothing is reverted on the "
         "raise alone and tools/gscript.py is NOT edited.")
    nodes_before, _ = node_census(WORK, "[B2] before wire_indicators")
    w_before = g.count(WORK, "Wire")
    K["wire_before_call"] = w_before
    buf = io.StringIO()
    t0 = time.time()
    try:
        with contextlib.redirect_stdout(buf):
            dt = g.wire_indicators(WORK, node_index=node_index, src_terms=[SRC_TERM_NAME],
                                   indicator_names=[IND_LABEL_RECORDED], diagram_index=d639,
                                   node_class=SRC_CLASS)
        K.update({"wire_indicators_returned": dt, "wire_indicators_raise_verbatim": ""})
    except Exception as e:                                                         # noqa: BLE001
        K.update({"wire_indicators_returned": None,
                  "wire_indicators_raise_verbatim": "%s: %s" % (type(e).__name__, str(e)[:600])})
    K["wire_indicators_cost_s"] = round(time.time() - t0, 2)
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    fact("[B2] wire_indicators returned %r (%.2f s) ; RAISE VERBATIM: %r"
         % (K.get("wire_indicators_returned"), K["wire_indicators_cost_s"],
            K.get("wire_indicators_raise_verbatim")))
    gate("B the wire_indicators call returned WITHOUT a raise",
         not K.get("wire_indicators_raise_verbatim"), "%r" % (K.get("wire_indicators_raise_verbatim"),))
    K["counts_after_call"] = counts(WORK, "[B2] after wire_indicators (before any purge)")
    K["exec_state_after_call_before_purge"] = read_es("[B2] after wire_indicators, BEFORE the purge", WORK)
    dump()

    # ---------- [B2b] THE PURGE (55(c))
    print("\n---------- [B2b] the census diff and the junk purge (55(c)) - BY UID", flush=True)
    fact("[B2b] row 1's census diff after wire_indicators was `Node 631 -> 631 ; 0 new uid(s): []` "
         "(diag_c64_s3b_row1.log:303), so ZERO purges is the EXPECTED outcome here; the purge is armed "
         "anyway (the brief mandates 55(c)) and reports whatever it finds.")
    fact("[B2b] PEER OBJECTION RECORDED, NOT ACTED ON (c65-row2-wireind §4): \"do not purge after this "
         "verb. The junk `Invoke` is a `move_in` artefact (diag_c64_s3b_row1.log:150, "
         "cycle59_s3a_recipe.log:85, 249), never a `wire_indicators` artefact; if a node does appear, "
         "deleting it destroys the only evidence of a new behaviour.\" The brief mandates the purge, so it "
         "stays armed - but census_and_purge PRINTS the new node's FULL terminal table and stores it in the "
         "JSON BEFORE any delete, so the evidence survives either way.")
    _after, prec = census_and_purge(WORK, nodes_before, "[B2] wire_indicators", hints)
    K["purge_after_call"] = prec
    gate("C the purge found NO new node that is not the measured junk shape",
         not prec["reported_not_deleted"],
         "new %r ; deleted %r ; reported-not-deleted %r"
         % (prec["new_uids"], [d["uid"] for d in prec["deleted"]],
            [d["uid"] for d in prec["reported_not_deleted"]]))
    es1 = read_es("[B2b] after the purge", WORK)
    K["exec_state_after_purge"] = es1
    K["counts_after_purge"] = counts(WORK, "[B2b] after the purge")
    gate("D *** ExecState == 1 after wire_indicators and the purge ***", es1 == 1, "%r" % (es1,))
    if es1 != 1:
        stop_report("D_exec_state_after_purge",
                    "ExecState is %r after wire_indicators and the purge, not 1; nothing is saved" % (es1,))

    # ---------- [B2c] the in-memory readback
    print("\n---------- [B2c] the in-memory readback: the source terminal, the panel row, the Local",
          flush=True)
    src_tt = terms_at(WORK, d639, src_nodes_index, SRC_UID, "[B2c] #%d the source" % SRC_UID)
    K["src_after"] = src_tt
    st1 = next((t for t in src_tt.get("terminals", []) if t["i"] == SRC_TERM), {})
    prows2, _pe2 = panel_all(WORK, "[B2c]")
    irow2 = panel_row(prows2, IND_CONTROL_UID)
    K["indicator_panel_row_after"] = irow2
    new_wire = st1.get("wire")
    K["new_wire_uid"] = new_wire
    fact("[B2c] the new wire: #%d t%d wire %r  |  panel control %d row %r  ->  SAME uid: %r"
         % (SRC_UID, SRC_TERM, new_wire, IND_CONTROL_UID, irow2,
            bool(new_wire) and new_wire == (irow2 or {}).get("wire")))
    gate("E ONE wire uid at BOTH ends (in memory): #%d t%d and panel control %d"
         % (SRC_UID, SRC_TERM, IND_CONTROL_UID),
         bool(new_wire) and new_wire == (irow2 or {}).get("wire"),
         "source %r ; panel row %r" % (st1, irow2))
    wafter = (K.get("counts_after_purge") or {}).get("Wire")
    gate("E2 the Wire census went C0 %r -> %r (delta 1: a MINT on a bare source, row 1's case)"
         % (C0, wafter), wafter == C0 + 1, "C0 %r -> %r" % (C0, wafter))
    # peer §5: a UID-SET diff, not just a count - `1906 -> 1907` is satisfied by a tunnel-crossing build too
    wset_after, _wsa = wire_uid_set(WORK, "[B2c] AFTER")
    minted = sorted(wset_after - wset_before)
    vanished = sorted(wset_before - wset_after)
    K["wire_uid_set_diff"] = {"minted": minted, "vanished": vanished,
                              "before": len(wset_before), "after": len(wset_after)}
    fact("[B2c] *** WIRE UID SET DIFF: %d minted %r ; %d vanished %r ***"
         % (len(minted), minted, len(vanished), vanished))
    gate("E2b *** EXACTLY ONE Wire uid was MINTED, none vanished, and the minted uid IS the wire at both "
         "ends (%r) - not an EXTENSION of a pre-existing net (tools/gscript.py:1765-1770) ***" % (new_wire,),
         len(minted) == 1 and not vanished and minted[:1] == [new_wire],
         "minted %r ; vanished %r ; new_wire %r" % (minted, vanished, new_wire))
    ltafter = (K.get("counts_after_purge") or {}).get("LoopTunnel")
    ltbefore = (K.get("counts_baseline") or {}).get("LoopTunnel")
    gate("E2c the LoopTunnel census did NOT move (%r -> %r ; the recorded value is %d) - no structure "
         "boundary was crossed (peer §3)" % (ltbefore, ltafter, LOOPTUNNEL_RECORDED),
         ltafter == ltbefore and ltafter == LOOPTUNNEL_RECORDED, "%r -> %r" % (ltbefore, ltafter))
    # peer §4.2: the 'index' label census AFTER - exactly ONE row may change, and it must be control 23525
    print("\n---------- [B2c] the %r LABEL CENSUS, AFTER the call (peer c65-row2-wireind §4.2)"
          % COLLIDING_LABEL, flush=True)
    label_after = label_census(WORK, d639, "[B2c] AFTER")
    K["label_census_after"] = label_after
    kb, ka = label_census_key(label_before), label_census_key(label_after)
    moved = sorted(k for k in set(kb) | set(ka) if kb.get(k) != ka.get(k))
    K["label_census_rows_that_moved"] = [{"key": list(k), "before": kb.get(k), "after": ka.get(k)}
                                         for k in moved]
    fact("[B2c] *** THE %r ROWS THAT CHANGED: %r ***"
         % (COLLIDING_LABEL, K["label_census_rows_that_moved"]))
    gate("E5 *** EXACTLY ONE %r-labelled row changed, and it is panel control %d - no co-labelled Local, "
         "Case terminal or Index Array terminal moved ***" % (COLLIDING_LABEL, IND_CONTROL_UID),
         len(moved) == 1 and moved[0] == (IND_CONTROL_UID, None),
         "%d changed: %r" % (len(moved), K["label_census_rows_that_moved"]))
    lloc2, lrows2 = node_view(WORK, LOCAL_UID, hints, "[B2c] the Local #%d" % LOCAL_UID)
    lrow2 = lrows2[0] if lrows2 else {}
    K["local_after"] = {"found": lloc2.get("found"), "terminals": lrows2}
    gate("E3 *** IN MEMORY: the Local #%d is NOT the thing that got wired - its terminal still carries "
         "wire %d, not the new wire %r ***" % (LOCAL_UID, CASE_T2_WIRE, new_wire),
         lrow2.get("wire") == CASE_T2_WIRE and lrow2.get("wire") != new_wire, "%r" % (lrow2,))
    t637_1 = loop637(WORK, "[B2c] AFTER", loop_hints)
    gate("E4 #%d is still at %r (no tunnel was created, 50(e))" % (LOOP11_UID, list(t637_0)),
         list(t637_1) == list(t637_0), "%r -> %r" % (list(t637_0), list(t637_1)))
    dump()

    # ---------- [B3] SAVE
    print("\n---------- [B3] SAVE the finished row", flush=True)
    sv = save_artefact("B3", FINAL_PATH, BED_MD5, "the BED D1_s3b_row2_20260921_151221.vi")
    if not sv.get("exists"):
        stop_report("B3_save", "the save left no file on disk")
    return FINAL_PATH


# ============================================================ the ORDERED `Broken?` pass (42(b)) - LAST
def ordered_pass(target, d639, new_wire, rc):
    """The ONLY ordered `Wire.Broken?` reader this fleet owns is the 6371004 property embedded in
    OpConnectNested_v0/v1, and it answers about the wire hanging off the SINK terminal it was handed - which
    means the sink must be addressable as Diagram[d].Nodes[n].Terminals[t]. Whether the new net HAS such a
    sink is decided by the reverse census, off the machine, not assumed here."""
    P = K.setdefault("ordered_pass", {})
    P["target"] = target
    P["note"] = ("LAST, after the cold reopen only (42(b), 52(f)). NOTHING is saved after this point; the "
                 "in-memory VI is discarded. The idempotent re-connect is how the op's `Broken?` read is "
                 "made to answer about the EXISTING wire. The ITEM terminal is `Broken?`; `Is Broken?` is "
                 "only the panel label (55(d)).")
    node_sinks = [m for m in (rc.get("sinks") or []) if not m.get("panel_row")]
    P["nodes_addressable_sinks_on_the_new_net"] = node_sinks
    if not node_sinks:
        P["not_attempted_because"] = (
            "the new net's ONLY sink is panel control %d, whose terminal is a `ControlTerminal` - class "
            "`Terminal`, not `Node` - and diag_c65_s3b_row2b.log:208 MEASURED that no ControlTerminal "
            "appears in Diagram #%d's Nodes[] list (116 uids INTERSECT 75 uids = 0). Both ordered readers "
            "this fleet owns (connect_nested_v1, connect_from_wire) address their SINK as "
            "Diagram[d].Nodes[n].Terminals[t], so an ordered `Broken?` on wire %r is NOT REACHABLE without "
            "a new op or a new verb, and this dispatch forbids both."
            % (IND_CONTROL_UID, D639, new_wire))
        fact("[L] *** THE ORDERED `Broken?` ON THE NEW WIRE IS NOT REACHABLE: %s ***"
             % P["not_attempted_because"])
        fact("[L] What DOES stand in its place, and is strictly stronger about the whole file: the COLD "
             "`ExecState` == 1 read above is the compiler's verdict that NO wire in the VI is broken. The "
             "ordered pass below is run on wire %d - row 2's FIRST-half connect wire, whose sink #%d t%d IS "
             "Nodes[]-addressable - so this artefact still gets one ordered reading."
             % (CASE_T2_WIRE, CASE_UID, CASE_T2))
    else:
        P["node_sink_chosen"] = node_sinks[0]

    # the ordered read on wire 23540 - the pair that IS addressable (Local #23523 SOURCE -> #10407 t2 SINK)
    sink_loc = find_node(target, CASE_UID, [d639, TOP], "[L] #%d" % CASE_UID)
    src_loc = find_node(target, LOCAL_UID, [d639, TOP], "[L] the Local #%d" % LOCAL_UID)
    sink_i = (sink_loc.get("found") or {}).get("nodes_index")
    sink_d = (sink_loc.get("found") or {}).get("diagram_index")
    src_i = (src_loc.get("found") or {}).get("nodes_index")
    src_d = (src_loc.get("found") or {}).get("diagram_index")
    P["call"] = ("connect_nested_v1(target, %r, %r, %r, %r, %r, 0) - IDEMPOTENT re-connect of the EXISTING "
                 "wire %d; wire_delta must be 0" % (sink_d, sink_i, CASE_T2, src_d, src_i, CASE_T2_WIRE))
    fact(P["call"])
    if sink_i is None or src_i is None:
        P["l2_not_attempted_because"] = "an endpoint is not addressable on the reopened file"
        gate("L the ordered `Broken?` pass", False, "NOT ATTEMPTED: %s" % P["l2_not_attempted_because"])
        return
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            odw, oes, oerr = CONNECT_V1(target, sink_d, sink_i, CASE_T2, src_d, src_i, 0, V1_LABELS)
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
    gate("L *** the ORDERED `Broken?` reads False on wire %d, row 2's first-half connect wire (the new "
         "indicator wire %r has no Nodes[]-addressable sink - see the FACT above) ***"
         % (CASE_T2_WIRE, new_wire),
         ib is False and rd.get("UID 2") == CASE_T2_WIRE,
         "Broken? %r on wire %r ; wire_delta %r" % (ib, rd.get("UID 2"), P.get("wire_delta")))
    read_es("[L] after the Broken? read (SUSPECT, NAMES.md:912-918; every save is already done)", target)


# ============================================================ MAIN
def main():
    print("=== diag_c65_s3b_row2c  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== cycle 65 material #3 part B: feed S3b ROW 2's EXISTING 'index' indicator (panel control "
          "%d) from #%d t%d 'element' with wire_indicators(node_class='IndexArray'), purge (55(c)), save, "
          "restart, cold-verify, ordered Broken? LAST." % (IND_CONTROL_UID, SRC_UID, SRC_TERM), flush=True)
    print("=== NO g.open_panel, NO move_in, NO allow_broken, NO gui_save, NO GUI, NO new op, NO new verb, "
          "NO edit to tools/gscript.py or any gate file. STRUCTURAL, NEVER FUNCTIONAL (34(f)).", flush=True)

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

    # ---------- [K] the COLD reopen in a freshly restarted LabVIEW
    print("\n========== [K] RESTART, then COLD-open the artefact", flush=True)
    C0 = R.get("C0_wire_census_of_the_bed")
    if final and os.path.exists(final):
        D.fresh("[K] RESTART before the cold reopen")
        R["handles"]["after_cold_restart"] = labview_handles()
        es_cold = read_es("[K] COLD, freshly restarted LabVIEW, %s" % os.path.basename(final), final)
        R["cold_exec_state"] = es_cold
        gate("K *** THE COLD READING of %s: ExecState 1 is the artefact's pass criterion ***"
             % os.path.basename(final), es_cold == 1, "ExecState %r" % (es_cold,))
        cf = probe("[K] the artefact, re-read", final)
        R["cold_md5"] = cf.get("md5")
        cc = counts(final, "[K] COLD")
        R["cold_counts"] = cc
        dump()
        want_wire = (C0 + 1) if isinstance(C0, int) else None
        gate("K2 *** THE COLD Wire census is C0 + 1 = %r (the brief's %d) ***"
             % (want_wire, WIRE_FINAL_EXPECTED),
             cc.get("Wire") == want_wire and cc.get("Wire") == WIRE_FINAL_EXPECTED,
             "Wire %r ; C0 %r ; full counts %r" % (cc.get("Wire"), C0, cc))
        base = K.get("bed_censuses_measured", {})
        gate("K2b the other COLD censuses are unchanged from the bed: Node %r, ControlTerminal %r, Local %r"
             % (base.get("Node"), base.get("ControlTerminal"), base.get("Local")),
             cc.get("Node") == base.get("Node") and cc.get("ControlTerminal") == base.get("ControlTerminal")
             and cc.get("Local") == base.get("Local"), "%r" % (cc,))
        gate("K2d COLD: the LoopTunnel census is still %d (no boundary crossed, peer c65-row2-wireind §3)"
             % LOOPTUNNEL_RECORDED, cc.get("LoopTunnel") == LOOPTUNNEL_RECORDED,
             "LoopTunnel %r" % (cc.get("LoopTunnel"),))
        cd639, _ce = safe("[K] diag_index(#639) COLD", lambda: diag_index(final, D639))
        cd686, _ce2 = safe("[K] diag_index(#686) COLD", lambda: diag_index(final, SIBLING_DIAG_UID))
        R["cold_d639"] = cd639
        t637_cold = loop637(final, "[K] COLD", [cd686, TOP, cd639])
        gate("K2c #%d is at the %r baseline on the COLD artefact (no tunnel, 50(e))"
             % (LOOP11_UID, K.get("loop637_baseline_measured")),
             list(t637_cold) == K.get("loop637_baseline_measured"), "%r" % (t637_cold,))

        # the two far ends, read off the COLD file
        sloc_c, srows_c = node_view(final, SRC_UID, [cd639, TOP], "[K] COLD #%d" % SRC_UID)
        st1_c = next((t for t in srows_c if t["i"] == SRC_TERM), {})
        cp, _cpe = panel_all(final, "[K] COLD panel")
        R["cold_panel_rows"] = len(cp)
        iprow = panel_row(cp, IND_CONTROL_UID)
        R["cold_indicator_panel_row"] = iprow
        new_wire = st1_c.get("wire")
        R["cold_new_wire_uid"] = new_wire
        R["cold_far_ends"] = {"src_t1": st1_c, "src_found": (sloc_c or {}).get("found"),
                              "indicator_panel_row": iprow}
        fact("[K] COLD FAR END: #%d t%d %r wire %r  <->  panel control %d row %r"
             % (SRC_UID, SRC_TERM, st1_c.get("name"), new_wire, IND_CONTROL_UID, iprow))
        gate("K3 *** COLD: ONE wire uid at BOTH ends of #%d t%d -> panel control %d ***"
             % (SRC_UID, SRC_TERM, IND_CONTROL_UID),
             bool(new_wire) and new_wire == (iprow or {}).get("wire"),
             "source %r ; panel row %r" % (st1_c, iprow))
        gate("K3b COLD: all %d panel rows read back" % CT_RECORDED, len(cp) == CT_RECORDED,
             "%d panel rows" % len(cp))

        cloc_c, crows_c = node_view(final, CASE_UID, [cd639, TOP], "[K] COLD #%d" % CASE_UID)
        ct2_c = next((t for t in crows_c if t["i"] == CASE_T2), {})
        lloc_c, lrows_c = node_view(final, LOCAL_UID, [cd639, TOP], "[K] COLD the Local #%d" % LOCAL_UID)
        lfar = lrows_c[0] if lrows_c else {}
        R["cold_case_t2"] = {"case_t2": ct2_c, "local_terminal": lfar,
                             "local_found": (lloc_c or {}).get("found")}
        fact("[K] COLD: #%d t%d wire %r  |  the Local #%d t0 %r wire %r"
             % (CASE_UID, CASE_T2, ct2_c.get("wire"), LOCAL_UID, lfar.get("name"), lfar.get("wire")))
        gate("K5 COLD: row 2's FIRST half still holds - #%d t%d carries wire %d and the Local #%d is at the "
             "far end" % (CASE_UID, CASE_T2, CASE_T2_WIRE, LOCAL_UID),
             ct2_c.get("wire") == CASE_T2_WIRE and lfar.get("wire") == CASE_T2_WIRE,
             "case t%d %r ; local %r" % (CASE_T2, ct2_c, lfar))
        dump()

        # K4 - THE LABEL-COLLISION GATE
        print("\n---------- [K4] the REVERSE CENSUS of the new net (every node of #%d, every panel row) - "
              "THE LABEL-COLLISION GATE" % D639, flush=True)
        rc = reverse_census(final, new_wire, cd639, "[K4]")
        one_src = rc["source_count"] == 1
        sink_rows = [m for m in rc["sinks"] if m.get("panel_row")]
        sink_is_ctl = len(sink_rows) == 1 and sink_rows[0]["node_uid"] == IND_CONTROL_UID
        local_off = not rc.get("local_23523_on_this_net")
        gate("K4 *** THE LABEL-COLLISION GATE: EXACTLY ONE source on the new net, its sink is panel control "
             "%d, and the Local #%d is NOT on it ***" % (IND_CONTROL_UID, LOCAL_UID),
             one_src and sink_is_ctl and local_off and not rc["scan_stopped"],
             "sources %d %r ; panel sinks %r ; Local on the net %r ; scan_stopped %r"
             % (rc["source_count"], rc["sources"], sink_rows, rc.get("local_23523_on_this_net"),
                rc["scan_stopped"]))
        gate("K4b that one source is #%d t%d %r" % (SRC_UID, SRC_TERM, SRC_TERM_NAME),
             one_src and rc["sources"][0].get("node_uid") == SRC_UID
             and rc["sources"][0].get("terminal") == SRC_TERM,
             "%r" % (rc["sources"],))
        gate("K4c COLD: the indicator's own panel row carries the new wire %r" % (new_wire,),
             bool(iprow) and bool(new_wire) and iprow.get("wire") == new_wire, "row %r" % (iprow,))
        dump()

        print("\n========== [L] the ORDERED `Wire.Broken?` pass (42(b), 55(d)) - LAST, nothing is saved "
              "after this point", flush=True)
        ordered_pass(final, cd639, new_wire, rc)
        close_quietly(final)
    else:
        for nm in ("K *** THE COLD READING ***", "K2 the COLD Wire census", "K3 ONE wire uid at both ends",
                   "K4 THE LABEL-COLLISION GATE", "L the ORDERED `Broken?` read"):
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
        print(("  %-24s Node %r -> %r -> %r ; new %r ; deleted %r ; reported-not-deleted %r"
               % (p["tag"], p["node_count_before"], p["node_count_after"], p["node_count_after_purge"],
                  p["new_uids"], [d["uid"] for d in p["deleted"]],
                  [d["uid"] for d in p["reported_not_deleted"]]))
              .encode("ascii", "replace").decode("ascii"), flush=True)

    print("\n=== THE WIRE ARITHMETIC (55(f))", flush=True)
    print("  C0 (bed) %r -> after wire_indicators %r -> after the purge %r -> COLD %r  (want C0 + 1 = %r)"
          % (C0, (K.get("counts_after_call") or {}).get("Wire"),
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
