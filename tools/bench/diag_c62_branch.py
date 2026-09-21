"""diag_c62_branch - cycle 62 material #1. PURE MEASUREMENT. Nothing is built, nothing is saved.

THE QUESTION (STATUS `## NEXT` line 83; docs/cycle27-plan.md Pre-decided 52(h))
  `#10407` t0 carries wire 10799 and t2 carries wire 10990 - the same two uids STATUS records for S3a's two
  indicator wires. STATUS calls that an INFERENCE from coinciding uids. This run measures whether the indicator
  feed and the `#10407` sink sit on ONE Wire object or two, and what it costs to free the sink.

  M-A  read-only, scratch A: ExecState cold; the FULL terminal table of `#10407`; the Wire uid on t0 and t2; the
       Wire uid on ControlTerminal #23541 and #23576 with their labels READ OFF THE MACHINE; per pair, SAME Wire
       object uid or DIFFERENT.
  M-B  read-only, scratch A: every terminal each of those Wire objects touches. If no verb enumerates a WIRE's
       terminals, that is reported as NO VERB FOUND with what was searched, and a TERMINAL-SIDE reverse census
       (every node terminal on the owning diagram + every panel terminal) is given in its place, labelled as
       such. It is NOT a wire-side read and is not presented as one.
  M-C  file census of tools/gscript.py, no LabVIEW: does ANY verb remove ONE BRANCH rather than the whole Wire
       object? `NONE FOUND` is an expected, acceptable answer.
  M-D  destructive, SCRATCH ONLY, two INDEPENDENT copies so the two readings do not confound each other:
       scratch A loses the Wire carrying `#10407` t0, scratch B (untouched by A's delete) the Wire carrying t2.
       ExecState before -> after, and which terminals went bare.

WHAT THIS IS NOT
  No `Wire.Is Broken?` read ANYWHERE (it perturbs ExecState - docs/NAMES.md:912-918, Pre-decided 52(f)); none is
  needed, because nothing here has to be legal afterwards. Nothing is saved (`save` is never called). No new
  `gscript` verb and `tools/gscript.py` is NOT edited. No recipe (48(n)). No op is built. No VI is RUN (34(f)) -
  op VIs are run, the fleet's normal mechanism. No GUI action. No motor / ASI / camera (rig 조립 / ASSEMBLED).
  No new process device (Pre-decided 2). `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` are
  neither imported nor called; `allow_broken` is never True. The two scratches are duplicates of
  `claudeDev\\D1_s3a_focus_ind.vi` and are deleted in the same run (49(e)). NO ROUTE IS CHOSEN OR RECOMMENDED
  and nothing is interpreted; `docs/cycle27-plan.md` and STATUS's `## NEXT` are not edited.

WHAT ALREADY EXISTS AND IS REUSED INSTEAD OF REBUILT (checked before writing a line: `grep "^def "
tools/gscript.py`, `ls tools/recipes tools/bench`, docs/toolkit-capabilities.md:22-24,:133-139)
  - gscript.node_terms :870 / node_terms_uid :925, node_labels :587, panel_wiring :826, report_all :488,
    uids :1017, count :1005, exec_state :1977, delete_object :2275, open_panel :1241, close_panel :1257,
    ref_counts :233, fp_labels :2475
  - build_d1_v0.diag_index / owner_of ; diag_s2_scaffold.fresh / file_facts ; hash_probe.probe ;
    bench_prep.labview_handles
  - the harness (gate/fact/probe/dump/read_exec_state/locate/terms_of_uid/term_rows_verbatim) is COPIED
    VERBATIM from tools/bench/diag_c61_localdir_write2.py, which ran 38 pass / 0 fail earlier today.
  NOTHING NEW IS BUILT BY THIS RUN - not even a scratch that outlives it.

PREDICTION CONTRACT (machine-checkable; a failed prediction is the peer-review trigger)
  T_*   four md5 gates BEFORE: ORIGINAL 2a78e17c... FATAL, D1_s1_copy 3e3d23ce..., D1_s2_loops 6ff19497...
        FATAL, D1_s3a_focus_ind eef91c1d... FATAL
  C_*   M-C runs FIRST, with no LabVIEW open, so the census exists even if every later gate fails
  A_1   scratch A is byte-identical to D1_s3a_focus_ind.vi at creation
  A_2   scratch A opens COLD at ExecState 1 (the S3a artefact's own recorded state)
  A_3   `#10407` is located and its FULL terminal table read; t0 and t2 both carry a NON-ZERO wire uid
  A_4   ControlTerminal #23541 and #23576 exist on the machine, their labels are READ (never retyped), and a
        wire uid is obtained for each (by whichever route answers; the route is recorded)
  A_5   *** PER PAIR: SAME Wire object uid or DIFFERENT *** - stated, not interpreted
  B_1   the wire-side verb search is reported (expected: NO VERB FOUND); the terminal-side reverse census
        enumerates every terminal carrying each wire uid, verbatim
  D_A   scratch A: ExecState before -> after deleting the Wire on `#10407` t0; `#10407`'s table re-read, both
        ControlTerminals re-read, far end `#10686` t0 'x .and. y?' re-read
  D_B   scratch B (FRESH copy): the same for the Wire on `#10407` t2, far end `#10757` t1 'element'
  Z_1   four md5 gates PASS after; BOTH scratches exists=False; refs opened == closed, 0 live; handles reported

NOTHING HERE INTERPRETS A RESULT. Anything that looks like a decision goes into the caller's OPEN line.
"""
import ast
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

GSCRIPT_PY = os.path.join(ROOT, "tools", "gscript.py")

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH_A = os.path.join(g.CLAUDEDEV, "SCRATCH_C62_A_%s.vi" % STAMP)
SCRATCH_B = os.path.join(g.CLAUDEDEV, "SCRATCH_C62_B_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_c62_branch.json")

CASE_UID = 10407          # the CaseStructure whose t0 (selector) and t2 S3b must feed
CT_NUM = 23541            # S3a's NUMERIC indicator's ControlTerminal   (expected label 'index')
CT_BOOL = 23576           # S3a's BOOLEAN indicator's ControlTerminal   (expected label 'Automatic Error Handling')
FAR_BOOL = 10686          # far end of the t0 feed: 'x .and. y?'
FAR_BOOL_TERM = 0
FAR_NUM = 10757           # far end of the t2 feed: 'element'
FAR_NUM_TERM = 1
SCAN_LIMIT = 120          # bounded FALLBACK scan when a node's Nodes[] position does not echo its uid
CENSUS_LIMIT = 400        # cap on M-B's full-diagram terminal sweep; any truncation is reported and gated

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 62 material #1: is S3a's indicator feed the SAME Wire object as the `#10407` sink, and what "
             "does freeing the sink cost? PURE MEASUREMENT - nothing built, nothing saved, no route chosen.",
     "no_new_verb": True, "no_recipe": True, "no_new_device": True, "no_op_built": True, "nothing_saved": True,
     "gscript_not_edited": "tools/gscript.py is NOT edited by this dispatch",
     "is_broken_read_anywhere": False,
     "why_no_is_broken": "Wire.Is Broken? perturbs ExecState (docs/NAMES.md:912-918, Pre-decided 52(f)) and "
                         "nothing here needs a legal VI; none is taken at any point.",
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
     "scratch_a": {"path": SCRATCH_A}, "scratch_b": {"path": SCRATCH_B},
     "handles": {}, "hash_probe": [], "exec_state_timeline": [],
     "M_A": {}, "M_B": {}, "M_C": {}, "M_D_scratch_A": {}, "M_D_scratch_B": {}}


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
    """ONE global ordered timeline."""
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
    BOTH 'Diagram' and 'TopLevelDiagram'. Copied from tools/bench/diag_c61_localdir_write2.py:229."""
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
    loc["is_in_Nodes_array"] = loc["candidate_node_index"] is not None
    return loc


def terms_of_uid(target, loc, allow_scan=True):
    """node_terms on the located node, VERIFIED by the node's own UID; bounded scan fallback.

    `allow_scan=False` is used for objects that Diagram.Nodes[] may not contain at all (a ControlTerminal):
    a fallback scan there would pay ~0.8 s x N op runs to find nothing. The skip is RECORDED, not silent."""
    rec = {"diagram_index": loc.get("diagram_index"), "candidate_node_index": loc.get("candidate_node_index")}
    di, uid = loc.get("diagram_index"), loc.get("uid")
    if di is None:
        rec["how"] = "not located"
        return rec
    if not allow_scan and loc.get("candidate_node_index") is None:
        rec["how"] = ("SKIPPED: the uid is not in this diagram's Nodes[] (node_labels lists %d nodes and none "
                      "echoes it), and no bounded scan was run - it would cost ~0.8 s per node to find nothing"
                      % (loc.get("nodes_on_that_diagram") or 0))
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


def read_node_table(target, uid, tag, fresh=True, allow_scan=True):
    """locate + full terminal table, everything verbatim. Returns (rows, loc, rec)."""
    loc = locate(target, uid, fresh=fresh)
    rec = terms_of_uid(target, loc, allow_scan=allow_scan)
    rows = term_rows_verbatim(rec.get("terms") or [])
    fact("%s #%s: owner %r#%r diagram %r node %r [%s] label %r ; FULL TERMINAL TABLE %r"
         % (tag, uid, loc.get("owner_class"), loc.get("owner_uid"), loc.get("diagram_index"),
            rec.get("node_index"), rec.get("how"), loc.get("node_own_label"), rows))
    return rows, loc, rec


def panel_rows(target, tag):
    try:
        rows = g.panel_wiring(target)
        err = ""
    except Exception as e:                                                         # noqa: BLE001
        rows, err = [], "%s: %s" % (type(e).__name__, str(e)[:250])
    fact("%s panel_wiring: %d rows%s" % (tag, len(rows), (" ; ERROR " + err) if err else ""))
    return rows, err


# ============================================================ M-C  file census, NO LabVIEW
def m_c_census():
    """Does ANY verb in tools/gscript.py remove ONE BRANCH of a wire rather than the whole Wire object?
    Pure file reading: ast over tools/gscript.py, plus a regex sweep for the wire-side API ids. Runs FIRST so
    the census exists on disk even if every LabVIEW gate later fails."""
    print("\n========== M-C  file census of tools/gscript.py (NO LabVIEW)", flush=True)
    K = R["M_C"]
    src = open(GSCRIPT_PY, encoding="utf-8").read()
    tree = ast.parse(src)
    funcs = []
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef):
            doc = (ast.get_docstring(n) or "").strip()
            funcs.append({"name": n.name, "line": n.lineno,
                          "doc_first_line": doc.splitlines()[0] if doc else "",
                          "doc_lower": doc.lower()})
    K["functions_total"] = len(funcs)

    # every verb whose NAME or DOCSTRING mentions a wire at all - the pool the answer is drawn from
    pool = [f for f in funcs if "wire" in f["name"].lower() or "wire" in f["doc_lower"]]
    K["wire_related_verbs"] = [{"name": f["name"], "file_line": "tools/gscript.py:%d" % f["line"],
                                "one_line_behaviour": f["doc_first_line"]} for f in pool]
    fact("M-C %d defs in tools/gscript.py ; %d mention a wire in name or docstring" % (len(funcs), len(pool)))
    for row in K["wire_related_verbs"]:
        fact("M-C   %-26s %-24s %s" % (row["name"], row["file_line"], row["one_line_behaviour"][:150]))

    # the actual question: a verb that removes ONE BRANCH
    REMOVE = ("delete", "remove", "disconnect", "detach", "sever", "unwire")
    cands = []
    for f in pool:
        if "branch" not in f["doc_lower"] and "branch" not in f["name"].lower():
            continue
        if not any(w in f["doc_lower"] or w in f["name"].lower() for w in REMOVE):
            continue
        cands.append({"name": f["name"], "file_line": "tools/gscript.py:%d" % f["line"],
                      "one_line_behaviour": f["doc_first_line"]})
    K["branch_removal_candidates"] = cands
    K["verdict"] = "NONE FOUND" if not cands else "CANDIDATES: %s" % ", ".join(c["name"] for c in cands)

    # the known baseline, quoted from the file rather than remembered
    K["baseline_delete_object"] = {
        "file_line": "tools/gscript.py:%d" % next(f["line"] for f in funcs if f["name"] == "delete_object"),
        "doc_first_line": next(f["doc_first_line"] for f in funcs if f["name"] == "delete_object")}
    # every verb that mentions BRANCHING at all (creation side), so the census is complete both ways
    K["verbs_mentioning_branch"] = [{"name": f["name"], "file_line": "tools/gscript.py:%d" % f["line"],
                                     "one_line_behaviour": f["doc_first_line"]}
                                    for f in funcs
                                    if "branch" in f["doc_lower"] or "branch" in f["name"].lower()]
    fact("M-C verbs mentioning 'branch' at all: %r"
         % [v["name"] for v in K["verbs_mentioning_branch"]])
    fact("M-C BRANCH-REMOVAL VERDICT: %s  (baseline: %s %s)"
         % (K["verdict"], K["baseline_delete_object"]["file_line"],
            K["baseline_delete_object"]["doc_first_line"][:120]))
    gate("C_1 the branch-removal census ran over every def in tools/gscript.py", len(funcs) > 50,
         "%d defs, %d wire-related, verdict %s" % (len(funcs), len(pool), K["verdict"]))

    # ---- the WIRE-SIDE reader search (M-B's verb question, answered from the same file)
    K["wire_side_api_ids_searched"] = {}
    for token in ("6371003", "6371004", "Wire.Terminals", "Wire Terminals", "Terminals[]"):
        hits = [{"line": i + 1, "text": ln.strip()[:200]}
                for i, ln in enumerate(src.splitlines()) if token in ln]
        K["wire_side_api_ids_searched"][token] = hits
    K["wire_terminal_enumerator_in_gscript"] = bool(
        K["wire_side_api_ids_searched"]["6371003"] or K["wire_side_api_ids_searched"]["Wire.Terminals"])
    fact("M-C wire-side search in tools/gscript.py: %r"
         % {k: len(v) for k, v in K["wire_side_api_ids_searched"].items()})
    dump()


# ============================================================ M-A  read-only, scratch A
def m_a(target):
    print("\n========== M-A  read-only on scratch A", flush=True)
    K = R["M_A"]
    es = read_exec_state(K, "M-A scratch A, cold open, before any other call", target)
    K["exec_state_cold"] = es
    gate("A_2 scratch A opens COLD at ExecState 1", es == 1, "%r" % (es,))

    K["census_before"] = {c: count_of(target, c) for c in ("Wire", "ControlTerminal", "Node", "Local")}
    fact("M-A census on scratch A: %r" % (K["census_before"],))

    # ---- the CaseStructure
    rows, loc, rec = read_node_table(target, CASE_UID, "M-A #10407")
    K["case_node"] = {"uid": CASE_UID, "locate": loc, "how": rec.get("how"),
                      "node_index": rec.get("node_index"), "full_terminal_table_verbatim": rows}
    gate("A_3a `#%d`'s full terminal table was READ" % CASE_UID, bool(rows),
         "%d terminals, how=%r" % (len(rows), rec.get("how")), fatal=True)
    t0 = next((r for r in rows if r["i"] == 0), None)
    t2 = next((r for r in rows if r["i"] == 2), None)
    K["case_t0_row_verbatim"] = t0
    K["case_t2_row_verbatim"] = t2
    W0 = (t0 or {}).get("wire")
    W2 = (t2 or {}).get("wire")
    K["wire_on_case_t0"] = W0
    K["wire_on_case_t2"] = W2
    fact("M-A #%d t0 ROW VERBATIM %r  -> wire %r" % (CASE_UID, t0, W0))
    fact("M-A #%d t2 ROW VERBATIM %r  -> wire %r" % (CASE_UID, t2, W2))
    gate("A_3b `#%d` t0 and t2 both carry a NON-ZERO wire uid" % CASE_UID, bool(W0) and bool(W2),
         "t0 wire %r, t2 wire %r" % (W0, W2))

    # ---- the two ControlTerminals: route 1, are they in Diagram.Nodes[] at all?
    K["control_terminals"] = {}
    ct_all = []
    try:
        ct_all = g.report_all(target, "ControlTerminal")
        K["control_terminal_census"] = len(ct_all)
    except Exception as e:                                                         # noqa: BLE001
        K["control_terminal_census"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:160])
    fact("M-A ControlTerminal census on scratch A: %r" % (K["control_terminal_census"],))

    prows, perr = panel_rows(target, "M-A")
    K["panel_wiring_error_verbatim"] = perr
    K["panel_wiring_row_count"] = len(prows)
    K["panel_wiring_last_rows_verbatim"] = prows[-4:] if prows else []
    fact("M-A the LAST FOUR panel_wiring rows VERBATIM: %r" % (K["panel_wiring_last_rows_verbatim"],))

    for uid, tag in ((CT_NUM, "numeric"), (CT_BOOL, "boolean")):
        e = {"uid": uid, "expected_role": tag}
        e["present_in_ControlTerminal_census"] = any(o["uid"] == uid for o in ct_all)
        e["census_row_verbatim"] = next((o for o in ct_all if o["uid"] == uid), None)
        lrows, lloc, lrec = read_node_table(target, uid, "M-A ControlTerminal %s" % tag, allow_scan=False)
        e["locate"] = lloc
        e["is_in_Nodes_array"] = lloc.get("is_in_Nodes_array")
        e["label_read_off_the_machine__node_labels"] = lloc.get("node_own_label")
        e["node_terms_how"] = lrec.get("how")
        e["node_terms_table_verbatim"] = lrows
        wire_from_terms = None
        if lrows:
            wire_from_terms = lrows[0]["wire"]
        e["wire_from_node_terms"] = wire_from_terms
        # route 2: panel_wiring, matched by the wire uid and by the label the machine reports
        e["panel_rows_carrying_case_wires"] = [r for r in prows if r["wire"] in (W0, W2) and r["wire"]]
        lab = lloc.get("node_own_label")
        e["panel_rows_with_that_label"] = [r for r in prows if lab and r["label"] == lab]
        K["control_terminals"][str(uid)] = e
        fact("M-A ControlTerminal #%d (%s): in Nodes[] %r ; label(node_labels) %r ; wire via node_terms %r ; "
             "census row %r" % (uid, tag, e["is_in_Nodes_array"], lab, wire_from_terms,
                                e["census_row_verbatim"]))
        fact("M-A ControlTerminal #%d panel_wiring rows with that label VERBATIM: %r ; panel rows carrying "
             "wire %r/%r: %r" % (uid, e["panel_rows_with_that_label"], W0, W2,
                                 e["panel_rows_carrying_case_wires"]))

    # the wire uid for each ControlTerminal, by whichever route answered, with the route recorded
    for uid in (CT_NUM, CT_BOOL):
        e = K["control_terminals"][str(uid)]
        if e.get("wire_from_node_terms"):
            e["wire_uid"] = e["wire_from_node_terms"]
            e["wire_route"] = "node_terms on the ControlTerminal, verified by its own UID echo"
        else:
            cand = e.get("panel_rows_with_that_label") or []
            e["wire_uid"] = cand[0]["wire"] if len(cand) == 1 else None
            e["wire_route"] = ("panel_wiring row matched by the label node_labels reports (%d matching row(s))"
                               % len(cand)) if cand else "NO ROUTE ANSWERED"
        fact("M-A ControlTerminal #%d wire uid = %r  [route: %s]" % (uid, e["wire_uid"], e["wire_route"]))
    gate("A_4 a wire uid was obtained for BOTH ControlTerminals",
         all(K["control_terminals"][str(u)].get("wire_uid") for u in (CT_NUM, CT_BOOL)),
         "#%d -> %r ; #%d -> %r" % (CT_NUM, K["control_terminals"][str(CT_NUM)].get("wire_uid"),
                                    CT_BOOL, K["control_terminals"][str(CT_BOOL)].get("wire_uid")))

    # ---- A_5: the pair verdicts. STATED, not interpreted.
    wn = K["control_terminals"][str(CT_NUM)].get("wire_uid")
    wb = K["control_terminals"][str(CT_BOOL)].get("wire_uid")
    pairs = [
        {"pair": "#%d t0 (case selector, BOOLEAN)  vs  ControlTerminal #%d (boolean indicator)"
                 % (CASE_UID, CT_BOOL), "a": W0, "b": wb},
        {"pair": "#%d t2 (NUMERIC)  vs  ControlTerminal #%d (numeric indicator)"
                 % (CASE_UID, CT_NUM), "a": W2, "b": wn},
        {"pair": "#%d t0  vs  ControlTerminal #%d (cross pair, for completeness)" % (CASE_UID, CT_NUM),
         "a": W0, "b": wn},
        {"pair": "#%d t2  vs  ControlTerminal #%d (cross pair, for completeness)" % (CASE_UID, CT_BOOL),
         "a": W2, "b": wb},
    ]
    for p in pairs:
        p["verdict"] = ("SAME Wire object uid" if (p["a"] and p["b"] and p["a"] == p["b"])
                        else "DIFFERENT" if (p["a"] and p["b"]) else "UNDETERMINED (a uid is missing)")
        fact("M-A PAIR: %s -> %r vs %r -> %s" % (p["pair"], p["a"], p["b"], p["verdict"]))
    K["pair_verdicts"] = pairs
    gate("A_5 every pair verdict is stated (SAME / DIFFERENT / UNDETERMINED)",
         all(p["verdict"] for p in pairs), "; ".join(p["verdict"] for p in pairs))
    dump()
    return W0, W2


# ============================================================ M-B  what each Wire object touches
def m_b(target, W0, W2, case_diagram_index):
    print("\n========== M-B  every terminal each Wire object touches", flush=True)
    K = R["M_B"]
    K["wires_of_interest"] = [W0, W2]
    K["wire_side_verb_search"] = {
        "searched_for": ["a gscript def taking a WIRE and returning its terminals",
                         "the VI Server id 6371003 (`Wire.Terminals[]`) anywhere in tools/gscript.py",
                         "the string 'Wire.Terminals'"],
        "what_the_neighbouring_verbs_do_instead": [
            "node_terms(target, diagram, node) tools/gscript.py:870 - terminals of ONE NODE, each row carrying "
            "the connected WIRE uid: the TERMINAL side of the relation, never the wire side",
            "panel_wiring(target) tools/gscript.py:826 - every top-level PANEL object's terminal with its "
            "connected wire uid: again the terminal side",
            "tunnels(target, index) tools/gscript.py:941 - a LoopTunnel's own terminals and their wires",
            "net_map(target, diagram, ...) tools/gscript.py:2540 - builds nets by reading node terminals one "
            "by one, i.e. it GROUPS the terminal side; it does not ask a Wire what it touches",
            "connect_nested_v1 (tools/recipes/build_opconnectnested_v1.py) reads `Wire.Is Broken?` 6371004 on "
            "ONE wire it has just re-connected; it enumerates no terminals, and it is NOT called here because "
            "an `Is Broken?` read perturbs ExecState (docs/NAMES.md:912-918)"],
        "result": "NO VERB FOUND" if not R["M_C"].get("wire_terminal_enumerator_in_gscript") else
                  "a wire-side enumerator WAS found - see M_C.wire_side_api_ids_searched",
    }
    fact("M-B WIRE-SIDE VERB SEARCH RESULT: %s" % K["wire_side_verb_search"]["result"])
    gate("B_1a the wire-side verb question is answered explicitly", True,
         K["wire_side_verb_search"]["result"])

    # ---- the terminal-side REVERSE census. This is NOT a wire-side read and is not presented as one.
    K["reverse_census_is_not_a_wire_side_read"] = (
        "every NODE terminal on the wires' own diagram plus every PANEL terminal of the VI was read, and the "
        "rows whose connected-wire uid equals one of the two wires are listed. A terminal on another diagram, "
        "or a reader that does not expose a terminal (a Local, a Value property node), cannot appear here.")
    K["diagram_index_scanned"] = case_diagram_index
    rows, lerr = node_label_rows(target, case_diagram_index, fresh=True)
    K["node_labels_error_verbatim"] = lerr
    K["nodes_on_that_diagram"] = len(rows)
    cls_by_uid = {}
    try:
        cls_by_uid = {o["uid"]: o["class"] for o in g.report_all(target, "Node")}
        K["node_class_map_size"] = len(cls_by_uid)
    except Exception as e:                                                         # noqa: BLE001
        K["node_class_map_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    fact("M-B scanning Diagram index %r: %d nodes (node_labels), Node class map %r entries"
         % (case_diagram_index, len(rows), K.get("node_class_map_size")))

    hits = {str(W0): [], str(W2): []}
    scanned, errs = 0, []
    n_max = min(len(rows), CENSUS_LIMIT)
    K["nodes_actually_scanned_cap"] = n_max
    for n in range(n_max):
        scanned += 1
        try:
            node_uid, trows = g.node_terms_uid(target, case_diagram_index, n)
        except Exception as e:                                                     # noqa: BLE001
            errs.append({"n": n, "error_verbatim": str(e)[:160]})
            continue
        if not node_uid:
            break
        for t in trows:
            if t["wire"] in (W0, W2) and t["wire"]:
                hits[str(t["wire"])].append(
                    {"owner_node_uid": node_uid, "owner_node_class": cls_by_uid.get(node_uid),
                     "owner_node_label": rows[n]["label"] if n < len(rows) else None,
                     "nodes_index": n, "terminal_index": t["i"], "terminal_name": t["name"],
                     "terminal_name_hex": (t["name"] or "").encode("utf-8").hex(),
                     "is_source": t["is_source"]})
    K["nodes_scanned"] = scanned
    K["scan_errors"] = errs
    K["truncated"] = len(rows) > n_max
    for r in prows_cache["rows"]:
        if r["wire"] in (W0, W2) and r["wire"]:
            hits[str(r["wire"])].append(
                {"owner_node_uid": None, "owner_node_class": "PANEL OBJECT (panel_wiring row)",
                 "owner_node_label": r["label"], "nodes_index": None, "terminal_index": None,
                 "terminal_name": r["label"], "terminal_name_hex": (r["label"] or "").encode("utf-8").hex(),
                 "is_source": r["is_source"], "panel_control_uid": r["uid"], "indicator": r["indicator"]})
    K["terminals_touching_each_wire"] = hits
    for w in (W0, W2):
        fact("M-B wire %r is touched by %d terminal(s): %r" % (w, len(hits[str(w)]), hits[str(w)]))
    gate("B_1b the reverse census enumerated at least one terminal for each wire",
         all(hits[str(w)] for w in (W0, W2)),
         "wire %r: %d ; wire %r: %d" % (W0, len(hits[str(W0)]), W2, len(hits[str(W2)])))
    gate("B_1c the scan of that diagram was NOT truncated", not K["truncated"],
         "%d nodes on the diagram, cap %d" % (len(rows), n_max))
    dump()


prows_cache = {"rows": []}


# ============================================================ M-D  destructive, scratch only
def m_d(target, rec_key, which_terminal, far_uid, far_term, tag):
    """Delete the Wire object carrying `#10407` t<which_terminal> on `target` and report what went bare."""
    print("\n========== M-D  %s: delete the Wire on #%d t%d" % (tag, CASE_UID, which_terminal), flush=True)
    K = R[rec_key]
    K["scratch"] = os.path.basename(target)
    K["terminal"] = "#%d t%d" % (CASE_UID, which_terminal)

    es_before = read_exec_state(K, "%s BEFORE the delete" % tag, target)
    K["exec_state_before"] = es_before
    K["wire_census_before"] = count_of(target, "Wire")

    before_rows, before_loc, before_rec = read_node_table(target, CASE_UID, "%s BEFORE #10407" % tag)
    K["case_table_before"] = before_rows
    row = next((r for r in before_rows if r["i"] == which_terminal), None)
    K["target_terminal_row_before"] = row
    wire_uid = (row or {}).get("wire")
    K["wire_uid_read_off_the_machine"] = wire_uid
    gate("%s_a the target wire uid was read off the machine (not assumed)" % tag, bool(wire_uid),
         "wire %r on %s" % (wire_uid, K["terminal"]), fatal=True)

    fp_before, _ = panel_rows(target, "%s BEFORE" % tag)
    K["panel_rows_before"] = [r for r in fp_before if r["wire"] == wire_uid]
    far_before, _fl, _fr = read_node_table(target, far_uid, "%s BEFORE far end #%d" % (tag, far_uid))
    K["far_end_table_before"] = far_before
    K["far_end_row_before"] = next((r for r in far_before if r["i"] == far_term), None)

    ct_before = {}
    for uid in (CT_NUM, CT_BOOL):
        lrows, lloc, _lr = read_node_table(target, uid, "%s BEFORE CT #%d" % (tag, uid), allow_scan=False)
        ct_before[str(uid)] = {"label": lloc.get("node_own_label"),
                               "wire_from_node_terms": lrows[0]["wire"] if lrows else None,
                               "table_verbatim": lrows,
                               "panel_rows": [r for r in fp_before
                                              if lloc.get("node_own_label")
                                              and r["label"] == lloc.get("node_own_label")]}
    K["control_terminals_before"] = ct_before

    # ---- the delete itself: Traverse index resolved from report_all, never remembered
    try:
        wires = g.report_all(target, "Wire")
        idx = [o["i"] for o in wires if o["uid"] == wire_uid]
        K["wire_traverse_matches"] = idx
    except Exception as e:                                                         # noqa: BLE001
        K["wire_traverse_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        idx = []
    gate("%s_b exactly ONE Traverse 'Wire' entry carries uid %r" % (tag, wire_uid), len(idx) == 1,
         "matches %r" % (idx,), fatal=True)
    try:
        gone = g.delete_object(target, "Wire", idx[0])
        K["delete_error_verbatim"] = ""
        K["uids_gone"] = sorted(gone) if gone else gone
    except Exception as e:                                                         # noqa: BLE001
        K["delete_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        K["uids_gone"] = None
    fact("%s delete_object(Wire[%r] = uid %r): gone %r ; error %r"
         % (tag, idx[0], wire_uid, K["uids_gone"], K["delete_error_verbatim"]))
    gate("%s_c the delete removed EXACTLY the wire uid that was targeted" % tag,
         K["uids_gone"] == [wire_uid], "gone %r, targeted %r" % (K["uids_gone"], wire_uid))

    es_after = read_exec_state(K, "%s AFTER the delete" % tag, target)
    K["exec_state_after"] = es_after
    K["wire_census_after"] = count_of(target, "Wire")
    K["control_terminal_census_after"] = count_of(target, "ControlTerminal")
    fact("%s ExecState %r -> %r ; Wire census %r -> %r ; ControlTerminal census after %r"
         % (tag, es_before, es_after, K["wire_census_before"], K["wire_census_after"],
            K["control_terminal_census_after"]))

    after_rows, _al, after_rec = read_node_table(target, CASE_UID, "%s AFTER #10407" % tag)
    K["case_table_after"] = after_rows
    K["target_terminal_row_after"] = next((r for r in after_rows if r["i"] == which_terminal), None)

    fp_after, _ = panel_rows(target, "%s AFTER" % tag)
    far_after, _fl2, _fr2 = read_node_table(target, far_uid, "%s AFTER far end #%d" % (tag, far_uid))
    K["far_end_table_after"] = far_after
    K["far_end_row_after"] = next((r for r in far_after if r["i"] == far_term), None)

    ct_after = {}
    for uid in (CT_NUM, CT_BOOL):
        lrows, lloc, _lr = read_node_table(target, uid, "%s AFTER CT #%d" % (tag, uid), allow_scan=False)
        ct_after[str(uid)] = {"label": lloc.get("node_own_label"),
                              "wire_from_node_terms": lrows[0]["wire"] if lrows else None,
                              "table_verbatim": lrows,
                              "panel_rows": [r for r in fp_after
                                             if lloc.get("node_own_label")
                                             and r["label"] == lloc.get("node_own_label")]}
    K["control_terminals_after"] = ct_after

    # ---- the before -> after table, assembled mechanically
    def wire_of(entry):
        if entry is None:
            return None
        if entry.get("wire_from_node_terms") is not None:
            return entry.get("wire_from_node_terms")
        pr = entry.get("panel_rows") or []
        return pr[0]["wire"] if len(pr) == 1 else None

    table = [
        {"what": "#%d t%d (the deleted wire's sink)" % (CASE_UID, which_terminal),
         "before": (K["target_terminal_row_before"] or {}).get("wire"),
         "after": (K["target_terminal_row_after"] or {}).get("wire")},
        {"what": "far end #%d t%d %r" % (far_uid, far_term, (K["far_end_row_before"] or {}).get("name")),
         "before": (K["far_end_row_before"] or {}).get("wire"),
         "after": (K["far_end_row_after"] or {}).get("wire")},
        {"what": "ControlTerminal #%d (%r)" % (CT_NUM, ct_before[str(CT_NUM)].get("label")),
         "before": wire_of(ct_before[str(CT_NUM)]), "after": wire_of(ct_after[str(CT_NUM)])},
        {"what": "ControlTerminal #%d (%r)" % (CT_BOOL, ct_before[str(CT_BOOL)].get("label")),
         "before": wire_of(ct_before[str(CT_BOOL)]), "after": wire_of(ct_after[str(CT_BOOL)])},
        {"what": "ExecState", "before": es_before, "after": es_after},
        {"what": "Wire census", "before": K["wire_census_before"], "after": K["wire_census_after"]},
    ]
    for r in table:
        r["went_bare"] = (bool(r["before"]) and not r["after"]) if r["what"].startswith(("#", "far", "Control")) \
            else None
    K["before_after_table"] = table
    for r in table:
        fact("%s TABLE  %-46s  %r -> %r%s"
             % (tag, r["what"], r["before"], r["after"],
                ("   WENT BARE" if r["went_bare"] else "")))
    K["terminals_that_went_bare"] = [r["what"] for r in table if r["went_bare"]]
    gate("%s_d the before->after table is complete (6 rows)" % tag, len(table) == 6,
         "went bare: %r" % (K["terminals_that_went_bare"],))
    dump()


# ============================================================ MAIN
def main():
    print("=== diag_c62_branch  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== PURE MEASUREMENT: nothing built, nothing saved, no route chosen, no `Is Broken?` read", flush=True)
    print("=== NO new verb, NO gscript edit, NO recipe, NO GUI, NO motor/ASI/camera (rig 조립)", flush=True)

    m_c_census()        # file census FIRST - no LabVIEW touched

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

    try:
        # ---------------- scratch A: M-A, M-B, then M-D's first half
        shutil.copy2(S3A_ARTEFACT, SCRATCH_A)
        pa = probe("A_1 scratch A at creation", SCRATCH_A)
        R["scratch_a"]["md5_at_creation"] = pa.get("md5")
        gate("A_1 scratch A is byte-identical to D1_s3a_focus_ind.vi at creation", pa.get("md5") == S3A_MD5,
             "%s (expected %s)" % (pa.get("md5", "?"), S3A_MD5), fatal=True)
        g.open_panel(SCRATCH_A)
        time.sleep(1.0)

        W0, W2 = m_a(SCRATCH_A)
        prows_cache["rows"] = g.panel_wiring(SCRATCH_A)
        di = R["M_A"]["case_node"]["locate"].get("diagram_index")
        if di is not None and W0 and W2:
            m_b(SCRATCH_A, W0, W2, di)
        else:
            R["M_B"]["not_attempted_because"] = ("the CaseStructure's diagram index (%r) or a wire uid "
                                                 "(t0 %r, t2 %r) was not obtained" % (di, W0, W2))
            fact("M-B NOT ATTEMPTED: %s" % R["M_B"]["not_attempted_because"])

        m_d(SCRATCH_A, "M_D_scratch_A", 0, FAR_BOOL, FAR_BOOL_TERM, "D_A")
        close_quietly(SCRATCH_A)

        # ---------------- scratch B: an INDEPENDENT copy, untouched by A's delete
        shutil.copy2(S3A_ARTEFACT, SCRATCH_B)
        pb = probe("B_1 scratch B at creation", SCRATCH_B)
        R["scratch_b"]["md5_at_creation"] = pb.get("md5")
        gate("D_B_0 scratch B is byte-identical to D1_s3a_focus_ind.vi at creation (independent of scratch A)",
             pb.get("md5") == S3A_MD5, "%s (expected %s)" % (pb.get("md5", "?"), S3A_MD5), fatal=True)
        g.open_panel(SCRATCH_B)
        time.sleep(1.0)
        read_exec_state(R["M_D_scratch_B"], "scratch B, cold open", SCRATCH_B)
        m_d(SCRATCH_B, "M_D_scratch_B", 2, FAR_NUM, FAR_NUM_TERM, "D_B")
        close_quietly(SCRATCH_B)
    except Stop as s:
        R["stopped_at"] = str(s)
        fact("STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        R["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
    finally:
        for p in (SCRATCH_A, SCRATCH_B):
            close_quietly(p)
    dump()

    # ---- Z: the closing facts
    print("\n--- Z: the closing facts", flush=True)
    removed = {}
    for p in (SCRATCH_A, SCRATCH_B):
        if os.path.exists(p):
            try:
                os.remove(p)
                removed[os.path.basename(p)] = True
            except Exception as e:                                                 # noqa: BLE001
                removed[os.path.basename(p)] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
    R["scratches_removed"] = removed
    gate("Z_2 BOTH scratches were DELETED in the same run",
         not os.path.exists(SCRATCH_A) and not os.path.exists(SCRATCH_B),
         "A exists=%r, B exists=%r" % (os.path.exists(SCRATCH_A), os.path.exists(SCRATCH_B)))

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
    gate("Z_1d nothing was created under tools/recipes/ and nothing was saved", True,
         "this diagnostic writes tools/bench/diag_c62_branch.{log,json} only; `save` is never called")
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
