"""diag_c62_s3b_movein - S3b ROW 1 ONLY, with the ONE new step 53(d-quad) added: move_in BEFORE the connect.

WHAT ALREADY EXISTS AND IS REUSED (checked before writing a line of this file)
  tools/bench/diag_c62_s3b_build.py   dispatch #3's scaffold, helpers and gate wording - reused verbatim in
                                      shape (node_table / panel_all / loop637_counts / delete_wire_uid /
                                      traverse_index_of / call_donor / t3_separator / ordered_pass)
  tools/recipes/build_d1_v0.py:318    `move_in(target, uid, dest_diagram_index, position)` - THE fleet's
                                      move-into-diagram verb, the same one S3a's boolean carrier used
                                      (tools/bench/diag_s58_boolwire.py:889, MOVE_POSITION (120,4000), with
                                      the junk-`Invoke` purge that move leaves behind)
  docs/toolkit-capabilities.md        `OpCreateLocalRead_v0.vi` (md5 f695d97a..., READ via `Write?`=False),
                                      `OpConnectNested_v1.vi` (the ONLY writer that reaches a SINK on a
                                      NESTED diagram; gscript.connect_terminals is top-level-only)
  grep "^def " tools/gscript.py       delete_object / wire_indicators / node_terms_uid / node_labels /
                                      panel_wiring / fp_labels / report_all / uids / count / exec_state /
                                      save / op / open_panel / close_panel
  NOTHING NEW IS BUILT: no op, no gscript verb, no recipe, no device, no edit to tools/gscript.py.

WHY THE SEQUENCE GAINS EXACTLY ONE STEP (docs/cycle27-plan.md Pre-decided 53(d-quad), judgement's decision)
  Dispatch #3 (tools/bench/diag_c62_s3b_build.log) ran row 1 clean to the connect and read ExecState 0 where 1
  was required. The cause is PLACEMENT: `OpCreateLocalRead_v0` puts the new Local on `TopLevelDiagram` #536,
  `Nodes[0]`, while `#10407` is on `Diagram #639` (traverse 46), so connect_nested_v1(sink_diag=46,...,
  src_diag=0,...) built a cross-diagram TUNNELLED path - wire_delta 3, op error '', and TWO DIFFERENT wire uids
  at the two ends (#10407 t0 -> 23508, Local t0 -> 23601). 50(e) forbids exactly that. So: move_in the Local
  onto Diagram #639 FIRST, then connect on one diagram.

THE SEQUENCE - ROW 1 ONLY, ROW 2 IS NOT ATTEMPTED
  1 delete_object(target,'Wire',<idx of uid 10799>)                     ExecState 0 EXPECTED
  2 OpCreateLocalRead_v0.vi, Write?=False (READ), bound to the EXISTING indicator 23555
  3 move_in(<the new Local> -> Diagram #639, (120,4000))  + purge the junk Invoke move_in leaves
  4 connect_nested_v1(Local SOURCE -> #10407 t0 SINK), then IMMEDIATELY the #637 census
  5 SAVE UNCONDITIONALLY  -> claudeDev\\D1_s3b_row1a_<stamp>.vi
  6 ONLY IF the live ExecState at step 4 is 1: wire_indicators re-feeds indicator 23555, the T3 separator
    runs, then SAVE UNCONDITIONALLY -> claudeDev\\D1_s3b_row1_<stamp>.vi
  7 COLD reopen of the NEWEST saved file in a freshly restarted LabVIEW - THAT reading is the truth
  8 the ORDERED `Is Broken?` pass LAST, after the cold reopen (42(b)); the md5s are re-read after it

THE FILE RULE OVERRIDES EVERY STOP
  Any failure at any step: the working copy is written to claudeDev\\D1_s3b_row1_stop_<stage>_<stamp>.vi
  BEFORE anything is removed or closed, and its path/md5/size are reported. `ARTEFACTS ON DISK: []` is not an
  acceptable ending.
  MEASURED CONSTRAINT, REPORTED NOT REPAIRED: `gscript.save` (tools/gscript.py:2071-2074) REFUSES a VI whose
  ExecState is 0 - "SaveInstrument blocks forever on one" - and its only broken-VI route is `gui_save`, which
  is a GUI action and is banned by this brief and by the static gate. So "SAVE UNCONDITIONALLY" is attempted
  unconditionally; when ExecState is 0 the COM save RAISES, and the fallback file is a byte copy of the
  working file AS IT STANDS ON DISK, which carries NO in-memory edit. Every such file is gated and labelled
  `bytes_equal_to_the_bed`, so it is never mistaken for a built artefact.

WHAT THIS IS NOT
  Row 2 is not attempted. No new op, no new gscript verb, no recipe, no new process device, no edit to
  tools/gscript.py (its `wire_indicators` post-check defect at :1794-1797 is 53(d'')'s recorded, DELIBERATELY
  UNREPAIRED item), no cast, no second construction, no splice (51(h)).
  `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` neither imported nor called; `allow_broken`
  never True; `create_indicator` and `connect_ctl` NOT called (53(d') measured them out). No VI run (34(f) -
  OP VIs are run, the fleet's normal mechanism). No GUI action. No motor / ASI / camera (rig JOLIP/assembled).
  retrospective / audit_cycle / violations / doc_ingest / prior_art_review NOT run (54(a)). NO ROUTE IS CHOSEN
  OR RECOMMENDED; docs/cycle27-plan.md and STATUS `## NEXT` are untouched.

PREDICTION CONTRACT
  T_*   four md5 pins BEFORE (ORIGINAL FATAL, s1, s2 FATAL, s3a FATAL) + the donor f695d97a
  B1_a  the bed opens COLD at ExecState 1; #10407 t0 carries wire 10799
  B1_b  the delete removes EXACTLY 10799; ExecState goes to 0
  B1_c  the EXISTING indicator 23555 is found by its own control uid, label read off the machine, EXACTLY one
        front-panel row carries it
  B1_d  OpCreateLocalRead_v0(Write?=False) adds EXACTLY ONE Local; Local census 8 -> 9
  B1_e  RULE-1a GATE (50(i)): ONE terminal, NAME == 'Automatic Error Handling' as read off the machine,
        is_source True (= READ)
  B1_m  *** move_in leaves the Local owned by Diagram #639 *** (owner class + uid + diagram index + Nodes[])
  B1_g  after the connect BOTH ends carry the SAME wire uid (that is what a same-diagram wire looks like)
  B1_k  *** the #637 census IMMEDIATELY after the connect equals the 59/48 baseline *** (taken BEFORE any
        save decision - the reading dispatch #3 never took)
  B1_f  ExecState == 1 after the connect (the step-6 precondition)
  B1_s5 *** step 5 leaves a FILE ON DISK *** (path/md5/size printed whatever ExecState read)
  B1_i  the T3 separator: exactly ONE source on the re-fed net, and its sink is panel control 23555
  B1_s6 *** step 6 leaves a FILE ON DISK *** (only if step 6 ran)
  C_1   the COLD reading of the NEWEST saved file in a freshly restarted LabVIEW
  E_B1  the ORDERED `Is Broken?` on the new #10407 wire, LAST
  Z_*   four md5 pins PASS after; the donor byte-unchanged; scratch gone; refs/handles; the op's OWN embedded
        `Is Broken?` readback recorded (53(d5): OpConnectNested_v1 carries one internally)
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
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index, owner_of, move_in                               # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
import build_opconnectnested_v1 as CN1                                             # noqa: E402
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

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c62_s3b_movein.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

CASE_UID = 10407                 # CaseStructure on Diagram #639, Nodes[24]
D639, D536 = 639, 536
LOOP11_UID = 637                 # 37(e)'s tunnel / border witness, baseline 59 terminals / 48 wired
LOOP637_BASELINE = (59, 48)
CT_CENSUS_BASELINE = 116
SCAN_LIMIT = 140
LOCAL_CENSUS_BASE = 8            # docs/toolkit-capabilities.md:284
MOVE_POSITION = (120, 4000)      # diag_s58_boolwire.py:193 - a position INSIDE Diagram #639; cosmetic only

ROW = {"n": 1, "sink_term": 0, "wire_pin": 10799, "src_uid": 10686, "src_term": 0,
       "src_term_name": "x .and. y?", "old_control": 23555,
       "old_label": "Automatic Error Handling", "want_census": LOCAL_CENSUS_BASE + 1}

WORK = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_%s.vi" % STAMP)          # the step-6 artefact path
STEP3_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_row1a_%s.vi" % STAMP)   # the step-5 artefact path


def stop_path(stage):
    return os.path.join(g.CLAUDEDEV, "D1_s3b_row1_stop_%s_%s.vi" % (stage, STAMP))


T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 62 material #4: S3b ROW 1 ONLY, move_in added before the connect, saves UNCONDITIONAL",
     "route_source": "docs/cycle27-plan.md Pre-decided 53(d')/53(d'')/53(d-quad)/53(d5) - NOT chosen here",
     "row2_attempted": False,
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True,
     "create_indicator_called": False, "connect_ctl_called": False,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's normal mechanism",
     "no_gui_action": True,
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "gui_save": "NEVER called", "allow_broken": "NEVER True",
     "move_in": "IMPORTED AND CALLED - the one new step, Pre-decided 53(d-quad)",
     "op_embedded_is_broken_readbacks": [],
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "stages": {}, "artefacts_on_disk": []}
K = R["stages"].setdefault("B1", {"row": 1})


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
    """the LIVE Traverse 'Diagram' index of #639 and #536, resolved by uid every time (34(h))."""
    out = {}
    for uid in (D639, D536):
        try:
            out[uid] = diag_index(target, uid)
        except Exception as e:                                                     # noqa: BLE001
            out[uid] = None
            rec["diag_index_error_%d" % uid] = "%s: %s" % (type(e).__name__, str(e)[:200])
    rec["diagram_indices"] = out
    fact("live diagram indices: #639 -> %r, #536 (top level) -> %r" % (out.get(D639), out.get(D536)))
    return out


def live_d639(tag):
    """RE-READ the Traverse 'Diagram' index of #639 off the machine, NEVER cached across a mutation.

    docs/cycle27-plan.md:341-344 - "A traverse INDEX is not a stable key ... must be re-read, never cached
    across a mutation" - restated as RISK (ii) in diag_s58_boolwire.py:116-117. The forced review
    archive/peer/2026-09-21-c62-astcheck7.md section 4.1 found this file caching one index across the wire
    delete, the Local creation and the move; this helper is that repair.
    """
    try:
        v = diag_index(WORK, D639)
        err = ""
    except Exception as e:                                                         # noqa: BLE001
        v, err = None, "%s: %s" % (type(e).__name__, str(e)[:200])
    K.setdefault("d639_reresolved", []).append({"tag": tag, "value": v, "error_verbatim": err})
    fact("%s diag_index(#639) RE-READ off the machine = %r%s"
         % (tag, v, (" ; ERROR " + err) if err else ""))
    return v


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
        loc["how"] = "NOT IN Diagram.Nodes[] (node_labels lists %d nodes, none echoes this uid)" % len(rows_l)
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


def loop637_counts(target, rec, tag):
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


def delete_by_uid(rec, tag, target, cls, uid):
    """diag_s58_boolwire.py:456-483 verbatim in shape - resolve uid -> Traverse index, then delete_object."""
    rd = {"tag": tag, "class": cls, "uid": uid}
    try:
        cur = [o["uid"] for o in g.report_all(target, cls)]
        rd["members"] = len(cur)
        rd["index"] = cur.index(uid)
    except Exception as e:                                                         # noqa: BLE001
        rd["index"] = None
        rd["error_verbatim"] = "index resolution failed %s: %s" % (type(e).__name__, str(e)[:250])
        rec.setdefault("deletes", []).append(rd)
        fact("%s: could NOT resolve #%r to a %s Traverse index - %s" % (tag, uid, cls, rd["error_verbatim"]))
        return rd
    try:
        gone = g.delete_object(target, cls, rd["index"])
        rd["gone"] = sorted(gone) if gone else gone
        rd["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rd["gone"] = None
        rd["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:500])
    rec.setdefault("deletes", []).append(rd)
    fact("%s: delete_object(target, %r, %r) on uid #%r (of %r members) -> gone %r ; error VERBATIM %r"
         % (tag, cls, rd["index"], uid, rd.get("members"), rd.get("gone"), rd["error_verbatim"]))
    return rd


def traverse_index_of(target, uid, rec, tag):
    """the source's index in the Traverse class lists wire_indicators addresses (53(d') used 'Function')."""
    cls_rows = {}
    for cls in ("Function", "Node", "GObject"):
        try:
            u = [o["uid"] for o in g.report_all(target, cls)]
            cls_rows[cls] = u.index(uid) if uid in u else None
        except Exception as e:                                                     # noqa: BLE001
            cls_rows[cls] = "ERROR %s: %s" % (type(e).__name__, str(e)[:100])
    rec["source_class_membership"] = cls_rows
    pick = next(((c, i) for c, i in cls_rows.items() if isinstance(i, int)), (None, None))
    fact("%s the source #%d in the Traverse class lists: %r -> using node_class %r index %r"
         % (tag, uid, cls_rows, pick[0], pick[1]))
    return pick


# ============================================================ the donor call (OpCreateLocalRead_v0, unchanged)
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


# ============================================================ the T3 separator (reverse census, read-only)
def t3_separator(target, wire_uid, d639, rec, tag):
    """every terminal that carries `wire_uid`, from the TERMINAL side. No `Is Broken?` is read."""
    members, scanned = [], 0
    if isinstance(d639, int) and wire_uid:
        for i in range(SCAN_LIMIT):
            try:
                u, tr = g.node_terms_uid(target, d639, i)
            except Exception:                                                      # noqa: BLE001
                break
            if not u:
                break
            scanned += 1
            for r in term_rows_verbatim(tr):
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
    rec["t3"] = {"wire": wire_uid, "nodes_scanned_on_639": scanned, "panel_rows_total": len(prows),
                 "members": members, "source_count": len(srcs), "sources": srcs, "sinks": sinks}
    fact("%s T3 SEPARATOR - the net of wire %r (%d nodes scanned on #639, %d panel rows): %r"
         % (tag, wire_uid, scanned, len(prows), members))
    fact("%s T3 SOURCES on that net: %d -> %r" % (tag, len(srcs), srcs))
    return rec["t3"]


# ============================================================ THE FILE RULE
def leave_a_file(tag, dest, why):
    """THE FILE RULE. Attempt the COM save UNCONDITIONALLY; whatever it does, put a FILE at `dest`.

    gscript.save refuses (raises, it does not hang) when ExecState == 0 - tools/gscript.py:2071-2074 - and its
    only broken-VI route is gui_save, banned here. So on a refusal the fallback is a byte copy of the working
    file AS IT STANDS ON DISK, and the record says plainly whether that carries any edit.
    """
    rec = {"tag": tag, "dest": dest, "why": why, "save_error_verbatim": "", "fallback_copy": False}
    es = read_exec_state(K, "%s immediately before the save attempt" % tag, WORK)
    rec["exec_state_at_save"] = es
    try:
        rec["save_returned_size"] = g.save(WORK)
    except Exception as e:                                                         # noqa: BLE001
        rec["save_returned_size"] = None
        rec["save_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    if os.path.abspath(dest) != os.path.abspath(WORK):
        try:
            shutil.copy2(WORK, dest)
            rec["copy_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            rec["copy_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    ff = D.file_facts("%s the artefact" % tag, dest)
    rec.update({"exists": bool(ff.get("exists")), "md5": ff.get("md5"), "size": ff.get("size")})
    rec["bytes_equal_to_the_bed"] = (ff.get("md5") == S3A_MD5)
    rec["carries_the_in_memory_edits"] = bool(ff.get("exists")) and not rec["save_error_verbatim"]
    R["artefacts_on_disk"].append({"stage": tag, "path": dest, "md5": ff.get("md5"), "size": ff.get("size"),
                                   "exec_state_at_save": es,
                                   "carries_the_in_memory_edits": rec["carries_the_in_memory_edits"],
                                   "bytes_equal_to_the_bed": rec["bytes_equal_to_the_bed"],
                                   "save_error_verbatim": rec["save_error_verbatim"]})
    K.setdefault("saves", []).append(rec)
    fact("%s FILE ON DISK: %s  md5 %r  size %r  (ExecState at the save %r ; COM save error %r ; carries the "
         "in-memory edits %r ; bytes equal to the bed %r)"
         % (tag, dest, rec["md5"], rec["size"], es, rec["save_error_verbatim"],
            rec["carries_the_in_memory_edits"], rec["bytes_equal_to_the_bed"]))
    dump()
    return rec


def abandon(stage, why):
    """THE FILE RULE OVERRIDES EVERY STOP: write the file FIRST, then report, then stop."""
    K["abandoned_because"] = why
    fact("ROW 1 STOPPED at %s: %s" % (stage, why))
    sv = leave_a_file("STOP_%s" % stage, stop_path(stage), why)
    gate("B1_stop *** THE FILE RULE: a file is on disk at the stop ***", bool(sv.get("exists")),
         "%s md5 %r size %r (carries the in-memory edits %r)"
         % (os.path.basename(sv["dest"]), sv.get("md5"), sv.get("size"),
            sv.get("carries_the_in_memory_edits")))
    read_exec_state(K, "at the stop", WORK)
    for label, uid in (("#10407", CASE_UID), ("source #%d" % ROW["src_uid"], ROW["src_uid"]),
                       ("the new Local", K.get("local_readback", {}).get("uid"))):
        if uid is None:
            continue
        rows, _l = node_table(WORK, uid, "STOP REPORT %s" % label)
        K.setdefault("stop_report_tables", {})[label] = rows
    try:
        prows, _pe = panel_all(WORK, "STOP REPORT panel")
        K.setdefault("stop_report_tables", {})["the indicator's panel row"] = \
            [r for r in prows if r.get("uid") == ROW["old_control"]]
        fact("STOP REPORT - the indicator's panel row (control uid %d): %r"
             % (ROW["old_control"], K["stop_report_tables"]["the indicator's panel row"]))
    except Exception as e:                                                         # noqa: BLE001
        fact("STOP REPORT panel read raised %s: %s" % (type(e).__name__, str(e)[:200]))
    close_quietly(WORK)
    if os.path.exists(WORK) and os.path.abspath(WORK) != os.path.abspath(sv["dest"]):
        try:
            os.remove(WORK)
        except Exception as e:                                                     # noqa: BLE001
            fact("could not remove %s: %s" % (WORK, e))
    K["working_copy_removed"] = not os.path.exists(WORK)
    fact("the working copy %s is removed: %r" % (os.path.basename(WORK), K["working_copy_removed"]))
    dump()
    raise Stop(why)


# ============================================================ ROW 1
def build_row1():
    print("\n========== B1  ROW 1 on #%d t%d  (source #%d t%d %r -> indicator %r, control uid %d)"
          % (CASE_UID, ROW["sink_term"], ROW["src_uid"], ROW["src_term"], ROW["src_term_name"],
             ROW["old_label"], ROW["old_control"]), flush=True)
    K.update({"from": os.path.basename(S3A_ARTEFACT), "working_file": os.path.basename(WORK),
              "step5_artefact": os.path.basename(STEP3_PATH), "step6_artefact": os.path.basename(WORK)})
    shutil.copy2(S3A_ARTEFACT, WORK)
    g.open_panel(WORK)
    time.sleep(1.0)
    es0 = read_exec_state(K, "[0] cold open of the bed", WORK)
    gate("B1_a the bed opens COLD at ExecState 1", es0 == 1, "%r" % (es0,))
    dd = diagrams(WORK, K)
    d639 = dd.get(D639)

    K["local_census_before"] = count_of(WORK, "Local")
    K["control_terminal_census_before"] = count_of(WORK, "ControlTerminal")
    fp0, _e0 = panel_all(WORK, "BEFORE")
    K["panel_rows_before_count"] = len(fp0)
    t637_0 = loop637_counts(WORK, K, "BEFORE")
    gate("B1_k0 #637 baseline reads %r as recorded" % (LOOP637_BASELINE,),
         t637_0 == LOOP637_BASELINE, "%r" % (t637_0,))

    case_rows, _cl = node_table(WORK, CASE_UID, "BEFORE #10407")
    K["case_table_before"] = case_rows
    sink_row = next((r for r in case_rows if r["i"] == ROW["sink_term"]), None)
    K["sink_row_before"] = sink_row
    W = (sink_row or {}).get("wire")
    gate("B1_a2 #10407 t%d carries the wire this row replaces" % ROW["sink_term"],
         W == ROW["wire_pin"], "wire %r (the cycle-62 reading was %r)" % (W, ROW["wire_pin"]))

    src_rows, _sl = node_table(WORK, ROW["src_uid"], "BEFORE source")
    K["source_table_before"] = src_rows
    src_row = next((r for r in src_rows if r["i"] == ROW["src_term"]), None)
    src_name_live = (src_row or {}).get("name")
    K["source_terminal_name_read_off_the_machine"] = src_name_live
    gate("B1_a3 the source terminal's NAME reads off the machine as %r" % ROW["src_term_name"],
         src_name_live == ROW["src_term_name"],
         "%r (hex %r)" % (src_name_live, (src_row or {}).get("name_hex")))

    # ---- the EXISTING indicator: found by its own control uid, its label READ OFF THE MACHINE
    prow = next((r for r in fp0 if r["uid"] == ROW["old_control"]), None)
    K["existing_indicator_panel_row"] = prow
    live_label = (prow or {}).get("label")
    K["existing_indicator_label_read_off_the_machine"] = live_label
    K["existing_indicator_label_hex"] = (live_label or "").encode("utf-8").hex()
    try:
        fpl = g.fp_labels(WORK)
    except Exception as e:                                                         # noqa: BLE001
        fpl = []
        K["fp_labels_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    hits = [(i, t, ind) for (i, t, ind) in fpl if t == live_label]
    K["existing_indicator_fp_rows"] = hits
    fact("the EXISTING indicator (control uid %d): panel row %r ; label READ OFF THE MACHINE %r (hex %r) ; "
         "front-panel rows carrying that label: %r"
         % (ROW["old_control"], prow, live_label, K["existing_indicator_label_hex"], hits))
    if not gate("B1_c the EXISTING indicator is found by its own control uid and EXACTLY ONE front-panel row "
                "carries its label", bool(live_label) and len(hits) == 1,
                "label %r rows %r (the recorded label was %r)" % (live_label, hits, ROW["old_label"])):
        abandon("c_indicator", "the existing indicator's label/panel row is ambiguous or missing")
    gate("B1_c2 that label equals the one this row was planned against", live_label == ROW["old_label"],
         "live %r vs recorded %r" % (live_label, ROW["old_label"]))

    # ---- 1. delete the whole Wire object
    gone = delete_wire_uid(WORK, W, K, "[1]")
    gate("B1_b the delete removed EXACTLY the wire uid targeted", gone == [W],
         "gone %r, targeted %r" % (gone, W))
    es1 = read_exec_state(K, "[1] after the delete (0 is EXPECTED)", WORK)
    K["exec_state_after_delete"] = es1

    # ---- 2. the Local, in READ mode, bound to the EXISTING indicator
    bool_label, _fpl_donor = donor_bool_label()
    K["donor_direction_control_label"] = bool_label
    if not gate("B1_d0 the donor's direction control was identified on the machine", bool(bool_label),
                "%r" % (bool_label,)):
        abandon("d0_donor_label", "the donor's Write? control could not be identified")
    rd = call_donor(WORK, hits[0][0], bool_label, K, "[2]")
    gate("B1_d the Local census went %r -> %r (want %r)"
         % (rd["local_census_before"], rd["local_census_after"], ROW["want_census"]),
         rd["local_census_after"] == ROW["want_census"], "added %r" % (rd["local_uids_added"],))
    if len(rd["local_uids_added"]) != 1:
        abandon("d_local", "the donor added %r Locals" % (len(rd["local_uids_added"]),))
    local_uid = rd["local_uids_added"][0]
    K["local_uid"] = local_uid
    read_exec_state(K, "[2] after the Local was created (unwired)", WORK)

    # ---- THE RULE-1a GATE (50(i)) + THE PLACEMENT BEFORE THE MOVE
    lrows, lloc = node_table(WORK, local_uid, "the new Local BEFORE move_in")
    K["local_readback"] = {"uid": local_uid, "loc": lloc, "terminal_rows_verbatim": lrows}
    K["placement_before_move_in"] = {"owner_class": lloc.get("owner_class"),
                                     "owner_uid": lloc.get("owner_uid"),
                                     "diagram_index": lloc.get("diagram_index"),
                                     "nodes_index": lloc.get("nodes_index")}
    one = lrows[0] if len(lrows) == 1 else {}
    fact("LOCAL READBACK VERBATIM (before move_in): Local #%s -> %d terminal(s); NAME %r (hex %r), "
         "is_source %r, wire %r ; owner %r#%r diagram %r Nodes[%r]"
         % (local_uid, len(lrows), one.get("name"), one.get("name_hex"), one.get("is_source"),
            one.get("wire"), lloc.get("owner_class"), lloc.get("owner_uid"), lloc.get("diagram_index"),
            lloc.get("nodes_index")))
    gate("B1_e RULE-1a GATE (50(i)): ONE terminal, NAME == the indicator label it was created from, "
         "is_source True (= READ)",
         len(lrows) == 1 and one.get("name") == live_label and one.get("is_source") is True,
         "name %r (hex %r) vs label %r (hex %r) ; is_source %r"
         % (one.get("name"), one.get("name_hex"), live_label, K["existing_indicator_label_hex"],
            one.get("is_source")))
    local_term_i = one.get("i", 0)
    K["local_term_index"] = local_term_i

    # ---- 3. THE NEW STEP (53(d-quad)): move_in the Local onto Diagram #639
    print("\n---------- [3] move_in: the ONE new step (Pre-decided 53(d-quad))", flush=True)
    try:
        inv_before = set(g.uids(WORK, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_before = set()
        fact("[3] uids(Invoke) BEFORE raised %s: %s" % (type(e).__name__, str(e)[:140]))
    d639 = live_d639("[3] before move_in")          # re-read, never cached across the delete + the create
    mv_ret, mv_err = None, None
    if not isinstance(d639, int):
        mv_err = "NOT ATTEMPTED: diag_index(#639) did not resolve (%r)" % (d639,)
    else:
        try:
            mv_ret = move_in(WORK, local_uid, d639, MOVE_POSITION)
            mv_err = ""
        except Exception as e:                                                     # noqa: BLE001
            mv_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    K["move_in_call"] = {"call": "move_in(target, %r, %r, %r)  # build_d1_v0.py:318"
                                 % (local_uid, d639, MOVE_POSITION),
                         "returned": mv_ret, "error_verbatim": mv_err}
    fact("[3] move_in(Local #%r -> Diagram #%d at LIVE Traverse index %r, position %r) returned %r ; "
         "error VERBATIM %r" % (local_uid, D639, d639, MOVE_POSITION, mv_ret, mv_err))
    gate("B1_m0 move_in returned without raising", mv_err == "", "returned %r, error %r" % (mv_ret, mv_err))

    # the junk `Invoke` residue move_in leaves (diag_s58_boolwire.py:900-910, PREDICTED RISK)
    try:
        inv_after = set(g.uids(WORK, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_after = set()
        fact("[3] uids(Invoke) AFTER raised %s: %s" % (type(e).__name__, str(e)[:140]))
    junk = sorted(inv_after - inv_before)
    K["junk_invoke_uids_added_by_move_in"] = junk
    fact("[3] move_in left %r junk `Invoke`(s): %r" % (len(junk), junk))
    for ju in junk:
        delete_by_uid(K, "[3] junk Invoke purge", WORK, "Invoke", ju)

    lrows_m, lloc_m = node_table(WORK, local_uid, "the new Local AFTER move_in")
    K["placement_after_move_in"] = {"owner_class": lloc_m.get("owner_class"),
                                    "owner_uid": lloc_m.get("owner_uid"),
                                    "diagram_index": lloc_m.get("diagram_index"),
                                    "nodes_index": lloc_m.get("nodes_index"),
                                    "terminal_rows_verbatim": lrows_m}
    fact("[3] PLACEMENT: before move_in owner %r#%r diagram %r Nodes[%r]  ->  after move_in owner %r#%r "
         "diagram %r Nodes[%r]"
         % (K["placement_before_move_in"]["owner_class"], K["placement_before_move_in"]["owner_uid"],
            K["placement_before_move_in"]["diagram_index"], K["placement_before_move_in"]["nodes_index"],
            lloc_m.get("owner_class"), lloc_m.get("owner_uid"), lloc_m.get("diagram_index"),
            lloc_m.get("nodes_index")))
    es3 = read_exec_state(K, "[3] after move_in (and the junk purge)", WORK)
    K["exec_state_after_move_in"] = es3
    gate("B1_m *** move_in leaves the Local owned by Diagram #639 ***",
         lloc_m.get("owner_uid") == D639 and lloc_m.get("owner_class") in ("Diagram", "TopLevelDiagram"),
         "owner (%r, %r) ; diagram index %r ; Nodes[%r] ; ExecState %r"
         % (lloc_m.get("owner_class"), lloc_m.get("owner_uid"), lloc_m.get("diagram_index"),
            lloc_m.get("nodes_index"), es3))
    if lloc_m.get("nodes_index") is None:
        abandon("m_placement", "the Local is not addressable in Diagram.Nodes[] after move_in (%r)"
                % (lloc_m.get("how"),))
    if lrows_m:
        local_term_i = lrows_m[0].get("i", local_term_i)

    # ---- THE POST-MOVE READBACK (forced review 2026-09-21-c62-astcheck7 section 4.2/4.3): the state that
    # actually gets wired is the state AFTER the move, and this project has MEASURED that a GObject.Move can
    # flip is_source FALSE on every terminal of the moved object (build_d1_routeb_v0.py:48-49). A flip here is
    # a FINDING to report, not a repair and not a route change.
    one_m = lrows_m[0] if len(lrows_m) == 1 else {}
    K["local_readback_after_move_in"] = {"uid": local_uid, "terminal_rows_verbatim": lrows_m}
    fact("[3] LOCAL READBACK VERBATIM (AFTER move_in): Local #%s -> %d terminal(s); NAME %r (hex %r), "
         "is_source %r, wire %r"
         % (local_uid, len(lrows_m), one_m.get("name"), one_m.get("name_hex"), one_m.get("is_source"),
            one_m.get("wire")))
    gate("B1_e2 RULE-1a GATE RE-READ AFTER move_in: ONE terminal, NAME == %r, is_source True (= READ)"
         % (live_label,),
         len(lrows_m) == 1 and one_m.get("name") == live_label and one_m.get("is_source") is True,
         "name %r (hex %r) ; is_source %r  [before the move it read name %r is_source %r]"
         % (one_m.get("name"), one_m.get("name_hex"), one_m.get("is_source"), one.get("name"),
            one.get("is_source")))
    K["local_census_after_move_in"] = count_of(WORK, "Local")
    gate("B1_m2 the Local census is STILL %r after move_in (the move duplicated nothing)"
         % (ROW["want_census"],), K["local_census_after_move_in"] == ROW["want_census"],
         "%r" % (K["local_census_after_move_in"],))

    # ---- 4. connect the Local's SOURCE into the freed #10407 sink - NOW BOTH ON Diagram #639
    print("\n---------- [4] the connect, same diagram", flush=True)
    d639 = live_d639("[4] before the connect")      # re-read, never cached across move_in
    _cr, case_loc = node_table(WORK, CASE_UID, "#10407 before the connect")
    sink_i = case_loc.get("nodes_index")
    src_diag, src_i = lloc_m.get("diagram_index"), lloc_m.get("nodes_index")
    K["connect_call"] = ("connect_nested_v1(target, sink_diag=%r, sink_node=%r, sink_term=%r, src_diag=%r, "
                         "src_node=%r, src_term=%r)" % (d639, sink_i, ROW["sink_term"], src_diag, src_i,
                                                        local_term_i))
    fact("[4] CONNECT: %s   (SAME diagram on both sides: %r == %r)"
         % (K["connect_call"], d639, src_diag))
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es_c, err_c = CONNECT_V1(WORK, d639, sink_i, ROW["sink_term"], src_diag, src_i,
                                         local_term_i, V1_LABELS)
        K["connect_result"] = {"wire_delta": dw, "exec_state_returned": es_c, "error_verbatim": err_c}
    except Exception as e:                                                         # noqa: BLE001
        K["connect_result"] = {"wire_delta": None, "exec_state_returned": None,
                               "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])}
    op_out = buf.getvalue().rstrip().splitlines()
    for ln in op_out:
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    for ln in op_out:
        if "Is Broken?" in ln:
            R["op_embedded_is_broken_readbacks"].append({"where": "[4] connect", "line": ln.strip()})
    fact("[4] connect result: %r" % (K["connect_result"],))

    case_rows2, _c2 = node_table(WORK, CASE_UID, "AFTER the connect #10407")
    K["case_table_after_connect"] = case_rows2
    sink_after = next((r for r in case_rows2 if r["i"] == ROW["sink_term"]), None)
    K["sink_row_after_connect"] = sink_after
    lrows2, _l2 = node_table(WORK, local_uid, "the Local AFTER the connect")
    K["local_table_after_connect"] = lrows2
    K["sink_end_wire_uid"] = (sink_after or {}).get("wire")
    K["local_end_wire_uid"] = (lrows2[0].get("wire") if lrows2 else None)
    same_uid = bool(K["sink_end_wire_uid"]) and K["sink_end_wire_uid"] == K["local_end_wire_uid"]
    K["both_ends_same_wire_uid"] = same_uid
    K["far_end_terminal_name"] = (lrows2[0].get("name") if lrows2 else None)
    fact("[4] #10407 t%d wire uid %r  |  the Local #%s terminal %r %r wire uid %r  ->  SAME uid: %r "
         "(wire_delta %r)"
         % (ROW["sink_term"], K["sink_end_wire_uid"], local_uid,
            (lrows2[0].get("i") if lrows2 else None), K["far_end_terminal_name"],
            K["local_end_wire_uid"], same_uid, K["connect_result"].get("wire_delta")))
    gate("B1_g *** BOTH ENDS CARRY THE SAME WIRE UID (a same-diagram wire) ***", same_uid,
         "sink %r vs local %r ; wire_delta %r ; far end owner uid %r terminal name %r"
         % (K["sink_end_wire_uid"], K["local_end_wire_uid"], K["connect_result"].get("wire_delta"),
            local_uid, K["far_end_terminal_name"]))

    # ---- THE #637 CENSUS, IMMEDIATELY, BEFORE ANY SAVE DECISION (the reading dispatch #3 never took)
    t637_1 = loop637_counts(WORK, K, "IMMEDIATELY AFTER THE CONNECT")
    K["loop637_before"], K["loop637_after_connect"] = t637_0, t637_1
    gate("B1_k *** THE #637 CENSUS IMMEDIATELY AFTER THE CONNECT == the %r baseline (no tunnel, no border "
         "object - 50(e)/37(e)) ***" % (LOOP637_BASELINE,), t637_1 == LOOP637_BASELINE,
         "%r -> %r" % (t637_0, t637_1))
    K["control_terminal_census_after_connect"] = count_of(WORK, "ControlTerminal")
    gate("B1_l the ControlTerminal census is unchanged at %d after the connect" % CT_CENSUS_BASELINE,
         K["control_terminal_census_before"] == K["control_terminal_census_after_connect"]
         == CT_CENSUS_BASELINE,
         "%r -> %r" % (K["control_terminal_census_before"], K["control_terminal_census_after_connect"]))
    es4 = read_exec_state(K, "[4] after the connect (1 is what step 6 needs)", WORK)
    K["exec_state_after_connect"] = es4
    gate("B1_f ExecState == 1 after the connect", es4 == 1, "%r" % (es4,))

    # ---- 5. SAVE UNCONDITIONALLY
    print("\n---------- [5] SAVE UNCONDITIONALLY, whatever ExecState reads", flush=True)
    sv5 = leave_a_file("STEP5", STEP3_PATH, "the step-5 artefact, saved unconditionally")
    gate("B1_s5 *** STEP 5 LEFT A FILE ON DISK ***", bool(sv5.get("exists")),
         "%s md5 %r size %r (carries the in-memory edits %r)"
         % (os.path.basename(STEP3_PATH), sv5.get("md5"), sv5.get("size"),
            sv5.get("carries_the_in_memory_edits")))

    # ---- 6. ONLY IF the live ExecState at step 4 is 1
    if es4 != 1:
        K["step6_skipped_because"] = ("the live ExecState at step 4 read %r, not 1 - the brief says SKIP "
                                      "step 6 and say so plainly; it is NOT forced" % (es4,))
        fact("[6] SKIPPED: %s" % K["step6_skipped_because"])
        gate("B1_i the T3 separator: exactly ONE source on the re-fed net, sink == control 23555", False,
             "NOT RUN: %s" % K["step6_skipped_because"])
        gate("B1_s6 *** STEP 6 LEFT A FILE ON DISK ***", False,
             "NOT RUN: %s" % K["step6_skipped_because"])
        close_quietly(WORK)
        return STEP3_PATH

    print("\n---------- [6] wire_indicators re-feeds indicator 23555, then the T3 separator", flush=True)
    d639 = live_d639("[6] before wire_indicators")   # re-read, never cached across the connect
    node_class, ni_f = traverse_index_of(WORK, ROW["src_uid"], K, "[6]")
    K["wire_indicators_call"] = ("g.wire_indicators(target, node_index=%r, src_terms=[%r], "
                                 "indicator_names=[%r], diagram_index=%r, node_class=%r)"
                                 % (ni_f, src_name_live, live_label, d639, node_class))
    fact("[6] CALL: %s" % K["wire_indicators_call"])
    if not isinstance(ni_f, int) or not isinstance(d639, int):
        K["wire_indicators_error_verbatim"] = "NOT ATTEMPTED: node_class/index %r/%r, d639 %r" \
            % (node_class, ni_f, d639)
        K["wire_indicators_returned"] = None
        fact("[6] %s" % K["wire_indicators_error_verbatim"])
    else:
        try:
            K["wire_indicators_returned"] = g.wire_indicators(WORK, ni_f, [src_name_live], [live_label],
                                                              diagram_index=d639, node_class=node_class)
            K["wire_indicators_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            K["wire_indicators_returned"] = None
            K["wire_indicators_error_verbatim"] = "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])
    fact("[6] wire_indicators returned %r ; raised %r  (a raise here is a READING - gscript.py:1794-1797 "
         "tests exec_state ABSOLUTELY, 53(d''); the T3 separator below is what decides)"
         % (K["wire_indicators_returned"], K["wire_indicators_error_verbatim"]))
    es6 = read_exec_state(K, "[6] after wire_indicators", WORK)
    K["exec_state_after_wire_indicators"] = es6

    src_rows3, _s3 = node_table(WORK, ROW["src_uid"], "AFTER wire_indicators source")
    K["source_table_after"] = src_rows3
    sr3 = next((r for r in src_rows3 if r["i"] == ROW["src_term"]), None)
    IND_W = (sr3 or {}).get("wire")
    K["indicator_wire_uid_read_off_the_machine"] = IND_W
    gate("B1_h wire_indicators left a NON-ZERO wire on the source #%d t%d"
         % (ROW["src_uid"], ROW["src_term"]), bool(IND_W), "wire %r ; row %r" % (IND_W, sr3))

    t3 = t3_separator(WORK, IND_W, d639, K, "[6]")
    sink_uids = [m.get("node_uid") for m in t3.get("sinks", [])]
    gate("B1_i *** THE T3 SEPARATOR: EXACTLY ONE source on wire %r, and its sink is panel control %d ***"
         % (IND_W, ROW["old_control"]),
         t3.get("source_count") == 1 and ROW["old_control"] in sink_uids,
         "sources %r -> %r ; sinks %r" % (t3.get("source_count"), t3.get("sources"), sink_uids))

    t637_2 = loop637_counts(WORK, K, "AFTER wire_indicators")
    K["loop637_after_wire_indicators"] = t637_2
    gate("B1_k2 #637 counts still == the %r baseline after wire_indicators" % (LOOP637_BASELINE,),
         t637_2 == LOOP637_BASELINE, "%r" % (t637_2,))
    K["control_terminal_census_after"] = count_of(WORK, "ControlTerminal")
    fp2, _e2 = panel_all(WORK, "AFTER")
    K["panel_rows_after_count"] = len(fp2)
    gate("B1_l2 the ControlTerminal census is unchanged at %d throughout" % CT_CENSUS_BASELINE,
         K["control_terminal_census_after"] == CT_CENSUS_BASELINE,
         "%r ; panel rows %r -> %r" % (K["control_terminal_census_after"],
                                       K["panel_rows_before_count"], K["panel_rows_after_count"]))

    sv6 = leave_a_file("STEP6", WORK, "the step-6 artefact, saved unconditionally")
    gate("B1_s6 *** STEP 6 LEFT A FILE ON DISK ***", bool(sv6.get("exists")),
         "%s md5 %r size %r (carries the in-memory edits %r)"
         % (os.path.basename(WORK), sv6.get("md5"), sv6.get("size"),
            sv6.get("carries_the_in_memory_edits")))
    K.update({"sink_nodes_index": sink_i, "src_diag_of_local": src_diag,
              "src_nodes_index_of_local": src_i})
    close_quietly(WORK)
    dump()
    return WORK


# ============================================================ the ORDERED `Is Broken?` pass (42(b)) - LAST
def ordered_pass(target):
    P = K.setdefault("ordered_pass", {})
    if not K.get("both_ends_same_wire_uid") and not K.get("sink_end_wire_uid"):
        P["not_attempted_because"] = "the row never produced a wire on #10407 t0"
        fact("ORDERED PASS NOT ATTEMPTED: %s" % P["not_attempted_because"])
        gate("E_B1 the ORDERED `Is Broken?` reads False on the new #10407 wire", False,
             "NOT ATTEMPTED: %s" % P["not_attempted_because"])
        return
    dd = diagrams(target, P)
    d639 = dd.get(D639)
    _cr, loc = node_table(target, CASE_UID, "ordered pass #10407")
    sink_i = loc.get("nodes_index")
    lrows, lloc = node_table(target, K.get("local_uid"), "ordered pass the Local")
    P["call"] = ("connect_nested_v1(target, %r, %r, %r, %r, %r, %r) - IDEMPOTENT re-connect of an EXISTING "
                 "connection; wire_delta must be 0" % (d639, sink_i, ROW["sink_term"],
                                                       lloc.get("diagram_index"), lloc.get("nodes_index"),
                                                       (lrows[0]["i"] if lrows else 0)))
    fact(P["call"])
    if sink_i is None or lloc.get("nodes_index") is None:
        P["not_attempted_because"] = "the sink or the Local is not addressable on the reopened file"
        gate("E_B1 the ORDERED `Is Broken?` reads False on the new #10407 wire", False,
             "NOT ATTEMPTED: %s" % P["not_attempted_because"])
        return
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, d639, sink_i, ROW["sink_term"],
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
    fact("ORDERED `Is Broken?` = %r on wire uid %r (wire_delta %r - expected 0, op error %r)"
         % (ib, rd.get("UID 2"), P.get("wire_delta"), P.get("error_verbatim")))
    gate("E_B1 the ORDERED `Is Broken?` reads False on the new #10407 wire", ib is False,
         "Is Broken? %r on wire %r ; wire_delta %r" % (ib, rd.get("UID 2"), P.get("wire_delta")))
    read_exec_state(None, "after the Is Broken? read (SUSPECT, NAMES.md:912-918; every save is done)", target)


# ============================================================ MAIN
def main():
    print("=== diag_c62_s3b_movein  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== S3b ROW 1 ONLY - move_in added before the connect (53(d-quad)); saves UNCONDITIONAL", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 D1_s2_loops.vi", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 D1_s3a_focus_ind.vi (the bed, never written)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    dn = probe("T4 the donor OpCreateLocalRead_v0.vi", DONOR)
    gate("T4 OpCreateLocalRead_v0.vi md5 == %s" % DONOR_MD5, dn.get("md5") == DONOR_MD5, dn.get("md5", "?"))

    D.fresh("T5 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    newest = None
    try:
        newest = build_row1()
    except Stop as s:
        fact("B1 STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        fact("B1 RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
        K["raised"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        try:
            abandon("raise", "an exception escaped the row: %s" % (str(e)[:200],))
        except Stop:
            pass
        except Exception as e2:                                                    # noqa: BLE001
            fact("the file rule itself raised %s: %s" % (type(e2).__name__, str(e2)[:300]))
    dump()

    # the NEWEST file this run put on disk, whatever stage produced it
    on_disk = [a for a in R["artefacts_on_disk"] if a.get("md5")]
    if not newest:
        newest = on_disk[-1]["path"] if on_disk else None
    R["newest_saved_file"] = newest
    fact("THE NEWEST SAVED FILE = %r" % (newest,))

    # ---- 7. the COLD reopen in a freshly restarted LabVIEW
    print("\n========== [7] COLD reopen of the NEWEST saved file in a freshly restarted LabVIEW", flush=True)
    if newest and os.path.exists(newest):
        D.fresh("C RESTART before the cold reopen")
        R["handles"]["after_c_restart"] = labview_handles()
        try:
            g.open_panel(newest)
            time.sleep(1.0)
        except Exception as e:                                                     # noqa: BLE001
            fact("C open_panel raised %s: %s" % (type(e).__name__, str(e)[:300]))
        es_cold = read_exec_state(None, "[7] COLD, freshly restarted LabVIEW, %s" % os.path.basename(newest),
                                  newest)
        R["cold_exec_state"] = es_cold
        R["cold_file"] = newest
        carries = next((a.get("carries_the_in_memory_edits") for a in R["artefacts_on_disk"]
                        if a["path"] == newest), None)
        R["cold_file_carries_the_in_memory_edits"] = carries
        gate("C_1 *** THE COLD READING of %s ***" % os.path.basename(newest), es_cold == 1,
             "ExecState %r (this file carries the in-memory edits: %r)" % (es_cold, carries))
        print("\n========== [8] the ORDERED `Is Broken?` pass (42(b)) - LAST, after the cold reopen",
              flush=True)
        ordered_pass(newest)
        close_quietly(newest)
    else:
        gate("C_1 *** THE COLD READING ***", False, "NOT REACHED: no file on disk")
        gate("E_B1 the ORDERED `Is Broken?` reads False on the new #10407 wire", False,
             "NOT REACHED: no file on disk")
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

    R["artefacts_after_the_ordered_pass"] = []
    for a in R["artefacts_on_disk"]:
        ff = D.file_facts("Z2 %s re-read after the ordered pass" % a["stage"], a["path"])
        R["artefacts_after_the_ordered_pass"].append({"stage": a["stage"], "path": a["path"],
                                                      "md5": ff.get("md5"), "size": ff.get("size"),
                                                      "exists": ff.get("exists")})
        gate("Z_2 %s md5 unchanged after the ordered pass" % a["stage"],
             ff.get("exists") and ff.get("md5") == a["md5"],
             "%s: %r vs %r" % (os.path.basename(a["path"]), a["md5"], ff.get("md5")))

    left = [p for p in os.listdir(g.CLAUDEDEV) if p.startswith("SCRATCH_C62")]
    gate("Z_3 no scratch of this run is left behind", not left, "still present: %r" % (left,))
    rc = R["ref_counts"] or {}
    gate("Z_1c refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    gate("Z_1d *** AT LEAST ONE FILE IS ON DISK (the file rule) ***", bool(R["artefacts_on_disk"]),
         "%d file(s)" % len(R["artefacts_on_disk"]))
    fact("53(d5) RECORDED, NOT REPAIRED - OpConnectNested_v1's OWN embedded `Is Broken?` readbacks seen in "
         "this run: %r" % (R["op_embedded_is_broken_readbacks"],))
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
