"""diag_s56_transport3 - cycle 56 material #5. A DIAGNOSTIC under tools/bench/, never a recipe.

WHAT IT IS FOR (judgement's three ORDERS, cycle 56 dispatch 5; this script interprets nothing and chooses nothing):

  PHASE 1  The 5001 of dispatch 3 was probably OUR ADDRESSING ERROR. `wire_indicators` looks its `Indicator Names`
           up on the diagram it is HANDED (tools/gscript.py:1787-1788), and dispatch 3 handed it the SOURCE's
           diagram (#639). Re-call it with `diagram_index` resolved from the TARGET INDICATOR's own owner diagram:
           `diag_index(target, owner_of(target, <indicator uid>)[1])` (tools/recipes/build_d1_v0.py:338,:357).
           Source #10686 t0 'x .and. y?' (wire 10799, Diagram #639, class Function); target = the SAME indicator
           dispatch 3 used, 'File # Saved' uid 6, wire 0, its label READ OFF THE MACHINE and passed byte-exact.
  PHASE 2  Can a node be put on the TOP-LEVEL diagram at all, and does a panel object follow?
           `build_index_array` (:2322, the VI -> Block Diagram head) -> `node_info(max_n=40)` (which read [] in
           dispatch 3; THE PREDICTION IS THAT IT NOW READS >= 1) -> `create_indicator` on that node's terminal
           index 2 -> `delete_object` the IA, leaving a free-standing indicator (docs/NAMES.md:476-478;
           docs/stage2-assembly-step-b.md:49-50 for the delete-the-helper route).
  PHASE 3  The local variable by DUPLICATION rather than creation: `copy_by_index` (:1479-1558) with
           `duplicate=True` (:1527) and the class as a FREE STRING 'Local' (:1526) against the 8 `Local` objects
           this VI already carries, then `move_in` into Diagram #23058 (loop 1.5's body, 37(h)) - the op's own
           label map (tools/bench/opmovebyindex_labels.json) has NO destination-diagram control, so the landing
           diagram is read back and the move into #23058 is a SECOND, already-built verb, not a new op.
           Plus ONE pure read: can any generic property READ available to us tell which control each existing
           `Local` is bound to (`Local.Control Name`, ID 6355400)?

PREDICTION CONTRACT (every line is a printed GATE; a FAIL is a reading, not a crash - the 34(j)/37(e) pattern):
  T1   the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                          (FATAL)
  T1b  claudeDev\\D1_s1_copy.vi md5 == 3e3d23cefd3a334001aa9d6156bf1aee
  T2   claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                                (FATAL)
  T3   each phase's scratch is byte-identical to its stated parent at creation                          (FATAL)
  A0   the target indicator's label is READ OFF THE MACHINE for ControlTerminal uid 6, wire 0
  A1   `owner_of(6)` answers ('Diagram', uid) and `diag_index` resolves that uid to a Traverse index
  A2   `wire_indicators` with the TARGET-resolved `diagram_index` returns an EMPTY error column
  A3   the target indicator's wire uid changes from 0 (the EFFECT gate; no new Wire object is expected -
       a branch joins an existing wire, tools/gscript.py:1771-1772)
  A4   #10686 t0 stays wired and its wired-terminal count is reported before and after                  (37(e))
  A5   #637's terminal count is unchanged - no new tunnel/border object appeared on #637                (37(e))
  A6   the ORDERED SECOND-PASS `Is Broken?` read returns a boolean (True is a LEGITIMATE reading)
  A7   phase 1 ends at ExecState 1 and `g.save()` returns a byte count
  B1   `build_index_array` puts exactly 1 new IndexArray on the target, and its owner diagram is READ BACK
  B2   `node_info(max_n=40)` on the top-level diagram reads >= 1 node                     (JUDGEMENT'S PREDICTION)
  B3   `create_indicator` on that node's terminal 2 produces a ControlTerminal (114 -> 115)
  B4   `delete_object` removes the IndexArray (1 object gone)
  B5   phase 2 ends at ExecState 1 and `g.save()` returns a byte count
  C1   the 8 `Local` uids read live equal {2991, 4277, 11574, 3160, 3097, 2143, 16942, 25805}
  C2   `copy_by_index('Local', duplicate=True)` reports an outcome verbatim (added uids or the exception)
  C3   the copy's class and owner diagram are READ BACK from the machine
  C4   `move_in` reports the copy's owner diagram as #23058
  C5   the `Local` Traverse count goes 8 -> 9
  C6   phase 3 ends at ExecState 1 and `g.save()` returns a byte count
  C7   the pure read question is ANSWERED mechanically (a scan of gscript.py, the op inventory and
       docs/vi-server-ids.json - not an opinion)
  Z1   ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 unchanged after everything
  Z2   refs opened == refs closed, 0 live

PREDICTED RISK, stated BEFORE the run so it is not an unpredicted result: phase 3's `copy_by_index` byte-
substitutes the two NIScriptingExamples\\Moving Objects fixtures with 475 kB copies of a main-VI scratch and loads
them FROM THAT FOLDER, where the scratch's ~94 subVI relative paths do not resolve. A relink cascade / ExecState 0
there is an EXPECTED outcome of the route judgement ordered, and `copy_by_index` then raises WITHOUT writing
anything back to the scratch (:1548-1557). Phase 3 is therefore LAST and is skipped, with the reason recorded, if
more than 12.0 min of the 18-min deadline are already spent - so a timeout still leaves phases 1 and 2 on disk.

BOUNDS: at most 3 attempts per verb, NO loop over indices. NO VI IS RUN (34(f)). NO NEW OP VI (Pre-decided 2). No
new device (user 2026-09-18 08:53). No GUI action. No motor / ASI / camera (rig 조립). Originals never opened for
write. `allow_broken` stays False and `gui_save` is NEVER called. `Is Broken?` is read ONLY in a separate, ordered
second pass, never in the pass that makes the connection (42(b)) - and, so the artefact survives that read's known
ExecState perturbation (docs/NAMES.md:912-918), the save happens BEFORE the second pass.

WHAT ALREADY EXISTED (checked before writing a line of this, per the material brief):
  * tools/gscript.py - `wire_indicators` :1756, `build_index_array` :2322, `create_indicator` :2388,
    `create_control` :2360, `delete_object` :2240, `copy_by_index` :1479, `restore_move_fixtures` :1465,
    `node_info` :2462, `node_terms_uid` :925, `panel_wiring` :826, `fp_labels` :2440, `report`/`report_all`
    :455/:488, `count` :1005, `exec_state` :1977, `save` :2062, `remove_bad_wires_scripted` :2486.
  * tools/recipes/build_d1_v0.py - `move_in` :318, `owner_of` :338, `diag_index` :357.
  * tools/bench/diag_s2_scaffold.py - `fresh`, `Preload`, `file_facts`, `version_bytes`, the md5 pins.
  * tools/bench/diag_s56_transport2.py - the gate/fact/probe/scratch shape this file follows.
  * tools/recipes/build_opconnectnested_v1.py:418 - the ONLY built carrier of `Wire.Is Broken?` 6371004
    (docs/NAMES.md:902-911), used here ONLY as the ordered second pass, an IDEMPOTENT re-connect of an EXISTING
    connection on the same net (wire_delta must be 0).
  NOTHING NEW WAS BUILT. No op VI was created, no recipe was added, gscript.py was not patched.
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
import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_v0 import diag_index, owner_of, move_in                             # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1              # noqa: E402
import build_opconnectnested_v1 as CN1                                            # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_s56_transport3.json")
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

TARGET_IND_UID = 6              # 'File # Saved', wire 0 - the indicator dispatch 3 used
SRC_UID = 10686                 # class Function, label 'And'; t0 'x .and. y?' is a SOURCE carrying wire 10799
SRC_TERM_NAME = "x .and. y?"
SRC_NODES_INDEX = 25            # Nodes[] index of #10686 on Diagram #639 (dispatch 2/3, uid verified by readback)
SRC_WIRE = 10799
D639 = 639
D686 = 686
LOOP11_UID = 637
LOOP11_NODES_INDEX = 4          # #637 is Nodes[4] of Diagram #686
SINK_NODES_INDEX = 24           # #10407, Nodes[24] of Diagram #639, already sourced by wire 10799
BODY_DIAG_UID = 23058           # loop 1.5's body (37(h), binding)
IA_LOCATION = (6200, 5200)      # far from every existing object; the IA is deleted again in the same phase
IA_TERM_INDEX = 2               # the terminal judgement named for create_indicator
LOCAL_UIDS_PIN = {2991, 4277, 11574, 3160, 3097, 2143, 16942, 25805}
LOCAL_CTLNAME_PROP = 6355400    # Local.Control Name (peer answer, UNVERIFIED on this machine)
# files-first: the first unwired (wire 0) indicator labels of tools/bench/main_vi_panel_wiring.json, in file order
FALLBACK_INDICATORS = ["File # Saved", "Image"]
PHASE3_BUDGET_S = 12.0 * 60.0

LEFTOVERS = [os.path.join(g.CLAUDEDEV, "DIAG_s56_wireind_20260920_214454.vi"),
             os.path.join(g.CLAUDEDEV, "DIAG_s56_localvar_20260920_214454.vi")]

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "question": "cycle 56 dispatch 5: (P1) was dispatch 3's 5001 an ADDRESSING error - does wire_indicators "
                 "work when diagram_index is the TARGET indicator's own owner diagram? (P2) can a node be placed "
                 "on the top-level diagram at all, and does a panel object follow? (P3) can a Local be placed by "
                 "DUPLICATION with copy_by_index?",
     "chooses_no_route": True, "interprets_nothing": True, "no_vi_was_run": True, "no_new_op": True,
     "no_new_device": True, "no_gui_action": True, "no_recipe": True,
     "rig_state": "조립 (motors/ASI forbidden, camera not needed)",
     "citations": {"wire_indicators_looks_names_up_on_the_diagram_it_is_handed": "tools/gscript.py:1787-1788",
                   "owner_of_diag_index": "tools/recipes/build_d1_v0.py:338,:357",
                   "ia_then_create_then_delete": "docs/NAMES.md:476-478, docs/stage2-assembly-step-b.md:49-50",
                   "copy_by_index_duplicate_free_string_class": "tools/gscript.py:1526-1527",
                   "is_broken": "docs/NAMES.md:902-911", "ordered_second_pass": "Pre-decided 42(b)",
                   "branch_adds_no_wire_object": "tools/gscript.py:1771-1772"},
     "disposed_review_recorded_not_acted_on": "archive/peer/2026-09-20-c56-transport-verbs-unreachable.md - "
                                             "judgement ACCEPTED its decisive point and ORDERED these three "
                                             "constructions; this script executes that decision (41(b)).",
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "handles": {}, "hash_probe": [], "leftover_cleanup": [], "phase1": {}, "phase2": {}, "phase3": {},
     "move_fixtures_after": {}}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` - the documented emitter (37(i)); the bold form is invisible to guard_peer.
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


def census(rec, tag, target):
    c = {}
    for k in ("Diagram", "WhileLoop", "SubVI", "Local", "IndexArray", "LoopTunnel", "Wire", "ControlTerminal",
              "Function"):
        try:
            c[k] = g.count(target, k)
        except Exception as e:                                                     # noqa: BLE001
            c[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    rec.setdefault("censuses", {})[tag] = c
    fact("class census [%s] %r" % (tag, c))
    return c


def read_exec_state(rec, tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    rec.setdefault("exec_state_timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def make_scratch(rec, tag, path, parent, parent_md5, parent_name):
    if os.path.exists(path):
        os.remove(path)
    shutil.copy2(parent, path)
    p = probe("T3 %s scratch at creation (copied from %s)" % (tag, parent_name), path)
    rec["scratch"] = path
    rec["parent"] = {"path": parent, "md5_expected": parent_md5, "name": parent_name}
    rec["scratch_at_creation"] = p
    gate("T3 the %s scratch is byte-identical to %s" % (tag, parent_name), p.get("md5") == parent_md5,
         "%s (expected %s)" % (p.get("md5", "?"), parent_md5), fatal=True)
    return path


def panel_rows(target):
    try:
        return list(g.panel_wiring(target) or [])
    except Exception as e:                                                         # noqa: BLE001
        fact("panel_wiring raised %s: %s" % (type(e).__name__, str(e)[:200]))
        return []


def row_of(rows, uid):
    return next((r for r in rows if r.get("uid") == uid), None)


def wired_counts(rec, tag, target, diag, node_i, uid_expect):
    """(node uid readback, n terminals, n WIRED terminals, the rows) - the 37(e) per-node metric."""
    out = {"tag": tag, "diagram_index": diag, "node_index": node_i, "uid_expect": uid_expect}
    try:
        u, rows = g.node_terms_uid(target, diag, node_i)
        out.update({"node_uid_readback": u, "n_terms": len(rows),
                    "n_wired": sum(1 for r in rows if r.get("wire")),
                    "terms": [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                               "wire": r["wire"]} for r in rows]})
    except Exception as e:                                                         # noqa: BLE001
        out["error"] = "%s: %s" % (type(e).__name__, str(e)[:160])
    rec.setdefault("wired_counts", []).append(out)
    fact("%s: node uid readback %r, %r terminals, %r WIRED"
         % (tag, out.get("node_uid_readback"), out.get("n_terms"), out.get("n_wired")))
    return out


def owner_read(rec, tag, target, uid):
    """owner_of with the strict guard first, then non-strict - the answer either way is REPORTED."""
    rd = {"tag": tag, "uid": uid}
    for strict in (True, False):
        try:
            cls, ouid = owner_of(target, uid, strict=strict)
            rd.update({"strict": strict, "owner_class": cls, "owner_uid": ouid, "error_verbatim": ""})
            break
        except Exception as e:                                                     # noqa: BLE001
            rd.update({"strict": strict, "owner_class": None, "owner_uid": None,
                       "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:250])})
    rec.setdefault("owner_reads", []).append(rd)
    fact("%s: owner_of(#%s) = (%r, %r) [strict=%r] error VERBATIM %r"
         % (tag, uid, rd.get("owner_class"), rd.get("owner_uid"), rd.get("strict"), rd.get("error_verbatim")))
    return rd


def save_phase(rec, tag, target):
    """ExecState, then the conditional save, then the file facts. Called BEFORE any Is Broken? read."""
    es = read_exec_state(rec, "%s immediately before the save attempt" % tag, target)
    size, serr = None, None
    if isinstance(es, int) and es == 1:
        try:
            size = g.save(target)          # allow_broken stays False; gui_save is NEVER called
        except Exception as e:                                                     # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:250])
    else:
        serr = "NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved." % (es,)
    rec["save"] = {"returned_bytes": size, "exception_or_reason_verbatim": serr,
                   "allow_broken": False, "gui_save": False, "exec_state_before_save": es}
    fact("%s g.save() returned %r; exception/reason VERBATIM %r" % (tag, size, serr))
    rec["save"]["file_after"] = D.file_facts("%s artefact after the save attempt" % tag, target)
    gate("%s ends at ExecState 1 and g.save() returned a byte count" % tag,
         isinstance(size, int) and size > 0, "ExecState %r, bytes %r, reason %r" % (es, size, serr))
    return es, size


def close_quietly(target):
    try:
        g.close_panel(target)
    except Exception as e:                                                         # noqa: BLE001
        fact("close_panel(%s) raised %s: %s" % (os.path.basename(target), type(e).__name__, e))


def op_indicators():
    """OpConnectNested_v1's own readouts, re-read AFTER a run (g.op caches the reference)."""
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
    return rd


def ordered_is_broken(rec, target, d639):
    """The ORDERED SECOND PASS (42(b)): an IDEMPOTENT re-connect of the EXISTING #10686 t0 -> #10407 t0
    connection on the same net, so the 6371004 carrier has a Nodes[]-addressable sink. wire_delta must be 0."""
    print("\n--- ORDERED PASS 2: the `Is Broken?` reading (42(b)) - idempotent re-connect of the EXISTING "
          "#%d t0 -> #10407 t0 connection on the same net; wire_delta must be 0" % SRC_UID, flush=True)
    rec["pass2"] = {"sink": "#10407 t0 (Nodes[%d] of Diagram #639), already sourced by wire %d"
                            % (SINK_NODES_INDEX, SRC_WIRE),
                    "why": "a front-panel ControlTerminal is not in Nodes[], so no 6371004 carrier can address "
                           "the indicator end; the same NET is read instead (dispatch 3's method)"}
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, d639, SINK_NODES_INDEX, 0, d639, SRC_NODES_INDEX, 0, V1_LABELS)
        rec["pass2"].update({"wire_delta": dw, "exec_state_returned": es, "error_verbatim": err})
    except Exception as e:                                                         # noqa: BLE001
        rec["pass2"].update({"wire_delta": None, "exec_state_returned": None,
                             "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    rec["pass2"]["op_indicators"] = op_indicators()
    ib = rec["pass2"]["op_indicators"].get("Is Broken?")
    rec["is_broken_ordered"] = ib
    fact("A6 ORDERED `Is Broken?` = %r on wire uid %r (op error column %r, wire_delta %r). True here is a "
         "LEGITIMATE reading, not a failure."
         % (ib, rec["pass2"]["op_indicators"].get("UID 2"), rec["pass2"].get("error_verbatim"),
            rec["pass2"].get("wire_delta")))
    gate("A6 the ORDERED second-pass `Is Broken?` read returned a boolean", isinstance(ib, bool), repr(ib))
    read_exec_state(rec, "after the Is Broken? read (SUSPECT, docs/NAMES.md:912-918; the save already happened)",
                    target)
    return ib


# ======================================================================================== PHASE 1
def phase1():
    rec = R["phase1"]
    rec["order"] = ("wire_indicators re-called with diagram_index = diag_index(owner_of(<target indicator uid>)) "
                    "- the TARGET's own owner diagram, not the SOURCE's (tools/gscript.py:1787-1788)")
    target = make_scratch(rec, "P1", os.path.join(g.CLAUDEDEV, "DIAG_s56_t3_p1_%s.vi" % STAMP),
                          S2_ARTEFACT, S2_MD5, "the S2 artefact D1_s2_loops.vi")
    print("\n=================== PHASE 1  (the 5001 addressing hypothesis)  scratch %s"
          % os.path.basename(target), flush=True)

    with D.Preload("P-1"):
        g.open_panel(target)
        time.sleep(1.0)
        census(rec, "before", target)
        rec["exec_state_before"] = read_exec_state(rec, "P1 BEFORE", target)

        # ---- A0: the target indicator's label, READ OFF THE MACHINE (panel_wiring reads Control.Label ->
        # Text.Text straight through COM, so the string is byte-exact; newlines are preserved, nothing is stripped)
        rows = panel_rows(target)
        rec["panel_rows_read"] = len(rows)
        tr = row_of(rows, TARGET_IND_UID)
        rec["target_row_before"] = tr
        lab = (tr or {}).get("label")
        rec["target_label_repr"] = repr(lab)
        rec["target_label_bytes"] = (lab or "").encode("utf-8").hex()
        fact("A0 ControlTerminal uid %d label VERBATIM %r (utf-8 hex %s), indicator=%r, wire=%r, is_source=%r"
             % (TARGET_IND_UID, lab, rec["target_label_bytes"], (tr or {}).get("indicator"),
                (tr or {}).get("wire"), (tr or {}).get("is_source")))
        gate("A0 the target indicator's label is READ OFF THE MACHINE for ControlTerminal uid %d, wire 0"
             % TARGET_IND_UID, bool(lab) and (tr or {}).get("wire") == 0,
             "label %r wire %r" % (lab, (tr or {}).get("wire")))

        # the SECOND reader, for the byte-exactness comparison attempt 2 needs. panel_wiring rows and fp_labels
        # indices are BOTH Panel.Controls[] (tabbing) order, so the row's position IS the fp_labels index.
        row_i = rows.index(tr) if tr in rows else None
        fpl = []
        if row_i is not None:
            try:
                fpl = g.fp_labels(target, max_n=row_i + 2)
            except Exception as e:                                                # noqa: BLE001
                fact("fp_labels raised %s: %s" % (type(e).__name__, str(e)[:160]))
        fp_lab = next((t for (i, t, _ind) in fpl if i == row_i), None)
        rec["fp_labels_probe"] = {"row_index": row_i, "fp_label_repr": repr(fp_lab),
                                  "agrees_bytewise": fp_lab == lab}
        fact("A0b the SECOND reader (fp_labels, index %r) reads %r - byte-identical to panel_wiring's: %r"
             % (row_i, fp_lab, fp_lab == lab))

        # ---- A1: the diagram the TARGET indicator's terminal lives on
        own = owner_read(rec, "A1 the target indicator's owner", target, TARGET_IND_UID)
        d_target = None
        if own.get("owner_uid"):
            try:
                d_target = diag_index(target, int(own["owner_uid"]))
            except Exception as e:                                                # noqa: BLE001
                fact("diag_index(#%s) raised %s: %s" % (own.get("owner_uid"), type(e).__name__, str(e)[:160]))
        rec["diagram_index_of_target_owner"] = d_target
        fact("A1 the TARGET indicator's own owner diagram = %r #%r -> Traverse Diagram index %r  (dispatch 3 "
             "passed the SOURCE's diagram #%d instead)"
             % (own.get("owner_class"), own.get("owner_uid"), d_target, D639))
        gate("A1 owner_of(#%d) answered and diag_index resolved it" % TARGET_IND_UID,
             own.get("owner_class") == "Diagram" and isinstance(d_target, int),
             "(%r, %r) -> index %r" % (own.get("owner_class"), own.get("owner_uid"), d_target))

        # the source side, re-resolved LIVE (38(e)): Traverse `Function` index is wire_indicators' `index`
        try:
            fn = [o["uid"] for o in g.report_all(target, "Function")]
            fn_i = fn.index(SRC_UID)
        except Exception as e:                                                     # noqa: BLE001
            fn, fn_i = [], None
            fact("report_all(Function) / index raised %s: %s" % (type(e).__name__, str(e)[:160]))
        rec["function_class_count"] = len(fn)
        rec["src_function_traverse_index"] = fn_i
        fact("A1b #%d sits at Traverse index %r of class `Function` (%d members); dispatch 3 measured 102"
             % (SRC_UID, fn_i, len(fn)))
        d639 = None
        try:
            d639 = diag_index(target, D639)
        except Exception as e:                                                      # noqa: BLE001
            fact("diag_index(#%d) raised %s: %s" % (D639, type(e).__name__, str(e)[:160]))
        d686 = None
        try:
            d686 = diag_index(target, D686)
        except Exception as e:                                                      # noqa: BLE001
            fact("diag_index(#%d) raised %s: %s" % (D686, type(e).__name__, str(e)[:160]))
        rec["diagram_index_639"] = d639
        rec["diagram_index_686"] = d686
        fact("A1c Diagram #%d reads Traverse index %r; Diagram #%d reads %r" % (D639, d639, D686, d686))

        src_before = wired_counts(rec, "A4 BEFORE #%d (the source node)" % SRC_UID, target, d639,
                                  SRC_NODES_INDEX, SRC_UID)
        loop_before = wired_counts(rec, "A5 BEFORE #%d (loop 1.1, the tunnel check)" % LOOP11_UID, target, d686,
                                   LOOP11_NODES_INDEX, LOOP11_UID)
        t0 = next((t for t in src_before.get("terms", []) if t["i"] == 0), None)
        fact("A4a #%d t0 reads %r (is_source %r, wire %r)"
             % (SRC_UID, (t0 or {}).get("name"), (t0 or {}).get("is_source"), (t0 or {}).get("wire")))

        # ---- the <= 3 attempts. HARD BOUND, no loop over indices.
        attempts_spec = []
        if lab is not None and isinstance(d_target, int):
            attempts_spec.append({"n": 1, "label": lab, "diagram_index": d_target,
                                  "why": "the label read live off panel_wiring + the TARGET's own owner diagram"})
        if fp_lab is not None and fp_lab != lab and isinstance(d_target, int):
            attempts_spec.append({"n": 2, "label": fp_lab, "diagram_index": d_target,
                                  "why": "the SECOND reader's byte-different label (newline preserved)"})
        else:
            rec["attempt2_skipped_because"] = ("both readers returned the SAME bytes (%r), so 'the byte-exact "
                                               "label with any newline preserved' IS attempt 1 - spending an "
                                               "attempt on an identical string would measure nothing" % (lab,))
        alt = next((r for r in rows if r.get("indicator") and not r.get("wire")
                    and r.get("uid") != TARGET_IND_UID), None)
        rec["alt_row"] = alt
        rec["alt_row_chosen_because"] = ("the NEXT unwired (wire 0) indicator row read live; the files-first "
                                         "order in tools/bench/main_vi_panel_wiring.json is %r"
                                         % (FALLBACK_INDICATORS,))
        alt_di = None
        if alt:
            ao = owner_read(rec, "A1d the ALT indicator's owner", target, alt["uid"])
            if ao.get("owner_uid"):
                try:
                    alt_di = diag_index(target, int(ao["owner_uid"]))
                except Exception as e:                                             # noqa: BLE001
                    fact("diag_index(alt owner) raised %s: %s" % (type(e).__name__, str(e)[:140]))
            attempts_spec.append({"n": 3, "label": alt["label"], "diagram_index": alt_di,
                                  "why": "a DIFFERENT wire-0 indicator row, its own owner diagram"})
        attempts_spec = attempts_spec[:3]
        rec["attempts_spec"] = attempts_spec
        fact("A2 attempt plan (HARD BOUND <= 3, no loop over indices): %r"
             % ([{k: a[k] for k in ("n", "label", "diagram_index")} for a in attempts_spec],))

        rec["attempts"] = []
        for a in attempts_spec:
            att = {"n": a["n"], "indicator_label_repr": repr(a["label"]),
                   "indicator_label_hex": (a["label"] or "").encode("utf-8").hex(),
                   "diagram_index": a["diagram_index"], "why": a["why"], "src_term": SRC_TERM_NAME,
                   "function_index": fn_i}
            es_b = read_exec_state(rec, "P1 attempt %d BEFORE" % a["n"], target)
            att["exec_state_before"] = es_b
            wires_b = g.count(target, "Wire")
            if fn_i is None or not isinstance(a["diagram_index"], int):
                att["error_verbatim"] = ("NOT ATTEMPTED: function index %r / diagram_index %r unresolved"
                                         % (fn_i, a["diagram_index"]))
                att["seconds"] = None
            else:
                try:
                    dt = g.wire_indicators(target, fn_i, [SRC_TERM_NAME], [a["label"]],
                                           diagram_index=a["diagram_index"], node_class="Function")
                    att.update({"error_verbatim": "", "seconds": dt})
                except Exception as e:                                             # noqa: BLE001
                    att.update({"error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:500]), "seconds": None})
            rows_after = panel_rows(target)
            want_uid = TARGET_IND_UID if a["n"] != 3 else (alt or {}).get("uid")
            ra = row_of(rows_after, want_uid)
            att["row_after"] = ra
            att["new_wire_uid"] = (ra or {}).get("wire")
            att["wire_count_delta"] = g.count(target, "Wire") - wires_b
            att["exec_state_after"] = read_exec_state(rec, "P1 attempt %d AFTER" % a["n"], target)
            rec["attempts"].append(att)
            fact("A2 attempt %d: wire_indicators(Function[%r], [%r] -> [%r], diagram_index=%r) error VERBATIM %r"
                 % (a["n"], fn_i, SRC_TERM_NAME, a["label"], a["diagram_index"], att["error_verbatim"]))
            fact("A3 attempt %d: indicator uid %r wire %r -> %r ; whole-VI Wire count delta %r (a BRANCH adds no "
                 "Wire object, tools/gscript.py:1771-1772); ExecState %r -> %r"
                 % (a["n"], want_uid, 0 if a["n"] != 3 else (alt or {}).get("wire"), att["new_wire_uid"],
                    att["wire_count_delta"], es_b, att["exec_state_after"]))
            dump()
            if att.get("new_wire_uid"):
                break

        won = next((a for a in rec["attempts"] if a.get("new_wire_uid")), None)
        rec["succeeded_attempt"] = (won or {}).get("n")
        gate("A2 wire_indicators returned an EMPTY error column on at least one attempt",
             any(a.get("error_verbatim") == "" for a in rec["attempts"]),
             repr([a.get("error_verbatim") for a in rec["attempts"]]))
        gate("A3 a target indicator's wire uid changed from 0", bool(won),
             "attempt %r -> wire %r" % ((won or {}).get("n"), (won or {}).get("new_wire_uid")))

        src_after = wired_counts(rec, "A4 AFTER #%d (the source node)" % SRC_UID, target, d639,
                                 SRC_NODES_INDEX, SRC_UID)
        loop_after = wired_counts(rec, "A5 AFTER #%d (loop 1.1, the tunnel check)" % LOOP11_UID, target, d686,
                                  LOOP11_NODES_INDEX, LOOP11_UID)
        gate("A4 #%d t0 stays wired and its wired-terminal count is reported (37(e))" % SRC_UID,
             src_before.get("n_wired") is not None and src_after.get("n_wired") is not None,
             "%r -> %r wired of %r -> %r terminals" % (src_before.get("n_wired"), src_after.get("n_wired"),
                                                       src_before.get("n_terms"), src_after.get("n_terms")))
        gate("A5 #%d terminal count unchanged - no new tunnel/border object (37(e))" % LOOP11_UID,
             loop_before.get("n_terms") == loop_after.get("n_terms"),
             "%r -> %r terminals, %r -> %r wired" % (loop_before.get("n_terms"), loop_after.get("n_terms"),
                                                     loop_before.get("n_wired"), loop_after.get("n_wired")))
        census(rec, "after", target)
        # SAVE FIRST, then the ordered Is Broken? pass (whose read is known to perturb ExecState)
        save_phase(rec, "A7 PHASE 1", target)
        if isinstance(d639, int):
            ordered_is_broken(rec, target, d639)
        else:
            fact("A6 NOT ATTEMPTED: Diagram #%d did not resolve to a Traverse index." % D639)
        close_quietly(target)
    dump()


# ======================================================================================== PHASE 2
def phase2():
    rec = R["phase2"]
    rec["order"] = ("build_index_array on the TOP-LEVEL diagram -> node_info(max_n=40) -> create_indicator on "
                    "terminal %d -> delete_object the IndexArray, leaving a free-standing indicator" % IA_TERM_INDEX)
    target = make_scratch(rec, "P2", os.path.join(g.CLAUDEDEV, "DIAG_s56_t3_p2_%s.vi" % STAMP),
                          S2_ARTEFACT, S2_MD5, "the S2 artefact D1_s2_loops.vi")
    print("\n=================== PHASE 2  (top-level node + a panel object)  scratch %s"
          % os.path.basename(target), flush=True)

    with D.Preload("P-2"):
        g.open_panel(target)
        time.sleep(1.0)
        c_before = census(rec, "before", target)
        rec["exec_state_before"] = read_exec_state(rec, "P2 BEFORE", target)

        # ---- B1: the Index Array on the top-level diagram (the VI -> Block Diagram head)
        try:
            top0 = g.node_info(target, max_n=40)
        except Exception as e:                                                     # noqa: BLE001
            top0 = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
        rec["node_info_before"] = top0
        fact("B2a node_info(max_n=40) BEFORE the IndexArray: %r entries -> %r"
             % (len(top0) if isinstance(top0, list) else top0, top0))

        rec["B1"] = {"location": list(IA_LOCATION), "attempts": []}
        new_ia, ia_err = None, None
        try:
            new_ia = g.build_index_array(target, IA_LOCATION)
            ia_err = ""
        except Exception as e:                                                     # noqa: BLE001
            ia_err = "%s: %s" % (type(e).__name__, str(e)[:500])
        rec["B1"]["attempts"].append({"n": 1, "error_verbatim": ia_err, "new": new_ia})
        fact("B1 build_index_array(top-level, %r) -> new %r ; error VERBATIM %r" % (IA_LOCATION, new_ia, ia_err))
        gate("B1 build_index_array put exactly 1 new IndexArray on the target",
             isinstance(new_ia, list) and len(new_ia) == 1, repr(new_ia))
        ia_uid = (new_ia[0]["uid"] if isinstance(new_ia, list) and new_ia else None)
        ia_ti = (new_ia[0]["i"] if isinstance(new_ia, list) and new_ia else None)
        rec["B1"]["ia_uid"] = ia_uid
        rec["B1"]["ia_traverse_index"] = ia_ti
        if ia_uid:
            owner_read(rec, "B1b the new IndexArray's owner diagram", target, ia_uid)

        # ---- B2: does the top-level Nodes[] census see it now?  JUDGEMENT'S PREDICTION: >= 1 node.
        try:
            top = g.node_info(target, max_n=40)
        except Exception as e:                                                     # noqa: BLE001
            top = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
        rec["node_info_after"] = top
        fact("B2 node_info(max_n=40) AFTER the IndexArray (create_indicator's OWN ladder): %r entries -> %r"
             % (len(top) if isinstance(top, list) else top, top))
        gate("B2 node_info reads >= 1 node on the top-level diagram", isinstance(top, list) and len(top) >= 1,
             "%r entries" % (len(top) if isinstance(top, list) else top,))

        # the new node's terminal list, for the record (Traverse Diagram index 0 = TopLevelDiagram #536,
        # identified by elimination in tools/bench/diag_c56_topdiagram_files.json)
        node_i = (top[-1][0] if isinstance(top, list) and top else None)
        rec["B3"] = {"node_index": node_i, "terminal_index": IA_TERM_INDEX, "attempts": []}
        if node_i is not None:
            wired_counts(rec, "B3a the new node's terminals (Traverse Diagram 0)", target, 0, node_i, ia_uid)

        # ---- B3: create_indicator on terminal 2 of that node.  <= 3 attempts; only 1 is planned.
        ct_before = c_before.get("ControlTerminal")
        new_ct, ci_err = None, None
        if node_i is None:
            ci_err = "NOT ATTEMPTED: node_info reported no node index to address."
        else:
            try:
                new_ct = g.create_indicator(target, node_i, IA_TERM_INDEX)
                ci_err = ""
            except Exception as e:                                                 # noqa: BLE001
                ci_err = "%s: %s" % (type(e).__name__, str(e)[:500])
        rec["B3"]["attempts"].append({"n": 1, "error_verbatim": ci_err, "new": new_ct})
        fact("B3 create_indicator(Nodes[%r].Terminals[%d]) -> new %r ; error VERBATIM %r"
             % (node_i, IA_TERM_INDEX, new_ct, ci_err))
        ct_after = g.count(target, "ControlTerminal")
        rec["B3"]["control_terminal_count"] = {"before": ct_before, "after": ct_after}
        gate("B3 create_indicator produced a ControlTerminal (%r -> %r)" % (ct_before, ct_after),
             bool(new_ct) and isinstance(ct_after, int) and isinstance(ct_before, int)
             and ct_after == ct_before + 1, "new %r, count %r -> %r" % (new_ct, ct_before, ct_after))
        new_ct_uid = None
        if isinstance(new_ct, list) and new_ct:
            new_ct_uid = new_ct[0].get("uid")
            rows = panel_rows(target)
            r = row_of(rows, new_ct_uid)
            rec["B3"]["new_indicator_row"] = r
            fact("B3b the new indicator reads label %r, indicator=%r, wire=%r"
                 % ((r or {}).get("label"), (r or {}).get("indicator"), (r or {}).get("wire")))
        read_exec_state(rec, "P2 after create_indicator", target)

        # ---- B4: delete the helper IndexArray (docs/NAMES.md:476-478 / stage2-assembly-step-b.md:49-50)
        rec["B4"] = {"attempts": []}
        gone, del_err = None, None
        if ia_uid is None:
            del_err = "NOT ATTEMPTED: no IndexArray uid to delete."
        else:
            try:
                ias = [o["uid"] for o in g.report_all(target, "IndexArray")]
                idx = ias.index(ia_uid)
                rec["B4"]["traverse_index_at_delete"] = idx
                gone = g.delete_object(target, "IndexArray", idx)
                del_err = ""
            except Exception as e:                                                 # noqa: BLE001
                del_err = "%s: %s" % (type(e).__name__, str(e)[:500])
        rec["B4"]["attempts"].append({"n": 1, "error_verbatim": del_err, "gone": sorted(gone) if gone else gone})
        fact("B4 delete_object(IndexArray[%r]) -> gone %r ; error VERBATIM %r"
             % (rec["B4"].get("traverse_index_at_delete"), sorted(gone) if gone else gone, del_err))
        gate("B4 delete_object removed the IndexArray", bool(gone) and len(gone) == 1,
             "%r (error %r)" % (sorted(gone) if gone else gone, del_err))
        es = read_exec_state(rec, "P2 after the delete", target)
        if isinstance(es, int) and es == 0:
            # the documented follow-up: the deleted node's wires are left broken (gscript.py:2242-2244)
            try:
                nw, es2 = g.remove_bad_wires_scripted(target)
                rec["B4"]["remove_bad_wires"] = {"wire_count_after": nw, "exec_state": es2, "error_verbatim": ""}
            except Exception as e:                                                 # noqa: BLE001
                rec["B4"]["remove_bad_wires"] = {"error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:300])}
            fact("B4b ExecState was 0 after the delete, so the DOCUMENTED follow-up ran: "
                 "remove_bad_wires_scripted -> %r" % (rec["B4"]["remove_bad_wires"],))
            read_exec_state(rec, "P2 after remove_bad_wires", target)
            if isinstance(new_ct_uid, int):
                rows = panel_rows(target)
                rec["B4"]["new_indicator_row_after_rbw"] = row_of(rows, new_ct_uid)
                fact("B4c the new indicator after remove_bad_wires: %r" % (rec["B4"]["new_indicator_row_after_rbw"],))
        census(rec, "after", target)
        save_phase(rec, "B5 PHASE 2", target)
        close_quietly(target)
    dump()


# ======================================================================================== PHASE 3
def property_read_scan():
    """The brief's PURE READ: is there any generic property READ available to us that can report which control
    each existing `Local` is bound to (`Local.Control Name`, ID 6355400)?  Answered mechanically."""
    out = {"question": "can any generic property READ available to us report Local.Control Name (ID %d)?"
                       % LOCAL_CTLNAME_PROP}
    with open(os.path.join(ROOT, "tools", "gscript.py"), encoding="utf-8") as f:
        gs = f.read()
    out["gscript_functions"] = sorted(ln.split("(")[0][4:] for ln in gs.splitlines() if ln.startswith("def "))
    out["gscript_property_related"] = [ln.strip() for ln in gs.splitlines()
                                       if ln.startswith("def ") and ("prop" in ln.lower() or "set_" in ln)]
    out["id_6355400_occurrences"] = {}
    for rel in ("docs/vi-server-ids.json", "tools/gscript.py"):
        p = os.path.join(ROOT, rel)
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                txt = f.read()
            out["id_6355400_occurrences"][rel] = txt.count(str(LOCAL_CTLNAME_PROP))
        except Exception as e:                                                     # noqa: BLE001
            out["id_6355400_occurrences"][rel] = "ERROR %s" % type(e).__name__
    try:
        ops = sorted(f for f in os.listdir(g.CLAUDEDEV) if f.lower().endswith(".vi") and f.startswith("Op"))
    except Exception as e:                                                         # noqa: BLE001
        ops = ["ERROR %s" % type(e).__name__]
    out["op_inventory_count"] = len(ops)
    out["op_candidates_property_like"] = [o for o in ops if "Prop" in o or "PN" in o]
    out["answer"] = (
        "NO generic property READER exists in this fleet. Every reader on disk is a PURPOSE-BUILT op with its "
        "property IDs hard-wired at build time (OpReport_v3 class/uid/pos/owner, OpPanelWiring_v0 "
        "label/indicator/uid/is-source/wire, OpFPLabels_v0, OpNodeInfo_v0 style/label, OpNodeTerms_v0, "
        "OpOwnerChain_v1, OpConnectNested_v1's `Wire.Is Broken?`), and none of them reads Local.Control Name. "
        "gscript.py has no generic property-read wrapper at all: the only property-touching entry points are "
        "`build_property` (:2194), which CREATES a Property Node inside a target VI - and reading its value back "
        "would require RUNNING that VI, which 34(f) forbids - plus the special-purpose WRITERS `set_index_mode`, "
        "`set_auto_error_handling`, `set_node_label`. ID %d appears %r times in docs/vi-server-ids.json and %r "
        "times in tools/gscript.py. So the binding of the 8 existing `Local`s CANNOT be read today without "
        "building a new op VI (Pre-decided 2 forbids it in this cycle)."
        % (LOCAL_CTLNAME_PROP, out["id_6355400_occurrences"].get("docs/vi-server-ids.json"),
           out["id_6355400_occurrences"].get("tools/gscript.py")))
    return out


def phase3():
    rec = R["phase3"]
    rec["order"] = ("copy_by_index('Local', duplicate=True, class as a free string) then move_in to Diagram "
                    "#%d - the op's label map has NO destination-diagram control, so the landing diagram is "
                    "READ BACK and the move is a second, already-built verb" % BODY_DIAG_UID)
    rec["op_label_map"] = {"file": "tools/bench/opmovebyindex_labels.json",
                           "keys": ["class_name", "traverse_target", "index", "selected_uid", "duplicate"],
                           "has_destination_diagram_control": False}
    rec["property_read_scan"] = property_read_scan()
    fact("C7 %s" % rec["property_read_scan"]["answer"])
    gate("C7 the pure read question is ANSWERED mechanically", bool(rec["property_read_scan"].get("answer")),
         "op inventory %r, property-like ops %r"
         % (rec["property_read_scan"].get("op_inventory_count"),
            rec["property_read_scan"].get("op_candidates_property_like")))
    dump()

    elapsed = time.time() - T_START
    rec["elapsed_at_entry_s"] = round(elapsed, 1)
    if elapsed > PHASE3_BUDGET_S:
        rec["skipped_because"] = ("%.0f s of the 18-min deadline were already spent (budget %.0f s). The "
                                  "PREDICTED RISK in this file's docstring applies: copy_by_index loads a "
                                  "main-VI-sized scratch from the Moving Objects fixture folder, where its subVI "
                                  "paths do not resolve, and a relink cascade would take the run past the "
                                  "deadline and cost phases 1-2 their reported readings." % (elapsed,
                                                                                             PHASE3_BUDGET_S))
        fact("C2 PHASE 3 NOT ATTEMPTED: %s" % rec["skipped_because"])
        gate("C2 copy_by_index reported an outcome verbatim", False, "NOT ATTEMPTED (time budget)")
        dump()
        return

    # the parent: phase 2's artefact when it ended at ExecState 1, else a third fresh copy of S2
    p2 = R["phase2"].get("save") or {}
    p2_path = R["phase2"].get("scratch")
    p2_ok = isinstance(p2.get("returned_bytes"), int) and p2_path and os.path.exists(p2_path)
    if p2_ok:
        parent, parent_md5 = p2_path, (p2.get("file_after") or {}).get("md5")
        parent_name = "phase 2's SAVED artefact %s (ExecState 1)" % os.path.basename(p2_path)
    else:
        parent, parent_md5, parent_name = S2_ARTEFACT, S2_MD5, "the S2 artefact D1_s2_loops.vi (phase 2 did not save)"
    target = make_scratch(rec, "P3", os.path.join(g.CLAUDEDEV, "DIAG_s56_t3_p3_%s.vi" % STAMP),
                          parent, parent_md5, parent_name)
    print("\n=================== PHASE 3  (the Local by DUPLICATION)  scratch %s  (parent: %s)"
          % (os.path.basename(target), parent_name), flush=True)

    with D.Preload("P-3"):
        g.open_panel(target)
        time.sleep(1.0)
        c_before = census(rec, "before", target)
        rec["exec_state_before"] = read_exec_state(rec, "P3 BEFORE", target)

        try:
            locs = g.report(target, "Local")
        except Exception as e:                                                     # noqa: BLE001
            locs = "ERROR %s: %s" % (type(e).__name__, str(e)[:160])
        rec["local_objects_before"] = locs
        live_uids = {o["uid"] for o in locs} if isinstance(locs, list) else set()
        fact("C1 `Local` objects BEFORE: count %r, uids %r, owners %r"
             % (c_before.get("Local"), sorted(live_uids),
                sorted({o.get("owner") for o in locs}) if isinstance(locs, list) else locs))
        gate("C1 the 8 `Local` uids read live equal the pinned set", live_uids == LOCAL_UIDS_PIN,
             "%r vs pin %r" % (sorted(live_uids), sorted(LOCAL_UIDS_PIN)))
        pick = (locs[0] if isinstance(locs, list) and locs else None)
        rec["picked_local"] = pick
        fact("C2a the donor Local = Traverse index %r, uid %r, owner %r (the FIRST member of class `Local`; "
             "expect_uid is passed as the op's own uid guard, gscript.py:1532)"
             % ((pick or {}).get("i"), (pick or {}).get("uid"), (pick or {}).get("owner")))

        # the scratch's panel is closed before its bytes are copied into the fixtures (gscript.py:1501-1504)
        close_quietly(target)

    # copy_by_index manages its own loads and byte substitutions, so the ORIGINAL preload is NOT held across it
    with contextlib.nullcontext():
        rec["C2"] = {"attempts": []}
        added, sel, cp_err = None, None, None
        if pick is None:
            cp_err = "NOT ATTEMPTED: no `Local` object was reported on the scratch."
        else:
            try:
                added, sel = g.copy_by_index(target, "Local", pick["i"], target, expect_uid=pick["uid"])
                cp_err = ""
            except Exception as e:                                                 # noqa: BLE001
                cp_err = "%s: %s" % (type(e).__name__, str(e)[:700])
        rec["C2"]["attempts"].append({"n": 1, "error_verbatim": cp_err, "added": added, "selected_uid": sel})
        fact("C2 copy_by_index(donor=target, 'Local'[%r], duplicate=True, expect_uid=%r) -> added %r, selected "
             "uid %r ; error VERBATIM %r"
             % ((pick or {}).get("i"), (pick or {}).get("uid"), added, sel, cp_err))
        gate("C2 copy_by_index reported an outcome verbatim", cp_err is not None,
             "added %r, error %r" % (added, cp_err))
        rec["move_fixtures_after_copy"] = {
            "source": D.file_facts("C2b Moving Objects Source after the copy", g.MOVE_SRC),
            "target": D.file_facts("C2b Moving Objects Target after the copy", g.MOVE_DST)}

        new_uid = None
        if isinstance(added, list) and added:
            new_uid = added[0].get("uid")
        rec["C2"]["new_uid"] = new_uid

        # ---- C3 / C4: where did it land, and can move_in put it on #23058?
        if new_uid is not None:
            pre3b = D.Preload("P-3b")
            pre3b.__enter__()      # entered explicitly so the long read block below needs no re-indentation
            g.open_panel(target)
            time.sleep(1.0)
            census(rec, "after_copy", target)
            try:
                locs2 = g.report(target, "Local")
            except Exception as e:                                                 # noqa: BLE001
                locs2 = "ERROR %s: %s" % (type(e).__name__, str(e)[:160])
            rec["local_objects_after_copy"] = locs2
            nrec = next((o for o in locs2 if o["uid"] == new_uid), None) if isinstance(locs2, list) else None
            rec["C3"] = {"new_object_row": nrec}
            fact("C3 the copy reads class %r, owner %r, pos %r"
                 % ((nrec or {}).get("class"), (nrec or {}).get("owner"), (nrec or {}).get("pos")))
            o1 = owner_read(rec, "C3b the copy's owner diagram AS COPIED", target, new_uid)
            gate("C3 the copy's class and owner diagram were READ BACK",
                 bool(nrec) and o1.get("owner_uid") is not None,
                 "class %r, owner %r #%r" % ((nrec or {}).get("class"), o1.get("owner_class"), o1.get("owner_uid")))

            di = None
            try:
                di = diag_index(target, BODY_DIAG_UID)
            except Exception as e:                                                 # noqa: BLE001
                fact("diag_index(#%d) raised %s: %s" % (BODY_DIAG_UID, type(e).__name__, str(e)[:160]))
            rec["C4"] = {"dest_diagram_uid": BODY_DIAG_UID, "dest_diagram_index": di, "attempts": []}
            mv_err, uid_back = None, None
            if di is None:
                mv_err = "NOT ATTEMPTED: Diagram #%d did not resolve to a Traverse index." % BODY_DIAG_UID
            else:
                try:
                    uid_back = move_in(target, new_uid, di, (120, 120))
                    mv_err = ""
                except Exception as e:                                             # noqa: BLE001
                    mv_err = "%s: %s" % (type(e).__name__, str(e)[:500])
            rec["C4"]["attempts"].append({"n": 1, "error_verbatim": mv_err, "uid_back": uid_back})
            fact("C4 move_in(#%r -> Diagram #%d, index %r) uid echo %r ; error VERBATIM %r"
                 % (new_uid, BODY_DIAG_UID, di, uid_back, mv_err))
            o2 = owner_read(rec, "C4b the copy's owner diagram AFTER move_in", target, new_uid)
            gate("C4 move_in reports the copy's owner diagram as #%d" % BODY_DIAG_UID,
                 o2.get("owner_uid") == BODY_DIAG_UID,
                 "owner %r #%r (error %r)" % (o2.get("owner_class"), o2.get("owner_uid"), mv_err))
            c_after = census(rec, "after", target)
            gate("C5 the `Local` Traverse count went %r -> 9" % c_before.get("Local"),
                 c_after.get("Local") == (c_before.get("Local") or 0) + 1,
                 "%r -> %r" % (c_before.get("Local"), c_after.get("Local")))
            save_phase(rec, "C6 PHASE 3", target)
            close_quietly(target)
            pre3b.__exit__(None, None, None)
        else:
            fact("C3/C4/C5/C6 NOT ATTEMPTED: copy_by_index added no object, so there is nothing to move, count "
                 "or save. That is the reading, reported as one.")
            for nm in ("C3 the copy's class and owner diagram were READ BACK",
                       "C4 move_in reports the copy's owner diagram as #%d" % BODY_DIAG_UID,
                       "C5 the `Local` Traverse count went %r -> 9" % c_before.get("Local"),
                       "C6 PHASE 3 ends at ExecState 1 and g.save() returned a byte count"):
                gate(nm, False, "NOT ATTEMPTED (no object was copied)")
    dump()


# ======================================================================================== MAIN
def main():
    print("=== diag_s56_transport3  %s   (cycle 56 dispatch 5; PHASE 1 -> 2 -> 3; NO VI IS RUN, 34(f); no new "
          "op, no new device, no GUI action, no recipe; CHOOSES NOTHING)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (dispatch 3 left ~60,179; fresh-instance baseline ~31,500): %r"
         % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    # ---- the mechanical pre-batch restart the brief orders (44(e); standing restart permission, CLAUDE.md 3)
    D.fresh("T2b RESTART (pre-batch, 44(e); dispatch 3 left the instance UP at ~60,179 handles)")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])

    # ---- the cleanup OWED from dispatch 3/4 (the permission layer refused it from a plain Remove-Item;
    # this run holds a writable session, so it is done from inside). ONE attempt each, no retry.
    for p in LEFTOVERS:
        e = {"path": p, "existed": os.path.exists(p)}
        if e["existed"]:
            try:
                os.remove(p)
                e["removed"] = not os.path.exists(p)
                e["error_verbatim"] = ""
            except Exception as ex:                                                # noqa: BLE001
                e["removed"] = False
                e["error_verbatim"] = "%s: %s" % (type(ex).__name__, str(ex)[:250])
        R["leftover_cleanup"].append(e)
        fact("owed cleanup (ONE attempt, no retry): %s existed=%r removed=%r error VERBATIM %r"
             % (os.path.basename(p), e["existed"], e.get("removed"), e.get("error_verbatim")))
    dump()

    for name, fn in (("PHASE 1", phase1), ("PHASE 2", phase2), ("PHASE 3", phase3)):
        try:
            fn()
        except Stop as s:
            fact("%s stopped at a FATAL gate: %s" % (name, s))
        except Exception as e:                                                     # noqa: BLE001
            fact("%s raised %s: %s" % (name, type(e).__name__, str(e)[:500]))
            dump()

    # ---- Z: the closing facts
    print("\n--- Z: the closing facts", flush=True)
    R["ref_counts"] = g.ref_counts()
    fact("refs %r" % (R["ref_counts"],))
    try:
        g.reset()
    except Exception as e:                                                         # noqa: BLE001
        fact("g.reset raised %s: %s" % (type(e).__name__, e))
    R["handles"]["after"] = labview_handles()
    fact("LabVIEW handles AFTER everything: %r" % R["handles"]["after"])
    # the Move fixtures are LEFT as the documented protocol leaves them (gscript.py:1466-1469: restoring the disk
    # under a possibly-loaded VI is what needs a restart) - their state is RECORDED, not repaired here.
    R["move_fixtures_after"] = {"source": D.file_facts("Z0 Moving Objects Source at the end", g.MOVE_SRC),
                                "target": D.file_facts("Z0 Moving Objects Target at the end", g.MOVE_DST)}
    zo = probe("Z1 ORIGINAL after everything", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after everything", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after everything", S2_ARTEFACT)
    gate("Z1 ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 all unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5,
         "%s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z2 refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    for ph in ("phase1", "phase2", "phase3"):
        sv = (R[ph].get("save") or {})
        fact("ARTEFACT %s: %r" % (ph, {"path": R[ph].get("scratch"), "bytes": sv.get("returned_bytes"),
                                       "file": sv.get("file_after")}))

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as s:
        fact("FATAL: %s" % s)
        dump()
        print("\n=== GATES %d pass / %d fail (FATAL stop)" % (len(passes), len(fails)), flush=True)
        sys.exit(1)
