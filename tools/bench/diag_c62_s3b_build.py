"""diag_c62_s3b_build - S3b's two rows, built in the ORDER judgement fixed, FOUR staged saves.

WHAT ALREADY EXISTS AND IS REUSED (checked before writing a line of this file)
  docs/toolkit-capabilities.md  `OpCreateLocalRead_v0.vi` (md5 f695d97a..., READ mode via `Write?`=False),
                                `OpConnectNested_v1.vi` (the ONLY writer that reaches a SINK on a NESTED
                                diagram - gscript.connect_terminals is top-level-only, so the brief's
                                "connect_terminals(Local SOURCE -> the freed #10407 sink)" is realised by the
                                shipped `connect_nested_v1`, exactly as dispatch #2 called it)
  grep "^def " tools/gscript.py  delete_object / wire_indicators / node_terms_uid / node_labels /
                                panel_wiring / fp_labels / report_all / count / exec_state / save / op
  ls tools/bench                diag_c62_s3b_rows.py (stage/gate scaffold, the donor-call and ordered-pass
                                helpers) and diag_c62_s3b_rows_t3.py (the reverse-census separator) - both are
                                reused here verbatim in shape. NOTHING NEW IS BUILT: no op, no gscript verb,
                                no recipe, no device.

WHY THE ORDER IS WHAT IT IS (docs/cycle27-plan.md Pre-decided 53(d')/53(d''), judgement's decision)
  53(d') measured both of 53(d)'s middle steps OUT: `create_indicator` addresses the TOP-LEVEL Nodes[] and this
  VI's top-level diagram is empty (two readers agreeing), and `connect_ctl` raises 1055 with no wire. What DOES
  work is `wire_indicators` re-feeding S3a's EXISTING indicator from a bared source - measured clean, exactly
  one source on the resulting net. 53(d'') then fixes the ORDER: our own `wire_indicators` tests
  `exec_state != 1` ABSOLUTELY (tools/gscript.py:1794-1797) and so raises a FALSE failure mid-sequence, so the
  Local goes in FIRST (the VI is legal again) and the indicator is re-fed LAST. THE WRAPPER IS NOT PATCHED HERE.

THE SEQUENCE, PER ROW, IN THIS ORDER (not re-ordered, not re-chosen)
  1 delete_object(target,'Wire',<idx of the row's wire uid>)           ExecState 0 EXPECTED
  2 OpCreateLocalRead_v0.vi, Write?=False (READ), bound to the row's EXISTING S3a indicator
  3 connect_nested_v1(Local SOURCE -> #10407 tN SINK)                  ExecState 1 EXPECTED
      => IFF 1: SAVE  claudeDev\\D1_s3b_row<N>a_<stamp>.vi   (the row's GUARANTEED artefact)
  4 wire_indicators(<source's Traverse 'Function' index>, [<source terminal name>],
                    [<the EXISTING indicator label>], diagram_index=<live #639>)
      a raise here is a READING, not a verdict - the T3 separator verifies the wire on the machine
  5 ExecState 1 EXPECTED  => SAVE  claudeDev\\D1_s3b_row<N>_<stamp>.vi
  ROW 1 runs on a copy of claudeDev\\D1_s3a_focus_ind.vi (md5 eef91c1d..., a FATAL pin, never written).
  ROW 2 STARTS FROM ROW 1's SAVED STEP-5 FILE, in a freshly restarted LabVIEW.
  C  COLD reopen of row 2's final file in a freshly restarted LabVIEW = the artefact's pass criterion.
  E  the ORDERED `Is Broken?` pass runs LAST, after the cold reopen, on the two new #10407 wires (42(b));
     the saved md5s are re-read after it. NO `Is Broken?` IS READ ABOVE ANY SAVE (52(f)).

WHAT THIS IS NOT
  No new op, no new gscript verb, no recipe, no new process device, no edit to tools/gscript.py, no cast, no
  second construction, no splice (51(h)). `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` neither
  imported nor called; `allow_broken` never True; `move_in` neither imported nor called; `create_indicator` and
  `connect_ctl` are NOT called (53(d') measured them out). No VI run (34(f) - OP VIs are run, the fleet's normal
  mechanism). No GUI action. No motor / ASI / camera (rig 조립). retrospective / audit_cycle / violations /
  doc_ingest / prior_art_review NOT run (54(a)). NO ROUTE IS CHOSEN OR RECOMMENDED; docs/cycle27-plan.md and
  STATUS `## NEXT` are untouched.

PREDICTION CONTRACT
  T_*    four md5 pins BEFORE (ORIGINAL FATAL, s1, s2 FATAL, s3a FATAL) + the donor f695d97a
  <S>_a  the bed opens COLD at ExecState 1; #10407 t<n> carries the row's measured wire uid
  <S>_b  the delete removes EXACTLY that wire uid; ExecState goes to 0
  <S>_c  the EXISTING indicator's panel row is found by its own control uid and its label is read off the
         machine; exactly ONE front-panel row carries that label (ambiguity is a FINDING, and it stops the row)
  <S>_d  OpCreateLocalRead_v0(Write?=False) adds EXACTLY ONE Local; census 8 -> 9 (row 1) -> 10 (row 2)
  <S>_e  RULE-1a GATE (50(i)): the new Local reads back with node_terms as ONE terminal whose NAME equals the
         indicator label it was created from and whose is_source is True (= READ)
  <S>_f  ExecState == 1 after the connect  ***  and the step-3 artefact is on disk  ***
  <S>_g  #10407 t<n> carries a NEW wire whose far end is the LOCAL (owner uid + terminal name printed)
  <S>_h  wire_indicators leaves a NON-ZERO wire on the source terminal (the uid read off the machine)
  <S>_i  *** THE T3 SEPARATOR: exactly ONE source on that net, and its sink is THIS row's own panel control
         uid *** (reverse census over every node of Diagram #639 and all 116 panel rows)
  <S>_j  ExecState == 1 after wire_indicators  ***  and the step-5 artefact is on disk  ***
  <S>_k  #637 terminal/wired counts unchanged (baseline 59/48) - no tunnel, no border object (37(e))
  <S>_l  the ControlTerminal census is unchanged at 116 - no panel object created or deleted (53(d'))
  C_1    COLD ExecState == 1 on row 2's final file in a freshly restarted LabVIEW
  E_B1/2 the ORDERED `Is Broken?` reads False on both new #10407 wires
  Z_*    four md5 pins PASS after; the donor byte-unchanged; every scratch exists=False; refs/handles reported
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
from build_d1_v0 import diag_index, owner_of                                       # noqa: E402
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
OUT = os.path.join(BENCH, "diag_c62_s3b_build.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

CASE_UID = 10407                 # CaseStructure on Diagram #639, Nodes[24]
D639, D536 = 639, 536
LOOP11_UID = 637                 # 37(e)'s tunnel / border witness, baseline 59 terminals / 48 wired
LOOP637_BASELINE = (59, 48)
CT_CENSUS_BASELINE = 116
SCAN_LIMIT = 140
LOCAL_CENSUS_BASE = 8            # docs/toolkit-capabilities.md:284

# the two rows, MEASURED in cycle 62 (diag_c62_branch2.log:27,:61 ; diag_c62_s3b_rows_t3.log:33-36).
# Every one of these numbers is RE-READ off the machine before it is used; they are pins, not inputs.
ROWS = {
    "B1": {"n": 1, "sink_term": 0, "wire_pin": 10799, "src_uid": 10686, "src_term": 0,
           "src_term_name": "x .and. y?", "old_control": 23555,
           "old_label": "Automatic Error Handling", "want_census": LOCAL_CENSUS_BASE + 1},
    "B2": {"n": 2, "sink_term": 2, "wire_pin": 10990, "src_uid": 10757, "src_term": 1,
           "src_term_name": "element", "old_control": 23525,
           "old_label": "index", "want_census": LOCAL_CENSUS_BASE + 2},
}
PATHS = {s: {"a": os.path.join(g.CLAUDEDEV, "D1_s3b_row%da_%s.vi" % (r["n"], STAMP)),
             "final": os.path.join(g.CLAUDEDEV, "D1_s3b_row%d_%s.vi" % (r["n"], STAMP))}
         for s, r in ROWS.items()}

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 62 material #3: S3b's two rows, Pre-decided 53(d')/53(d'') order, four staged saves",
     "route_source": "docs/cycle27-plan.md Pre-decided 53(d')/53(d'') - NOT chosen here",
     "connect_verb_note": ("gscript.connect_terminals addresses TOP-LEVEL nodes only; the shipped writer for a "
                           "SINK on a nested diagram is OpConnectNested_v1 via connect_nested_v1, which is what "
                           "dispatch #2 called for this same connection"),
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True, "is_broken_read_above_a_save": False,
     "create_indicator_called": False, "connect_ctl_called": False,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's normal mechanism",
     "no_gui_action": True,
     "rig_state": "조립 / ASSEMBLED - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "gui_save": "NEVER called", "allow_broken": "NEVER True", "move_in": "not imported, not called",
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "stages": {}, "artefacts_on_disk": []}


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


# ============================================================ one BUILD stage = one row, two saves
def build_row(step, src_path, row):
    n = row["n"]
    pa, pf = PATHS[step]["a"], PATHS[step]["final"]
    print("\n========== %s  ROW %d on #%d t%d  (source #%d t%d %r -> indicator %r, control uid %d)"
          % (step, n, CASE_UID, row["sink_term"], row["src_uid"], row["src_term"], row["src_term_name"],
             row["old_label"], row["old_control"]), flush=True)
    K = R["stages"].setdefault(step, {"row": n, "from": os.path.basename(src_path),
                                      "step3_artefact": os.path.basename(pa),
                                      "step5_artefact": os.path.basename(pf),
                                      "saved_step3": False, "saved_step5": False})
    shutil.copy2(src_path, pf)                       # the WORKING file is the row's FINAL path
    g.open_panel(pf)
    time.sleep(1.0)
    es0 = read_exec_state(K, "%s [0] cold open of the bed" % step, pf)
    gate("%s_a the bed opens COLD at ExecState 1" % step, es0 == 1, "%r" % (es0,))
    dd = diagrams(pf, K)
    d639 = dd.get(D639)

    K["local_census_before"] = count_of(pf, "Local")
    K["control_terminal_census_before"] = count_of(pf, "ControlTerminal")
    fp0, _e0 = panel_all(pf, "%s BEFORE" % step)
    K["panel_rows_before_count"] = len(fp0)
    t637_0 = loop637_counts(pf, K, "%s BEFORE" % step)
    gate("%s_k0 #637 baseline reads %r as recorded" % (step, LOOP637_BASELINE),
         t637_0 == LOOP637_BASELINE, "%r" % (t637_0,))

    case_rows, _cl = node_table(pf, CASE_UID, "%s BEFORE #10407" % step)
    K["case_table_before"] = case_rows
    sink_row = next((r for r in case_rows if r["i"] == row["sink_term"]), None)
    K["sink_row_before"] = sink_row
    W = (sink_row or {}).get("wire")
    gate("%s_a2 #10407 t%d carries the wire this row replaces" % (step, row["sink_term"]),
         W == row["wire_pin"], "wire %r (the cycle-62 reading was %r)" % (W, row["wire_pin"]))

    src_rows, src_loc = node_table(pf, row["src_uid"], "%s BEFORE source" % step)
    K["source_table_before"] = src_rows
    src_row = next((r for r in src_rows if r["i"] == row["src_term"]), None)
    K["source_row_before"] = src_row
    src_name_live = (src_row or {}).get("name")
    K["source_terminal_name_read_off_the_machine"] = src_name_live
    gate("%s_a3 the source terminal's NAME reads off the machine as %r" % (step, row["src_term_name"]),
         src_name_live == row["src_term_name"],
         "%r (hex %r)" % (src_name_live, (src_row or {}).get("name_hex")))

    # ---- the EXISTING indicator: found by its own control uid, its label READ OFF THE MACHINE
    prow = next((r for r in fp0 if r["uid"] == row["old_control"]), None)
    K["existing_indicator_panel_row"] = prow
    live_label = (prow or {}).get("label")
    K["existing_indicator_label_read_off_the_machine"] = live_label
    K["existing_indicator_label_hex"] = (live_label or "").encode("utf-8").hex()
    try:
        fpl = g.fp_labels(pf)
    except Exception as e:                                                         # noqa: BLE001
        fpl = []
        K["fp_labels_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    hits = [(i, t, ind) for (i, t, ind) in fpl if t == live_label]
    K["existing_indicator_fp_rows"] = hits
    fact("%s the EXISTING indicator (control uid %d): panel row %r ; label READ OFF THE MACHINE %r (hex %r) ; "
         "front-panel rows carrying that label: %r"
         % (step, row["old_control"], prow, live_label, K["existing_indicator_label_hex"], hits))
    if not gate("%s_c the EXISTING indicator is found by its own control uid and EXACTLY ONE front-panel row "
                "carries its label" % step, bool(live_label) and len(hits) == 1,
                "label %r rows %r (the recorded label was %r)" % (live_label, hits, row["old_label"])):
        return abandon(step, K, pf, "the existing indicator's label/panel row is ambiguous or missing", row)
    gate("%s_c2 that label equals the one this row was planned against" % step, live_label == row["old_label"],
         "live %r vs recorded %r" % (live_label, row["old_label"]))

    # ---- 1. delete the whole Wire object
    gone = delete_wire_uid(pf, W, K, "%s [1]" % step)
    gate("%s_b the delete removed EXACTLY the wire uid targeted" % step, gone == [W],
         "gone %r, targeted %r" % (gone, W))
    es1 = read_exec_state(K, "%s [1] after the delete (0 is EXPECTED)" % step, pf)
    K["exec_state_after_delete"] = es1

    # ---- 2. the Local, in READ mode, bound to the EXISTING indicator
    bool_label, _fpl_donor = donor_bool_label()
    K["donor_direction_control_label"] = bool_label
    if not gate("%s_d0 the donor's direction control was identified on the machine" % step,
                bool(bool_label), "%r" % (bool_label,)):
        return abandon(step, K, pf, "the donor's Write? control could not be identified", row)
    rd = call_donor(pf, hits[0][0], bool_label, K, "%s [2]" % step)
    gate("%s_d the Local census went %r -> %r (want %r)"
         % (step, rd["local_census_before"], rd["local_census_after"], row["want_census"]),
         rd["local_census_after"] == row["want_census"], "added %r" % (rd["local_uids_added"],))
    if len(rd["local_uids_added"]) != 1:
        return abandon(step, K, pf, "the donor added %r Locals" % (len(rd["local_uids_added"]),), row)
    local_uid = rd["local_uids_added"][0]
    read_exec_state(K, "%s [2] after the Local was created (unwired: 0 is EXPECTED)" % step, pf)

    # ---- THE RULE-1a GATE (50(i)): read the Local back with node_terms
    lrows, lloc = node_table(pf, local_uid, "%s the new Local" % step)
    K["local_readback"] = {"uid": local_uid, "loc": lloc, "terminal_rows_verbatim": lrows}
    one = lrows[0] if len(lrows) == 1 else {}
    fact("%s LOCAL READBACK VERBATIM: Local #%s -> %d terminal(s); NAME %r (hex %r), is_source %r, wire %r ; "
         "owner %r#%r diagram %r Nodes[%r]"
         % (step, local_uid, len(lrows), one.get("name"), one.get("name_hex"), one.get("is_source"),
            one.get("wire"), lloc.get("owner_class"), lloc.get("owner_uid"), lloc.get("diagram_index"),
            lloc.get("nodes_index")))
    gate("%s_e RULE-1a GATE (50(i)): ONE terminal, NAME == the indicator label it was created from, "
         "is_source True (= READ)" % step,
         len(lrows) == 1 and one.get("name") == live_label and one.get("is_source") is True,
         "name %r (hex %r) vs label %r (hex %r) ; is_source %r"
         % (one.get("name"), one.get("name_hex"), live_label, K["existing_indicator_label_hex"],
            one.get("is_source")))

    # ---- 3. connect the Local's SOURCE into the freed #10407 sink
    _cr, case_loc = node_table(pf, CASE_UID, "%s #10407 before the connect" % step)
    sink_i = case_loc.get("nodes_index")
    src_diag, src_i = lloc.get("diagram_index"), lloc.get("nodes_index")
    K["connect_call"] = ("connect_nested_v1(target, sink_diag=%r, sink_node=%r, sink_term=%r, src_diag=%r, "
                         "src_node=%r, src_term=%r)" % (d639, sink_i, row["sink_term"], src_diag, src_i,
                                                        one.get("i", 0)))
    fact("%s [3] CONNECT: %s" % (step, K["connect_call"]))
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es_c, err_c = CONNECT_V1(pf, d639, sink_i, row["sink_term"], src_diag, src_i,
                                         one.get("i", 0), V1_LABELS)
        K["connect_result"] = {"wire_delta": dw, "exec_state_returned": es_c, "error_verbatim": err_c}
    except Exception as e:                                                         # noqa: BLE001
        K["connect_result"] = {"wire_delta": None, "exec_state_returned": None,
                               "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])}
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    fact("%s [3] connect result: %r" % (step, K["connect_result"]))

    case_rows2, _c2 = node_table(pf, CASE_UID, "%s AFTER the connect #10407" % step)
    K["case_table_after_connect"] = case_rows2
    sink_after = next((r for r in case_rows2 if r["i"] == row["sink_term"]), None)
    K["sink_row_after_connect"] = sink_after
    lrows2, _l2 = node_table(pf, local_uid, "%s the Local AFTER the connect" % step)
    K["local_table_after_connect"] = lrows2
    K["new_sink_wire"] = (sink_after or {}).get("wire")
    K["far_end_owner_uid"] = local_uid
    K["far_end_terminal_name"] = (lrows2[0].get("name") if lrows2 else None)
    far_ok = bool(K["new_sink_wire"]) and bool(lrows2 and lrows2[0].get("wire")) \
        and K["new_sink_wire"] == lrows2[0].get("wire")
    fact("%s [3] #10407 t%d now carries wire %r ; the far end is LOCAL #%s, terminal %r name %r (the Local's "
         "own wire reads %r)" % (step, row["sink_term"], K["new_sink_wire"], local_uid,
                                 (lrows2[0].get("i") if lrows2 else None), K["far_end_terminal_name"],
                                 (lrows2[0].get("wire") if lrows2 else None)))
    gate("%s_g #10407 t%d carries a NEW wire whose far end is the LOCAL (owner uid %r, terminal name %r)"
         % (step, row["sink_term"], local_uid, K["far_end_terminal_name"]), far_ok,
         "sink wire %r, local wire %r" % (K["new_sink_wire"], (lrows2[0].get("wire") if lrows2 else None)))

    # ---- the STEP-3 SAVE, IFF ExecState == 1. NO `Is Broken?` IS READ ABOVE THIS POINT (52(f)).
    es3 = read_exec_state(K, "%s [3] immediately before the step-3 save decision" % step, pf)
    K["exec_state_at_step3"] = es3
    if es3 != 1:
        return abandon(step, K, pf, "step 3: ExecState reads %r where 1 is required" % (es3,), row)
    try:
        g.save(pf)
        shutil.copy2(pf, pa)                        # the step-3 state, preserved as its own artefact
        K["save3_error_verbatim"] = ""
    except Exception as e:                                                        # noqa: BLE001
        K["save3_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    ff3 = D.file_facts("%s the STEP-3 artefact" % step, pa)
    K["file_facts_step3"] = ff3
    K["saved_step3"] = bool(ff3.get("exists"))
    R["artefacts_on_disk"].append({"stage": "%s step3" % step, "path": pa, "md5": ff3.get("md5"),
                                   "size": ff3.get("size")})
    gate("%s_f *** THE ROW'S GUARANTEED ARTEFACT: ExecState 1 at step 3 and the file exists ***" % step,
         es3 == 1 and bool(ff3.get("exists")) and not K["save3_error_verbatim"],
         "%s md5 %r size %r error %r" % (os.path.basename(pa), ff3.get("md5"), ff3.get("size"),
                                         K["save3_error_verbatim"]))
    dump()

    # ---- 4. re-feed the EXISTING indicator from the bared source
    node_class, ni_f = traverse_index_of(pf, row["src_uid"], K, "%s [4]" % step)
    K["wire_indicators_call"] = ("g.wire_indicators(target, node_index=%r, src_terms=[%r], "
                                 "indicator_names=[%r], diagram_index=%r, node_class=%r)"
                                 % (ni_f, src_name_live, live_label, d639, node_class))
    fact("%s [4] CALL: %s" % (step, K["wire_indicators_call"]))
    if not isinstance(ni_f, int) or not isinstance(d639, int):
        K["wire_indicators_error_verbatim"] = "NOT ATTEMPTED: node_class/index %r/%r, d639 %r" \
            % (node_class, ni_f, d639)
        fact("%s [4] %s" % (step, K["wire_indicators_error_verbatim"]))
        K["wire_indicators_returned"] = None
    else:
        try:
            K["wire_indicators_returned"] = g.wire_indicators(pf, ni_f, [src_name_live], [live_label],
                                                              diagram_index=d639, node_class=node_class)
            K["wire_indicators_error_verbatim"] = ""
        except Exception as e:                                                    # noqa: BLE001
            K["wire_indicators_returned"] = None
            K["wire_indicators_error_verbatim"] = "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])
    fact("%s [4] wire_indicators returned %r ; raised %r  (a raise here is a READING - gscript.py:1794-1797 "
         "tests exec_state ABSOLUTELY; the T3 separator below is what decides)"
         % (step, K["wire_indicators_returned"], K["wire_indicators_error_verbatim"]))
    es4 = read_exec_state(K, "%s [4] after wire_indicators" % step, pf)
    K["exec_state_after_wire_indicators"] = es4

    src_rows3, _s3 = node_table(pf, row["src_uid"], "%s AFTER wire_indicators source" % step)
    K["source_table_after"] = src_rows3
    sr3 = next((r for r in src_rows3 if r["i"] == row["src_term"]), None)
    K["source_row_after"] = sr3
    IND_W = (sr3 or {}).get("wire")
    K["indicator_wire_uid_read_off_the_machine"] = IND_W
    gate("%s_h wire_indicators left a NON-ZERO wire on the source #%d t%d"
         % (step, row["src_uid"], row["src_term"]), bool(IND_W), "wire %r ; row %r" % (IND_W, sr3))

    # ---- the T3 SEPARATOR on the re-fed indicator net (read-only, NO `Is Broken?`)
    t3 = t3_separator(pf, IND_W, d639, K, "%s [4]" % step)
    sink_uids = [m.get("node_uid") for m in t3.get("sinks", [])]
    own_sink = row["old_control"] in sink_uids
    gate("%s_i *** THE T3 SEPARATOR: EXACTLY ONE source on wire %r, and its sink is THIS row's own panel "
         "control uid %d ***" % (step, IND_W, row["old_control"]),
         t3.get("source_count") == 1 and own_sink,
         "sources %r -> %r ; sinks %r (want %d among them)"
         % (t3.get("source_count"), t3.get("sources"), sink_uids, row["old_control"]))

    t637_1 = loop637_counts(pf, K, "%s AFTER" % step)
    K["loop637_before"], K["loop637_after"] = t637_0, t637_1
    gate("%s_k #637 terminal/wired counts UNCHANGED (no tunnel, no border object - 50(e)/37(e))" % step,
         t637_0 == t637_1, "%r -> %r" % (t637_0, t637_1))
    fp2, _e2 = panel_all(pf, "%s AFTER" % step)
    K["panel_rows_after_count"] = len(fp2)
    K["control_terminal_census_after"] = count_of(pf, "ControlTerminal")
    gate("%s_l the ControlTerminal census is unchanged at %d - no panel object created or deleted (53(d'))"
         % (step, CT_CENSUS_BASELINE),
         K["control_terminal_census_before"] == K["control_terminal_census_after"] == CT_CENSUS_BASELINE,
         "%r -> %r ; panel rows %r -> %r" % (K["control_terminal_census_before"],
                                             K["control_terminal_census_after"],
                                             K["panel_rows_before_count"], K["panel_rows_after_count"]))

    # ---- 5. the STEP-5 SAVE, IFF ExecState == 1
    es5 = read_exec_state(K, "%s [5] immediately before the step-5 save decision" % step, pf)
    K["exec_state_at_step5"] = es5
    if es5 != 1:
        return abandon(step, K, pf, "step 5: ExecState reads %r where 1 is required" % (es5,), row,
                       keep_step3=True)
    try:
        g.save(pf)
        K["save5_error_verbatim"] = ""
    except Exception as e:                                                        # noqa: BLE001
        K["save5_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    close_quietly(pf)
    ff5 = D.file_facts("%s the STEP-5 artefact" % step, pf)
    K["file_facts_step5"] = ff5
    K["saved_step5"] = bool(ff5.get("exists"))
    R["artefacts_on_disk"].append({"stage": "%s step5" % step, "path": pf, "md5": ff5.get("md5"),
                                   "size": ff5.get("size")})
    gate("%s_j *** THE ROW'S FINAL ARTEFACT: ExecState 1 after wire_indicators and the file exists ***" % step,
         es5 == 1 and bool(ff5.get("exists")) and not K["save5_error_verbatim"],
         "%s md5 %r size %r error %r" % (os.path.basename(pf), ff5.get("md5"), ff5.get("size"),
                                         K["save5_error_verbatim"]))
    K.update({"local_uid": local_uid, "new_wire_uid": K["new_sink_wire"], "sink_nodes_index": sink_i,
              "src_diag_of_local": src_diag, "src_nodes_index_of_local": src_i,
              "local_term_index": one.get("i", 0)})
    dump()
    return pf


def abandon(step, K, out_path, why, row, keep_step3=False):
    K["abandoned_because"] = why
    fact("%s ROW STOPPED: %s - nothing further is saved for this row, the working copy is removed. Files "
         "already saved at an earlier step STAY SAVED. No second construction, no cast, no splice (51(h))."
         % (step, why))
    read_exec_state(K, "%s at the stop" % step, out_path)
    for label, uid in (("#10407", CASE_UID), ("source #%d" % row["src_uid"], row["src_uid"]),
                       ("the new Local", K.get("local_readback", {}).get("uid"))):
        if uid is None:
            continue
        rows, _l = node_table(out_path, uid, "%s STOP REPORT %s" % (step, label))
        K.setdefault("stop_report_tables", {})[label] = rows
    try:
        prows, _pe = panel_all(out_path, "%s STOP REPORT panel" % step)
        K.setdefault("stop_report_tables", {})["the indicator's panel row"] = \
            [r for r in prows if r.get("uid") == row["old_control"]]
        fact("%s STOP REPORT - the indicator's panel row (control uid %d): %r"
             % (step, row["old_control"], K["stop_report_tables"]["the indicator's panel row"]))
    except Exception as e:                                                        # noqa: BLE001
        fact("%s STOP REPORT panel read raised %s: %s" % (step, type(e).__name__, str(e)[:200]))
    close_quietly(out_path)
    if os.path.exists(out_path):
        try:
            os.remove(out_path)
        except Exception as e:                                                    # noqa: BLE001
            fact("%s could not remove %s: %s" % (step, out_path, e))
    K["working_copy_removed"] = not os.path.exists(out_path)
    K["step3_artefact_kept"] = keep_step3 and os.path.exists(PATHS[step]["a"])
    fact("%s the working copy %s is removed: %r ; the step-3 artefact %s is kept: %r"
         % (step, os.path.basename(out_path), K["working_copy_removed"], os.path.basename(PATHS[step]["a"]),
            os.path.exists(PATHS[step]["a"])))
    dump()
    return None


# ============================================================ the ORDERED `Is Broken?` pass (42(b)) - LAST
def ordered_pass(target, step):
    src = R["stages"].get(step, {})
    P = src.setdefault("ordered_pass", {})
    need = ("sink_nodes_index", "local_term_index", "src_nodes_index_of_local", "src_diag_of_local")
    if not all(src.get(k) is not None for k in need):
        P["not_attempted_because"] = "the row did not reach a wired state; %r" % ({k: src.get(k)
                                                                                   for k in need},)
        fact("%s ORDERED PASS NOT ATTEMPTED: %s" % (step, P["not_attempted_because"]))
        gate("E_%s the ORDERED `Is Broken?` reads False on the new #10407 wire" % step, False,
             "NOT ATTEMPTED: %s" % P["not_attempted_because"])
        return
    dd = diagrams(target, P)
    d639 = dd.get(D639)
    _cr, loc = node_table(target, CASE_UID, "%s ordered pass #10407" % step)
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
    except Exception as e:                                                        # noqa: BLE001
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
            except Exception as e:                                                # noqa: BLE001
                rd[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:60])
    except Exception as e:                                                        # noqa: BLE001
        rd["_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
    P["op_indicators"] = rd
    ib = rd.get("Is Broken?")
    P["is_broken_ordered"] = ib
    fact("%s ORDERED `Is Broken?` = %r on wire uid %r (wire_delta %r - expected 0, op error %r)"
         % (step, ib, rd.get("UID 2"), P.get("wire_delta"), P.get("error_verbatim")))
    gate("E_%s the ORDERED `Is Broken?` reads False on the new #10407 wire" % step, ib is False,
         "Is Broken? %r on wire %r ; wire_delta %r" % (ib, rd.get("UID 2"), P.get("wire_delta")))
    read_exec_state(None, "%s after the Is Broken? read (SUSPECT, NAMES.md:912-918; every save is done)"
                    % step, target)


# ============================================================ MAIN
def main():
    print("=== diag_c62_s3b_build  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== S3b's two rows, Pre-decided 53(d')/53(d'') order, FOUR staged saves", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 D1_s2_loops.vi", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 D1_s3a_focus_ind.vi (row 1's SOURCE, never written)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    dn = probe("T4 the donor OpCreateLocalRead_v0.vi", DONOR)
    gate("T4 OpCreateLocalRead_v0.vi md5 == %s" % DONOR_MD5, dn.get("md5") == DONOR_MD5, dn.get("md5", "?"))

    D.fresh("T5 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    b1 = b2 = None
    try:
        b1 = build_row("B1", S3A_ARTEFACT, ROWS["B1"])
    except Stop as s:
        fact("B1 STOPPED: %s" % s)
    except Exception as e:                                                        # noqa: BLE001
        fact("B1 RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
        R["stages"].setdefault("B1", {})["raised"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        close_quietly(PATHS["B1"]["final"])
    dump()

    if b1:
        try:
            D.fresh("B2 RESTART (a fresh LabVIEW before the next staged step)")
            R["handles"]["after_b2_restart"] = labview_handles()
            b2 = build_row("B2", b1, ROWS["B2"])
        except Stop as s:
            fact("B2 STOPPED: %s" % s)
        except Exception as e:                                                    # noqa: BLE001
            fact("B2 RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
            R["stages"].setdefault("B2", {})["raised"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            close_quietly(PATHS["B2"]["final"])
    else:
        gate("B2_skip B2 was NOT reached (it starts from ROW 1's saved step-5 file)", False,
             "B1 produced no step-5 file")
    dump()

    # ---- C: the COLD reopen in a freshly restarted LabVIEW, then E: the ordered pass, LAST
    if b2:
        print("\n========== C  COLD reopen of ROW 2's final file in a freshly restarted LabVIEW", flush=True)
        D.fresh("C RESTART before the cold reopen")
        R["handles"]["after_c_restart"] = labview_handles()
        try:
            g.open_panel(b2)
            time.sleep(1.0)
        except Exception as e:                                                    # noqa: BLE001
            fact("C open_panel raised %s: %s" % (type(e).__name__, str(e)[:300]))
        es_cold = read_exec_state(None, "C COLD, freshly restarted LabVIEW", b2)
        R["cold_exec_state"] = es_cold
        gate("C_1 *** THE ARTEFACT'S PASS CRITERION: COLD ExecState == 1 ***", es_cold == 1, "%r" % (es_cold,))
        print("\n========== E  the ORDERED `Is Broken?` pass (42(b)) - LAST, after the cold reopen",
              flush=True)
        for step in ("B1", "B2"):
            ordered_pass(b2, step)
        close_quietly(b2)
    else:
        gate("C_1 *** THE ARTEFACT'S PASS CRITERION: COLD ExecState == 1 ***", False,
             "NOT REACHED: no ROW 2 final artefact")
        for step in ("B1", "B2"):
            gate("E_%s the ORDERED `Is Broken?` reads False on the new #10407 wire" % step, False,
                 "NOT REACHED: no ROW 2 final artefact")
    dump()

    print("\n--- Z: the closing facts", flush=True)
    R["ref_counts"] = g.ref_counts()
    fact("refs %r" % (R["ref_counts"],))
    try:
        g.reset()
    except Exception as e:                                                        # noqa: BLE001
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

    # the saved artefacts, re-read AFTER the ordered pass (which perturbs memory, never the files)
    R["artefacts_after_the_ordered_pass"] = []
    for a in R["artefacts_on_disk"]:
        ff = D.file_facts("Z2 %s re-read after the ordered pass" % a["stage"], a["path"])
        R["artefacts_after_the_ordered_pass"].append({"stage": a["stage"], "path": a["path"],
                                                      "md5": ff.get("md5"), "size": ff.get("size"),
                                                      "exists": ff.get("exists")})
        gate("Z_2 %s md5 unchanged after the ordered pass" % a["stage"],
             ff.get("exists") and ff.get("md5") == a["md5"],
             "%s: %r vs %r" % (os.path.basename(a["path"]), a["md5"], ff.get("md5")))

    left = [p for p in os.listdir(g.CLAUDEDEV) if p.startswith("SCRATCH_C62B_")]
    gate("Z_3 no scratch of this run is left behind", not left, "still present: %r" % (left,))
    rc = R["ref_counts"] or {}
    gate("Z_1c refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    gate("Z_1e no `Wire.Is Broken?` was read above any save",
         R["is_broken_read_above_a_save"] is False, "52(f) / docs/NAMES.md:912-918")
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
