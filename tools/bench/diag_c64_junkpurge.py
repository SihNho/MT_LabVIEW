"""diag_c64_junkpurge - cycle 64 material #4. ONE DELETE-BY-UID SEPARATES THE TWO SURVIVING EXPLANATIONS.

PURE MEASUREMENT. Nothing is built, no VI artefact is saved, no route is chosen or recommended. Every
target is a scratch duplicate created and deleted inside this run; `g.save` is neither imported nor called.

THE QUESTION (judgement, cycle 64, from tools/bench/diag_c64_readerfree.log, 23 pass / 0 fail)
  A reader-free edit (`connect_terminals` -> OpConnect_v0) leaves `ExecState` 1 -> 1. `connect_nested_v1`
  gives 1 -> 0 on the SAME idempotent pair. But those two arms differ in TWO properties at once: the second
  op carries the `Broken?` reader (Property #242) AND it left `Node` 2 -> 3, i.e. a junk object on the
  TARGET. Cycle 64 dispatch #1's ARM C (`set_node_label`, no wire touched) has the same shape: `Node`
  630 -> 631, `ExecState` 1 -> 0. Cycle 62's `move_in` left a junk `Invoke` #9317 and purged it.
  A junk node whose required inputs are unwired does not PERTURB a reading - it genuinely BREAKS the VI.
  So: identify the object the op leaves behind, read its terminals in full, delete it BY UID, and read
  `ExecState` again. NO value is predicted for that reading; the reading IS the measurement.

WHAT ALREADY EXISTS AND IS REUSED, NOT REBUILT (checked before writing a line of this file):
  tools/bench/diag_c64_readerfree.py    the gate/fact/probe/read_es/safe/drop_scratch skeleton, the md5-pin
                                        block, the leg shape - reused verbatim in structure
  tools/bench/diag_c62_negctrl.py       `node_on_639`, the uid-echo resolution of #10407/#10686 on Diagram
                                        #639 - reused, minus its `g.open_panel` call
  tools/gscript.py:488 report_all / :587 node_labels / :870 node_terms / :925 node_terms_uid / :1005 count /
                  :1017 uids / :1977 exec_state / :2275 delete_object / :1257 close_panel / :233 ref_counts
                                        the read-only census verbs AND the existing delete - NO new verb
  tools/recipes/build_d1_v0.py:357 diag_index          Diagram uid -> Traverse index
  tools/recipes/build_opconnectnested_v1.py:418 connect_nested_v1    the op under test
  tools/hash_probe.py probe / tools/bench/bench_prep.py labview_handles
  DELETE BY UID is `report_all(cls) -> .index(uid) -> delete_object(cls, idx)`, the shape cycle 58 used and
  tools/bench/build_timing_harnesses.py:27 already carries. It is NOT built as a new verb here; it is three
  lines in this file, and `delete_object(verify=True)` returns the uid set that actually disappeared, which
  is gated against the uid asked for.

FORBIDDEN AND ABSENT, by inspection and by tools/bench/c60c_astcheck.py:
  no save of any VI, NO `g.open_panel` CALL ANYWHERE IN THIS FILE (dispatch #2's poison), no `allow_broken`,
  no `gui_save`, no GUI action, no new op, no new gscript verb, no edit to tools/gscript.py, no cast, no
  splice (51(h)), no recipe, nothing written under tools/recipes/, no VI run (34(f)), no motor/ASI/camera
  (rig 조립/ASSEMBLED - nothing is touched), no new process device. retrospective.py / audit_cycle.py /
  violations.py / doc_ingest.py / prior_art_review.py are NOT run (54(a)). docs/cycle27-plan.md and
  STATUS.md's `## NEXT` are not edited.
  ⚠️ REPORTED, NOT DECIDED HERE: an EDIT is silently declined on a target that is not panel-loaded, so
  `connect_nested_v1` and `delete_object` BOTH call `g.ensure_loaded` INTERNALLY (gscript.py:1268-1337 ->
  open_panel). This file never calls it. No scratch path is ever removed-and-replaced while LabVIEW holds
  it (archive/peer/2026-09-21-c64-openpanel-cap.md: that is the live cause of run 2's stall); every scratch
  is a copy2 to a FRESH stamped name LabVIEW has never seen, and it is deleted once, at the end of its leg.

PREDICTION CONTRACT (a failed prediction here is a REVIEW trigger, not a retry)
  L1_a  on a scratch of claudeDev\\OpReport_v0.vi the bed pair still echoes its own uids at both ends:
        wire 467, 'Open VI Reference' Nodes[0].Terminals[1] 'vi reference' SOURCE -> 'Traverse for
        GObjects.vi' Nodes[1].Terminals[11] 'VI Refnum' SINK
  L1_b  ONE idempotent connect_nested_v1 on that pair: wire_delta 0 and the Wire census unchanged
  L1_c  EXACTLY ONE new Node uid appears (dispatch #3 measured Node 2 -> 3). Its uid, class, label, owning
        diagram and FULL terminal table are reported whatever they are
  L1_d  that node is deleted BY UID (wires on it first, by uid) and `delete_object` reports exactly that
        uid gone
  L1_e  *** THE READING: ExecState after the delete, plus three bare re-reads ~2 s apart. NO VALUE IS
        PREDICTED - 0 and 1 are both results and the gate records which ***
  L2_a  a scratch of claudeDev\\D1_s3a_focus_ind.vi opens COLD at ExecState 1, Node 630 / Wire 1905 /
        ControlTerminal 116
  L2_b  #10407 and #10686 resolve on Diagram #639 (traverse 46) as Nodes[24] / Nodes[25], uid-echoed, and
        #10407 t0 carries wire 10799
  L2_c  connect_nested_v1(46,24,0,46,25,0): wire_delta 0, Wire 1905 -> 1905
  L2_d  EXACTLY ONE new Node uid appears; uid, class, label, owning diagram and full terminal table reported
  L2_e  it is deleted BY UID and `delete_object` reports exactly that uid gone
  L2_f  *** THE READING: ExecState after the delete plus three re-reads. NO VALUE IS PREDICTED ***
  L3    for BOTH legs the OWNING DIAGRAM of the new node is named by the same census that found it
        (top-level vs Diagram #639) - never by owner_of, which is measured to answer silently wrong (53(d8))
  Z     four md5 pins hold before AND after (ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind);
        OpConnectNested_v1.vi, OpCreateLocalRead_v0.vi and OpReport_v0.vi byte-unchanged; both scratches
        exists=False; refs opened == closed == 0 live; handles reported either side
"""
import contextlib
import io
import json
import os
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
import shutil                                                                      # noqa: E402
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
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
DONOR = os.path.join(g.CLAUDEDEV, "OpCreateLocalRead_v0.vi")
DONOR_MD5 = "f695d97a36ae127cd2dd3ca6b1fc1089"
OP_V1 = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")
OP_V1_MD5 = "b7a1bb56"                 # prefix; the full value is measured and pinned at run time
OP_BED = os.path.join(g.CLAUDEDEV, "OpReport_v0.vi")
OP_BED_MD5 = "2b21a1c1"                # prefix of the md5 dispatch #3 measured (2b21a1c10f895d7dad41037e20cd690a)

TOP = 0                                # Traverse "Diagram" index 0 = the top-level diagram
# LEG 1's bed pair, MEASURED by dispatch #3 (tools/bench/diag_c64_readerfree.log:115) and RE-VERIFIED here
# on the scratch before it is used. src = Nodes[0].Terminals[1] 'vi reference' ; sink = Nodes[1].Terminals[11]
L1_SRC_NODE, L1_SRC_TERM = 0, 1
L1_SINK_NODE, L1_SINK_TERM = 1, 11
L1_WIRE_PIN = 467
# LEG 2's pair, the cycle-62 negative control's own call: connect_nested_v1(46, 24, 0, 46, 25, 0)
CASE_UID, SRC_UID, D639, WIRE_PIN = 10407, 10686, 639, 10799
L2_EXPECT_SINK_IDX, L2_EXPECT_SRC_IDX = 24, 25
L2_NODE_BASE, L2_WIRE_BASE, L2_CT_BASE = 630, 1905, 116

SCAN_BUDGET_S = 300.0                  # cap on the owning-diagram scan of a leg (bounded, reported)
RE_READS = 3
RE_READ_GAP_S = 2.0

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c64_junkpurge.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))
L1_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64JP1_%s.vi" % STAMP)
L2_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64JP2_%s.vi" % STAMP)
SCRATCHES = (L1_SCRATCH, L2_SCRATCH)

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 64 material #4: does the op's JUNK NODE break the VI, or does the reader perturb it?",
     "no_open_panel_call_in_this_file": True,
     "edits_reach_open_panel_through_the_wrapper": ("connect_nested_v1 and delete_object call "
                                                    "g.ensure_loaded internally (gscript.py:1268-1337); "
                                                    "this file never calls open_panel itself"),
     "no_save": "g.save is neither imported nor called anywhere in this file",
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True, "no_gui_action": True,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f))",
     "rig_state": "assembled - no motor, no ASI, no camera",
     "chooses_no_route": True, "recommends_no_route": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "leg1": {}, "leg2": {}, "leg3": {}}


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        dump()
        raise SystemExit(1)
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


def read_es(tag, target, leg):
    t0 = time.time()
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    row = {"step": len(R["exec_state_timeline"]) + 1, "leg": leg, "tag": tag, "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    fact("ExecState [%02d %s | %s] = %r   (+%.1f s, read cost %.2f s)"
         % (row["step"], leg, tag, es, row["t_since_start_s"], row["read_cost_s"]))
    return es


def safe(label, fn, default=None):
    """Run one read, record its error VERBATIM, never let it kill the run."""
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def drop_scratch(path, leg):
    """close_panel (NOT open_panel) then delete. A scratch never outlives the run."""
    if os.path.exists(path):
        safe("%s close_panel" % leg, lambda: g.close_panel(path))
        try:
            os.remove(path)
        except Exception as e:                                                     # noqa: BLE001
            fact("%s could not delete %s: %s" % (leg, os.path.basename(path), e))
    return os.path.exists(path)


# ===================================================================== censuses
def node_census(path, tag):
    """[{i, uid, class, pos}] for EVERY Node of the whole VI, in ONE op run (report_all)."""
    rows, err = safe("%s report_all('Node')" % tag, lambda: g.report_all(path, "Node"), [])
    out = [{"i": r["i"], "uid": r["uid"], "class": r["class"], "pos": r["pos"], "owner_class": r["owner"]}
           for r in (rows or [])]
    fact("%s node census: %d rows%s" % (tag, len(out), ("  [%s]" % err) if err else ""))
    return out, err


def wire_census(path, tag):
    rows, err = safe("%s report_all('Wire')" % tag, lambda: g.report_all(path, "Wire"), [])
    out = [{"uid": r["uid"], "pos": r["pos"]} for r in (rows or [])]
    fact("%s wire census: %d rows%s" % (tag, len(out), ("  [%s]" % err) if err else ""))
    return out, err


def counts(path, tag, classes=("Node", "Wire")):
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    fact("%s counts: %r" % (tag, rec))
    return rec


def owning_diagram(path, uid, hints, tag, budget_s=SCAN_BUDGET_S):
    """Which DIAGRAM lists `uid` in its Nodes[] - answered by the same census that finds the node.

    Deliberately NOT owner_of: archive/peer/2026-09-21-c62-movein-es0.md section 5 caught owner_of
    answering with the PREVIOUS query's object, silently (Pre-decided 53(d8)). `hints` are tried first
    (top level, and Diagram #639's traverse index on leg 2); the rest of the diagrams follow, bounded.
    """
    t0 = time.time()
    rec = {"uid": uid, "hints": list(hints), "scanned": [], "found": None}
    diags, derr = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(path, "Diagram"), [])
    rec["diagram_rows"] = len(diags or [])
    rec["diagram_census_error"] = derr
    by_index = {d["i"]: d for d in (diags or [])}
    order = [i for i in hints if i in by_index] + [i for i in sorted(by_index) if i not in hints]
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
    fact("%s owning diagram of #%s: %r  (%d diagram(s) scanned of %d, %.1f s)"
         % (tag, uid, rec["found"], len(rec["scanned"]), rec["diagram_rows"], rec["scan_cost_s"]))
    return rec


def terms_of(path, diagram_index, nodes_index, expect_uid, tag):
    """The FULL terminal table of one node, with the node's own uid echoed back before it is believed."""
    rec = {"diagram_index": diagram_index, "nodes_index": nodes_index, "expected_uid": expect_uid}
    try:
        echo, rows = g.node_terms_uid(path, diagram_index, nodes_index)
        rec["uid_echo"] = echo
        rec["ok"] = (echo == expect_uid)
        rec["terminals"] = [{"i": t["i"], "name": t["name"], "is_source": t["is_source"],
                             "wire": t["wire"], "has_wire": bool(t["wire"]),
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


def purge(path, node_uid, term_rows, tag, leg):
    """Wires on the node first, BY UID, then the node itself, BY UID (cycle 58's ordering)."""
    rec = {"node_uid": node_uid, "wire_deletes": [], "node_delete": None}
    wire_uids = sorted({t["wire"] for t in term_rows if t.get("wire")})
    rec["wires_on_the_node"] = wire_uids
    fact("%s the new node #%s carries %d wire(s): %r" % (tag, node_uid, len(wire_uids), wire_uids))
    for w in wire_uids:
        rec["wire_deletes"].append(delete_by_uid(path, "Wire", w, tag))
        rec.setdefault("exec_state_after_each_wire", []).append(
            read_es("[%s] after deleting Wire #%s" % (leg, w), path, leg))
    rec["node_delete"] = delete_by_uid(path, "Node", node_uid, tag)
    return rec


def new_nodes(before, after):
    seen = {n["uid"] for n in before}
    return [n for n in after if n["uid"] not in seen]


def the_reading(path, leg, tag, rec):
    """ExecState immediately after the delete, then RE_READS bare re-reads ~RE_READ_GAP_S apart."""
    rec["exec_state_after_delete"] = read_es("[%s] immediately AFTER the delete-by-uid" % leg, path, leg)
    rec["re_reads"] = []
    for k in range(RE_READS):
        time.sleep(RE_READ_GAP_S)
        rec["re_reads"].append(read_es("[%s] bare re-read %d of %d (~%.0f s apart)"
                                       % (leg, k + 1, RE_READS, RE_READ_GAP_S), path, leg))
    fact("%s THE READING: ExecState after the delete %r, then %r"
         % (tag, rec["exec_state_after_delete"], rec["re_reads"]))
    return rec["exec_state_after_delete"]


# ===================================================================== LEG 1 - the op bed
def leg1():
    print("\n=== LEG 1  THE OP BED: a scratch duplicate of claudeDev\\OpReport_v0.vi, the SAME idempotent "
          "pair dispatch #3 used (wire %d)" % L1_WIRE_PIN, flush=True)
    a = R["leg1"]
    a["bed"] = OP_BED
    a["scratch"] = L1_SCRATCH
    try:
        shutil.copy2(OP_BED, L1_SCRATCH)
        a["cold_exec_state"] = read_es("[L1 1] the untouched scratch, cold", L1_SCRATCH, "L1")
        a["counts_before"] = counts(L1_SCRATCH, "L1 before")
        nodes_before, _ = node_census(L1_SCRATCH, "L1 before")
        wires_before, _ = wire_census(L1_SCRATCH, "L1 before")
        a["nodes_before"] = nodes_before
        a["wires_before"] = [w["uid"] for w in wires_before]

        a["pair_check"] = {
            "src": terms_of(L1_SCRATCH, TOP, L1_SRC_NODE, None, "L1 src"),
            "sink": terms_of(L1_SCRATCH, TOP, L1_SINK_NODE, None, "L1 sink")}
        src_row = next((t for t in a["pair_check"]["src"]["terminals"] if t["i"] == L1_SRC_TERM), {})
        sink_row = next((t for t in a["pair_check"]["sink"]["terminals"] if t["i"] == L1_SINK_TERM), {})
        a["pair_src_terminal"], a["pair_sink_terminal"] = src_row, sink_row
        gate("L1_a the bed pair is intact on the scratch: wire %d at BOTH ends, src is_source True"
             % L1_WIRE_PIN,
             src_row.get("wire") == L1_WIRE_PIN and sink_row.get("wire") == L1_WIRE_PIN
             and src_row.get("is_source") is True and sink_row.get("is_source") is False,
             "src %r ; sink %r" % (src_row, sink_row))

        es_pre = read_es("[L1 2] immediately BEFORE the idempotent connect_nested_v1", L1_SCRATCH, "L1")
        a["exec_state_before_connect"] = es_pre
        a["call"] = ("connect_nested_v1(target, sink_diag=%d, sink_node=%d, sink_term=%d, src_diag=%d, "
                     "src_node=%d, src_term=%d)"
                     % (TOP, L1_SINK_NODE, L1_SINK_TERM, TOP, L1_SRC_NODE, L1_SRC_TERM))
        fact("L1 THE ONE CALL: %s   (IDEMPOTENT - this pair is already joined by wire %d)"
             % (a["call"], L1_WIRE_PIN))
        buf = io.StringIO()
        t0 = time.time()
        try:
            with contextlib.redirect_stdout(buf):
                dw, es_c, err_c = CONNECT_V1(L1_SCRATCH, TOP, L1_SINK_NODE, L1_SINK_TERM, TOP,
                                             L1_SRC_NODE, L1_SRC_TERM, V1_LABELS)
            a["connect"] = {"wire_delta": dw, "exec_state_returned": es_c, "op_error": err_c,
                            "error_verbatim": ""}
        except Exception as e:                                                     # noqa: BLE001
            a["connect"] = {"wire_delta": None, "exec_state_returned": None, "op_error": None,
                            "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:400])}
        a["connect"]["call_cost_s"] = round(time.time() - t0, 2)
        a["op_stdout_verbatim"] = [ln.strip() for ln in buf.getvalue().rstrip().splitlines()]
        for ln in a["op_stdout_verbatim"]:
            print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
        fact("L1 connect result: %r" % (a["connect"],))

        a["exec_state_after_connect"] = read_es("[L1 3] immediately AFTER the connect", L1_SCRATCH, "L1")
        a["counts_after_connect"] = counts(L1_SCRATCH, "L1 after connect")
        nodes_after, _ = node_census(L1_SCRATCH, "L1 after connect")
        wires_after, _ = wire_census(L1_SCRATCH, "L1 after connect")
        a["nodes_after_connect"] = nodes_after
        a["wires_after_connect"] = [w["uid"] for w in wires_after]
        gate("L1_b the connect was IDEMPOTENT (wire_delta 0 and the Wire census unchanged)",
             a["connect"].get("wire_delta") == 0
             and a["counts_before"].get("Wire") == a["counts_after_connect"].get("Wire"),
             "wire_delta %r ; Wire %r -> %r" % (a["connect"].get("wire_delta"),
                                                a["counts_before"].get("Wire"),
                                                a["counts_after_connect"].get("Wire")))

        fresh = new_nodes(nodes_before, nodes_after)
        a["new_nodes"] = fresh
        fact("L1 THE CENSUS DIFF: %d new Node uid(s): %r"
             % (len(fresh), [(n["uid"], n["class"], n["pos"], n["owner_class"]) for n in fresh]))
        gate("L1_c exactly ONE new Node appeared and it is identified by uid",
             len(fresh) == 1, "Node %r -> %r ; new %r"
             % (a["counts_before"].get("Node"), a["counts_after_connect"].get("Node"),
                [n["uid"] for n in fresh]))
        if len(fresh) != 1:
            a["note"] = "the census diff did not isolate ONE node; nothing is deleted on this leg"
            the_reading(L1_SCRATCH, "L1", "L1 (no delete happened)", a)
            return
        nu = fresh[0]
        a["the_new_node"] = nu
        own = owning_diagram(L1_SCRATCH, nu["uid"], [TOP], "L1")
        a["owning_diagram"] = own
        R["leg3"]["leg1"] = own
        gate("L1_c2 the new node's OWNING DIAGRAM is named by the census that found it (not owner_of)",
             bool(own.get("found")), "%r" % (own.get("found"),))
        di = (own.get("found") or {}).get("diagram_index")
        ni = (own.get("found") or {}).get("nodes_index")
        a["terminal_table"] = (terms_of(L1_SCRATCH, di, ni, nu["uid"], "L1 NEW NODE")
                               if di is not None else {"terminals": [],
                                                       "error_verbatim": "no owning diagram found"})
        fact("L1 THE NEW NODE: uid #%s, class %r, label %r, pos %r, owner_class %r, %d terminal(s), "
             "%d of them wired"
             % (nu["uid"], nu["class"], (own.get("found") or {}).get("label"), nu["pos"],
                nu["owner_class"], len(a["terminal_table"].get("terminals", [])),
                sum(1 for t in a["terminal_table"].get("terminals", []) if t["has_wire"])))
        gate("L1_c3 the new node's FULL terminal table was read (every terminal, name, is_source, wire)",
             bool(a["terminal_table"].get("terminals")) or bool(a["terminal_table"].get("uid_echo")),
             "echo %r ; %d terminal(s) ; %r" % (a["terminal_table"].get("uid_echo"),
                                                len(a["terminal_table"].get("terminals", [])),
                                                a["terminal_table"].get("error_verbatim", "")))

        a["purge"] = purge(L1_SCRATCH, nu["uid"], a["terminal_table"].get("terminals", []), "L1", "L1")
        nd = a["purge"]["node_delete"]
        gate("L1_d the new node was deleted BY UID and delete_object reports exactly that uid gone",
             nd.get("gone") == [nu["uid"]] and not nd.get("still_present"),
             "gone %r (asked %r) ; error %r ; still present %r"
             % (nd.get("gone"), nu["uid"], nd.get("error_verbatim"), nd.get("still_present")))

        es_after = the_reading(L1_SCRATCH, "L1", "L1", a)
        a["counts_after_delete"] = counts(L1_SCRATCH, "L1 after delete")
        wires_end, _ = wire_census(L1_SCRATCH, "L1 after delete")
        a["wires_after_delete"] = [w["uid"] for w in wires_end]
        a["verdict_shape"] = {"cold": a.get("cold_exec_state"),
                              "before_connect": a.get("exec_state_before_connect"),
                              "after_connect": a.get("exec_state_after_connect"),
                              "after_delete": es_after, "re_reads": a.get("re_reads"),
                              "Wire": [a["counts_before"].get("Wire"),
                                       a["counts_after_connect"].get("Wire"),
                                       a["counts_after_delete"].get("Wire")],
                              "Node": [a["counts_before"].get("Node"),
                                       a["counts_after_connect"].get("Node"),
                                       a["counts_after_delete"].get("Node")]}
        gate("L1_e *** THE READING: ExecState %r (cold) -> %r (after connect) -> %r (after the junk purge) "
             "***" % (a.get("cold_exec_state"), a.get("exec_state_after_connect"), es_after),
             True, "%r" % (a["verdict_shape"],))
    except Exception as e:                                                         # noqa: BLE001
        a["leg_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        fact("LEG 1 ABORTED: %s" % a["leg_error_verbatim"])
        gate("L1_a the bed pair is intact on the scratch", False, a["leg_error_verbatim"])
    finally:
        a["scratch_exists"] = drop_scratch(L1_SCRATCH, "L1")
        gate("Z_3a the LEG 1 scratch is deleted in the same run", not a["scratch_exists"], L1_SCRATCH)


# ===================================================================== LEG 2 - the real bed
def node_on_639(path, d639, uid, tag):
    """Nodes[] position of `uid` on Diagram #639, VERIFIED by the node's own uid echo (negctrl's helper)."""
    rec = {"uid": uid}
    rows, err = safe("%s node_labels(%r)" % (tag, d639), lambda: g.node_labels(path, int(d639)), [])
    rec["nodes_on_639"] = len(rows or [])
    rec["node_labels_error"] = err
    n = next((i for i, r in enumerate(rows or []) if r["uid"] == uid), None)
    rec["nodes_index"] = n
    rec["label"] = next((r["label"] for r in (rows or []) if r["uid"] == uid), None)
    rec["terminals"] = []
    if n is not None:
        t = terms_of(path, int(d639), n, uid, "%s #%d" % (tag, uid))
        rec["uid_echo"] = t.get("uid_echo")
        rec["terminals"] = t.get("terminals", [])
    fact("%s #%d on Diagram #%d: Nodes[%r] label %r ; t0 %r"
         % (tag, uid, D639, n, rec.get("label"), next((t for t in rec["terminals"] if t["i"] == 0), None)))
    return rec


def leg2():
    print("\n=== LEG 2  THE REAL BED: a scratch duplicate of claudeDev\\D1_s3a_focus_ind.vi and the negative "
          "control's own call connect_nested_v1(46,24,0,46,25,0)", flush=True)
    a = R["leg2"]
    a["bed"] = S3A_ARTEFACT
    a["scratch"] = L2_SCRATCH
    try:
        shutil.copy2(S3A_ARTEFACT, L2_SCRATCH)
        a["cold_exec_state"] = read_es("[L2 1] the untouched scratch, cold", L2_SCRATCH, "L2")
        gate("L2_a the scratch opens COLD at ExecState 1", a["cold_exec_state"] == 1,
             "%r" % (a["cold_exec_state"],))
        a["counts_before"] = counts(L2_SCRATCH, "L2 before", ("Node", "Wire", "ControlTerminal"))
        gate("L2_a2 the baselines hold: Node %d / Wire %d / ControlTerminal %d"
             % (L2_NODE_BASE, L2_WIRE_BASE, L2_CT_BASE),
             a["counts_before"].get("Node") == L2_NODE_BASE
             and a["counts_before"].get("Wire") == L2_WIRE_BASE
             and a["counts_before"].get("ControlTerminal") == L2_CT_BASE,
             "%r" % (a["counts_before"],))
        nodes_before, _ = node_census(L2_SCRATCH, "L2 before")
        a["nodes_before_count"] = len(nodes_before)

        d639, derr = safe("L2 diag_index(#%d)" % D639, lambda: diag_index(L2_SCRATCH, D639))
        a["d639_traverse_index"] = d639
        a["d639_error"] = derr
        fact("L2 diag_index(#%d) RE-READ off the machine = %r" % (D639, d639))
        a["nodes_on_639_before"], _ = safe("L2 node_labels(#639) before",
                                           lambda: g.node_labels(L2_SCRATCH, int(d639)), [])
        a["nodes_on_639_before_uids"] = [r["uid"] for r in (a["nodes_on_639_before"] or [])]
        a["sink"] = node_on_639(L2_SCRATCH, d639, CASE_UID, "L2 SINK")
        a["src"] = node_on_639(L2_SCRATCH, d639, SRC_UID, "L2 SOURCE")
        gate("L2_b #%d and #%d resolve on Diagram #%d with their own uid echoed back, at Nodes[%d]/[%d]"
             % (CASE_UID, SRC_UID, D639, L2_EXPECT_SINK_IDX, L2_EXPECT_SRC_IDX),
             a["sink"].get("uid_echo") == CASE_UID and a["src"].get("uid_echo") == SRC_UID
             and a["sink"].get("nodes_index") == L2_EXPECT_SINK_IDX
             and a["src"].get("nodes_index") == L2_EXPECT_SRC_IDX,
             "sink Nodes[%r] echo %r ; source Nodes[%r] echo %r"
             % (a["sink"].get("nodes_index"), a["sink"].get("uid_echo"),
                a["src"].get("nodes_index"), a["src"].get("uid_echo")))
        if a["sink"].get("nodes_index") is None or a["src"].get("nodes_index") is None:
            a["note"] = ("the pair did not resolve on Diagram #%d, so NO connect was attempted and "
                         "nothing was deleted on this leg" % D639)
            fact("LEG 2 STOPS BEFORE THE CONNECT: %s" % a["note"])
            return
        st0 = next((t for t in a["sink"].get("terminals", []) if t["i"] == 0), {})
        sr0 = next((t for t in a["src"].get("terminals", []) if t["i"] == 0), {})
        a["case_t0_wire_before"] = st0.get("wire")
        gate("L2_b2 #%d t0 and #%d t0 BOTH already carry wire %d" % (CASE_UID, SRC_UID, WIRE_PIN),
             st0.get("wire") == WIRE_PIN and sr0.get("wire") == WIRE_PIN,
             "sink t0 %r ; source t0 %r" % (st0, sr0))

        es_pre = read_es("[L2 2] immediately BEFORE the idempotent connect_nested_v1", L2_SCRATCH, "L2")
        a["exec_state_before_connect"] = es_pre
        a["call"] = ("connect_nested_v1(target, %r, %r, 0, %r, %r, 0)"
                     % (d639, a["sink"].get("nodes_index"), d639, a["src"].get("nodes_index")))
        fact("L2 THE ONE CALL: %s   (IDEMPOTENT - this pair is already joined by wire %d)"
             % (a["call"], WIRE_PIN))
        buf = io.StringIO()
        t0 = time.time()
        try:
            with contextlib.redirect_stdout(buf):
                dw, es_c, err_c = CONNECT_V1(L2_SCRATCH, d639, a["sink"]["nodes_index"], 0,
                                             d639, a["src"]["nodes_index"], 0, V1_LABELS)
            a["connect"] = {"wire_delta": dw, "exec_state_returned": es_c, "op_error": err_c,
                            "error_verbatim": ""}
        except Exception as e:                                                     # noqa: BLE001
            a["connect"] = {"wire_delta": None, "exec_state_returned": None, "op_error": None,
                            "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:400])}
        a["connect"]["call_cost_s"] = round(time.time() - t0, 2)
        a["op_stdout_verbatim"] = [ln.strip() for ln in buf.getvalue().rstrip().splitlines()]
        for ln in a["op_stdout_verbatim"]:
            print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
        fact("L2 connect result: %r" % (a["connect"],))

        a["exec_state_after_connect"] = read_es("[L2 3] immediately AFTER the connect", L2_SCRATCH, "L2")
        a["counts_after_connect"] = counts(L2_SCRATCH, "L2 after connect",
                                           ("Node", "Wire", "ControlTerminal"))
        gate("L2_c the connect was IDEMPOTENT (wire_delta 0 and the Wire census unchanged)",
             a["connect"].get("wire_delta") == 0
             and a["counts_before"].get("Wire") == a["counts_after_connect"].get("Wire"),
             "wire_delta %r ; Wire %r -> %r" % (a["connect"].get("wire_delta"),
                                                a["counts_before"].get("Wire"),
                                                a["counts_after_connect"].get("Wire")))
        nodes_after, _ = node_census(L2_SCRATCH, "L2 after connect")
        fresh = new_nodes(nodes_before, nodes_after)
        a["new_nodes"] = fresh
        fact("L2 THE CENSUS DIFF: %d new Node uid(s): %r"
             % (len(fresh), [(n["uid"], n["class"], n["pos"], n["owner_class"]) for n in fresh]))
        gate("L2_d exactly ONE new Node appeared and it is identified by uid",
             len(fresh) == 1, "Node %r -> %r ; new %r"
             % (a["counts_before"].get("Node"), a["counts_after_connect"].get("Node"),
                [n["uid"] for n in fresh]))
        if len(fresh) != 1:
            a["note"] = "the census diff did not isolate ONE node; nothing is deleted on this leg"
            the_reading(L2_SCRATCH, "L2", "L2 (no delete happened)", a)
            return
        nu = fresh[0]
        a["the_new_node"] = nu
        hints = [int(d639)] if isinstance(d639, int) else []
        own = owning_diagram(L2_SCRATCH, nu["uid"], hints + [TOP], "L2")
        a["owning_diagram"] = own
        R["leg3"]["leg2"] = own
        gate("L2_d2 the new node's OWNING DIAGRAM is named by the census that found it (not owner_of)",
             bool(own.get("found")), "%r" % (own.get("found"),))
        di = (own.get("found") or {}).get("diagram_index")
        ni = (own.get("found") or {}).get("nodes_index")
        a["terminal_table"] = (terms_of(L2_SCRATCH, di, ni, nu["uid"], "L2 NEW NODE")
                               if di is not None else {"terminals": [],
                                                       "error_verbatim": "no owning diagram found"})
        fact("L2 THE NEW NODE: uid #%s, class %r, label %r, pos %r, owner_class %r, %d terminal(s), "
             "%d of them wired"
             % (nu["uid"], nu["class"], (own.get("found") or {}).get("label"), nu["pos"],
                nu["owner_class"], len(a["terminal_table"].get("terminals", [])),
                sum(1 for t in a["terminal_table"].get("terminals", []) if t["has_wire"])))
        gate("L2_d3 the new node's FULL terminal table was read (every terminal, name, is_source, wire)",
             bool(a["terminal_table"].get("terminals")) or bool(a["terminal_table"].get("uid_echo")),
             "echo %r ; %d terminal(s) ; %r" % (a["terminal_table"].get("uid_echo"),
                                                len(a["terminal_table"].get("terminals", [])),
                                                a["terminal_table"].get("error_verbatim", "")))

        a["purge"] = purge(L2_SCRATCH, nu["uid"], a["terminal_table"].get("terminals", []), "L2", "L2")
        nd = a["purge"]["node_delete"]
        gate("L2_e the new node was deleted BY UID and delete_object reports exactly that uid gone",
             nd.get("gone") == [nu["uid"]] and not nd.get("still_present"),
             "gone %r (asked %r) ; error %r ; still present %r"
             % (nd.get("gone"), nu["uid"], nd.get("error_verbatim"), nd.get("still_present")))

        es_after = the_reading(L2_SCRATCH, "L2", "L2", a)
        a["counts_after_delete"] = counts(L2_SCRATCH, "L2 after delete",
                                          ("Node", "Wire", "ControlTerminal"))
        a["sink_after"] = node_on_639(L2_SCRATCH, d639, CASE_UID, "L2 SINK after")
        st0b = next((t for t in a["sink_after"].get("terminals", []) if t["i"] == 0), {})
        a["case_t0_wire_after"] = st0b.get("wire")
        gate("L2_e2 #%d t0 still carries wire %d after the purge" % (CASE_UID, WIRE_PIN),
             st0b.get("wire") == WIRE_PIN, "before %r ; after %r"
             % (a.get("case_t0_wire_before"), a.get("case_t0_wire_after")))
        gate("L2_e3 the ControlTerminal census is unchanged across the whole leg (%d)" % L2_CT_BASE,
             a["counts_before"].get("ControlTerminal") == a["counts_after_delete"].get("ControlTerminal"),
             "%r -> %r -> %r" % (a["counts_before"].get("ControlTerminal"),
                                 a["counts_after_connect"].get("ControlTerminal"),
                                 a["counts_after_delete"].get("ControlTerminal")))
        a["verdict_shape"] = {"cold": a.get("cold_exec_state"),
                              "before_connect": a.get("exec_state_before_connect"),
                              "after_connect": a.get("exec_state_after_connect"),
                              "after_delete": es_after, "re_reads": a.get("re_reads"),
                              "Wire": [a["counts_before"].get("Wire"),
                                       a["counts_after_connect"].get("Wire"),
                                       a["counts_after_delete"].get("Wire")],
                              "Node": [a["counts_before"].get("Node"),
                                       a["counts_after_connect"].get("Node"),
                                       a["counts_after_delete"].get("Node")],
                              "ControlTerminal": [a["counts_before"].get("ControlTerminal"),
                                                  a["counts_after_delete"].get("ControlTerminal")],
                              "case_t0_wire": [a.get("case_t0_wire_before"), a.get("case_t0_wire_after")]}
        gate("L2_f *** THE READING: ExecState %r (cold) -> %r (after connect) -> %r (after the junk purge) "
             "***" % (a.get("cold_exec_state"), a.get("exec_state_after_connect"), es_after),
             True, "%r" % (a["verdict_shape"],))
    except SystemExit:
        raise
    except Exception as e:                                                         # noqa: BLE001
        a["leg_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        fact("LEG 2 ABORTED: %s" % a["leg_error_verbatim"])
        gate("L2_a the scratch opens COLD at ExecState 1", False, a["leg_error_verbatim"])
    finally:
        a["scratch_exists"] = drop_scratch(L2_SCRATCH, "L2")
        gate("Z_3b the LEG 2 scratch is deleted in the same run", not a["scratch_exists"], L2_SCRATCH)


# ===================================================================== main
def main():
    print("=== diag_c64_junkpurge  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== cycle 64 material #4: ONE delete-by-uid separates 'the reader perturbs the reading' from "
          "'the op's junk node breaks the VI'. PURE MEASUREMENT - nothing is built, no VI is saved.",
          flush=True)
    print("=== NO g.open_panel call appears in this file; the edits reach it only inside the wrappers' own "
          "ensure_loaded. No loaded path is ever removed-and-replaced.", flush=True)

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
    s3 = probe("Z0d D1_s3a_focus_ind.vi (FATAL pin, never written)", S3A_ARTEFACT)
    gate("Z_0d D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    dn = probe("Z0e the donor OpCreateLocalRead_v0.vi", DONOR)
    gate("Z_0e OpCreateLocalRead_v0.vi md5 == %s" % DONOR_MD5, dn.get("md5") == DONOR_MD5, dn.get("md5", "?"))
    v1 = probe("Z0f OpConnectNested_v1.vi (the op under test)", OP_V1)
    R["op_v1_md5_before"] = v1.get("md5")
    gate("Z_0f OpConnectNested_v1.vi md5 starts with %s" % OP_V1_MD5,
         str(v1.get("md5", "")).startswith(OP_V1_MD5), v1.get("md5", "?"))
    bd = probe("Z0g the LEG 1 bed OpReport_v0.vi", OP_BED)
    R["op_bed_md5_before"] = bd.get("md5")
    gate("Z_0g OpReport_v0.vi md5 starts with %s" % OP_BED_MD5,
         str(bd.get("md5", "")).startswith(OP_BED_MD5), bd.get("md5", "?"))

    # ---- the pre-batch restart (44(e))
    D.fresh("Z_R RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    for legfn in (leg1, leg2):
        try:
            legfn()
        finally:
            dump()

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
    z6 = probe("Z1g the LEG 1 bed OpReport_v0.vi after everything", OP_BED)
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    gate("Z_1b the donor OpCreateLocalRead_v0.vi is byte-unchanged", z4.get("md5") == DONOR_MD5,
         "%s" % (z4.get("md5"),))
    gate("Z_1c OpConnectNested_v1.vi is byte-unchanged across the run",
         z5.get("md5") == R.get("op_v1_md5_before"),
         "%r -> %r" % (R.get("op_v1_md5_before"), z5.get("md5")))
    gate("Z_1d the LEG 1 bed OpReport_v0.vi is byte-unchanged across the run",
         z6.get("md5") == R.get("op_bed_md5_before"),
         "%r -> %r" % (R.get("op_bed_md5_before"), z6.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z_1e refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    left = [p for p in SCRATCHES if os.path.exists(p)]
    gate("Z_1f EVERY scratch is gone (nothing is left on disk by this run)", not left,
         "still on disk: %r" % ([os.path.basename(p) for p in left],))

    print("\n=== THE COMPLETE TIMESTAMPED ExecState TIMELINE", flush=True)
    print("  %-4s %-4s %-58s %-12s %-10s" % ("step", "leg", "call / tag", "ExecState", "wall"), flush=True)
    for row in R["exec_state_timeline"]:
        print(("  %-4d %-4s %-58s %-12r %-10s" % (row["step"], row["leg"], row["tag"][:58],
                                                  row["exec_state"], row["wall_clock"]))
              .encode("ascii", "replace").decode("ascii"), flush=True)

    print("\n=== THE TWO LEGS SIDE BY SIDE", flush=True)
    print("  %-6s %-30s %-8s %-10s %-11s %-12s %s"
          % ("leg", "bed", "cold ES", "ES connect", "ES purge", "re-reads", "the new node"), flush=True)
    for key, bed in (("leg1", "OpReport_v0.vi"), ("leg2", "D1_s3a_focus_ind.vi")):
        a = R[key]
        nu = a.get("the_new_node") or {}
        own = (a.get("owning_diagram") or {}).get("found") or {}
        print(("  %-6s %-30s %-8r %-10r %-11r %-12r #%s %s on Diagram idx %r (uid #%s), %d terminal(s)"
               % (key.upper(), bed, a.get("cold_exec_state"), a.get("exec_state_after_connect"),
                  a.get("exec_state_after_delete"), a.get("re_reads"), nu.get("uid"), nu.get("class"),
                  own.get("diagram_index"), own.get("diagram_uid"),
                  len((a.get("terminal_table") or {}).get("terminals", []))))
              .encode("ascii", "replace").decode("ascii"), flush=True)

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
