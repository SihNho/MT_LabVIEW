"""diag_s57_typepair - cycle 57 material #4, the cycle's LAST build act. A DIAGNOSTIC under tools/bench/,
never a recipe. tools/recipes/stage_d1_s3a_focus_ind.py is NOT written and NOT launched here (it is
stop-recorded by archive/peer/2026-09-20-priorart-d1-s3a-focus-ind.md and guard_cycle refuses a recipe build
this cycle); its on-disk presence is REPORTED only.

TWO INDEPENDENT THINGS ARE MEASURED (the brief's words; this script interprets nothing and chooses nothing):

 (1) A SAVED ARTEFACT AT THE POINT WHERE THE VI IS LEGAL. Dispatch 3 (tools/bench/diag_s57_ctmove_wire.log)
     held ExecState 1 immediately after the `move_in` and spent it on the wire, so a run in which every
     transport verb returned an EMPTY error column left NO FILE. This run fixes the ORDER, not the verbs:
     phase E saves BEFORE any wiring is attempted, and that artefact is never deleted, whatever happens later.

 (2) A CONTROL PAIR ON ONE VARIABLE - the 42(a) design. Dispatch 3's leg wired a NUMERIC indicator (created
     from IndexArray.Terminals[2], label read back as 'index') to a BOOLEAN source (#10686 t0 'x .and. y?',
     wire 10799). This leg changes EXACTLY ONE THING: the source is NUMERIC - #10757 t1 'element' (wire 10990),
     the payload source named in docs/cycle27-plan.md 45(c). Same verb, same destination diagram (#639), same
     move_in, same branch-onto-an-existing-net shape.

PHASES (each is measured and reported; nothing is decided from any of them):
  A  Resolve LIVE, assume nothing (34(h)): diag_index(#639), diag_index(#536); owner_of(#10757), owner_of(#10686);
     #10757's OWN object class and its Traverse index WITHIN that class; and #10757's full (i, name, is_source,
     wire) terminal list, naming which terminal is 'element' and what wire it carries.
  B  Create ONE indicator by the 46(a) route: build_index_array on the `VI -> Block Diagram` head -> owner_of ==
     ('TopLevelDiagram', 536) -> node_info before/after -> create_indicator(Nodes[0].Terminals[2]) -> census
     114 -> ? -> delete_object(IndexArray[0]) -> ExecState. Any junk uid the delete releases is purged exactly as
     dispatch 3 did (the set is `after - before`, so nothing pre-existing can be touched).
  C  READ the new indicator's label OFF THE MACHINE (panel_wiring / fp_labels diff), verbatim + utf-8 hex; state
     whether it holds a newline and whether it duplicates an existing panel label. owner_of(new uid).
  D  move_in(new uid, dest_diagram_index = the LIVE index of #639): error column, owner_of before/after,
     ControlTerminal census, panel row count, ExecState before/after.
  E  SAVE HERE, BEFORE ANY WIRING. ExecState == 1 => g.save() -> claudeDev\\D1_s3a_ind_placed_<stamp>.vi (md5,
     bytes, LV version bytes). THE RUN'S PRIMARY DELIVERABLE, NEVER DELETED. ExecState != 1 => no save, say so,
     stop the run there.
  F  Reopen that saved file COLD - LabVIEW is RESTARTED (standing authority, CLAUDE.md 3; 44(e)) so the file is
     loaded from disk into a fresh instance with NOTHING preloaded, not read out of the in-memory target. Report
     ExecState on that cold open, owner_of(new uid), and every index re-resolved live on it.
  G  Wire it: wire_indicators(node_index = the LIVE Traverse index of #10757 within the class phase A measured,
     src_terms = [the terminal name phase A read], indicator_names = [the label phase C read, re-read off this
     file], diagram_index = the LIVE index of #639, node_class = the class phase A measured). Reported: the error
     column VERBATIM, the indicator terminal's wire uid before and after, the whole-VI Wire count delta,
     #10757's terminal/wired counts before and after, #637's terminal/wired counts before and after with an
     explicit tunnel/border statement, ExecState before and after.
  H  Save again IFF legal: ExecState == 1 => claudeDev\\D1_s3a_num_ind_<stamp>.vi. ExecState 0 => no save, said
     plainly; phase E's artefact still stands.
  I  ORDERED SECOND PASS (42(b)), AFTER the phase-H save attempt: `Wire.Is Broken?` read by an IDEMPOTENT
     re-connect on the SAME net (wire_delta expected 0), never in the pass that made the connection.
  J  One extra reading, files-or-machine: does ANY reader in the fleet return a TERMINAL's or a CONTROL's DATA
     TYPE (representation / class of the wire)? Report the verb and file:line, or state plainly that none does.
     NOTHING IS BUILT for it.

HOW THE TWO ARTEFACT NAMES ARE OBTAINED (mechanical, no save-as exists): `gscript.save` (:2062) persists a VI to
ITS OWN PATH - there is no save-as verb in the fleet - so the phase A..E scratch IS the phase-E artefact path,
and phase G runs on a byte-identical COPY of it under the phase-H name. Phase E's file is therefore never
overwritten by phase H, and the staged rule ("the next stage starts FROM THAT FILE, in a fresh LabVIEW instance
when the stage uses VI Scripting", CLAUDE.md, user 2026-09-19) is satisfied literally.

PREDICTION CONTRACT (every line below is a printed GATE and every gate is the readback of a CALL to the machine,
46(g); the phase-J search is a FACT, not a gate, because it reads files):
  T1   the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                          (FATAL)
  T1b  claudeDev\\D1_s1_copy.vi md5 == 3e3d23cefd3a334001aa9d6156bf1aee
  T2   claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                                (FATAL)
  T3   the scratch is byte-identical to D1_s2_loops.vi at creation                                      (FATAL)
  A1   diag_index(#639) resolves to an int                                                    (FATAL: no dest)
  A2   diag_index(#536) resolves to 0
  A3   owner_of(#10757) answers ('Diagram', 639)
  A4   owner_of(#10686) answers ('Diagram', 639)
  A5   #10757 is found in at least one live Traverse class list, with an index in it
  A6   #10757 carries a terminal named 'element' that is a SOURCE, and its wire uid is reported
  B1   build_index_array puts exactly 1 new IndexArray on the target, owner ('TopLevelDiagram', 536)
  B2   node_info(max_n=40) goes 0 entries -> 1 entry
  B3   create_indicator(Nodes[0].Terminals[2]) returns a ControlTerminal and the census goes 114 -> 115
  B4   delete_object(IndexArray[0]) removes exactly 1 object
  B5   ExecState after the delete == 1
  C1   exactly ONE new front-panel row appeared and its label was READ off the machine (never retyped)
  C2   the new label is UNIQUE among the target's panel labels                       (a duplicate is a READING)
  C3   owner_of(new ControlTerminal uid) answers
  D1   move_in returned without raising
  D2   owner_of(new uid) reads ('Diagram', 639) AFTER the move                                (the EFFECT gate)
  D3   the ControlTerminal census is unchanged across the move
  D4   the panel row count is unchanged across the move
  D5   ExecState after the move (and the junk purge) == 1
  E1   ExecState == 1 at the save point and g.save() returned a byte count      (a 0 here STOPS the run, and is
                                                                                 a LEGITIMATE outcome)
  E2   the phase-E artefact is on disk and its version bytes read 26 00 80 00 (LV2026)
  F1   the COLD reopen (fresh LabVIEW, nothing preloaded) reads ExecState 1
  F2   owner_of(new uid) on the COLD open reads ('Diagram', 639)
  G1   wire_indicators returned an EMPTY error column
  G2   the indicator's wire uid changed from 0                                                (the EFFECT gate)
  G3   #10757's wired-terminal count is unchanged across the wiring                                    (37(e))
  G4   #637's terminal count is unchanged - NO tunnel or border object appeared                        (37(e))
  H1   ExecState == 1 at the second save point and g.save() returned a byte count   (a 0 is a LEGITIMATE STOP;
                                                                                     phase E's file still stands)
  I1   the ORDERED second-pass `Is Broken?` read returned a boolean             (True is a LEGITIMATE reading)
  Z1   ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 unchanged after everything
  Z2   refs opened == refs closed, 0 live

STOP DISCIPLINE: a phase whose own precondition is unmet STOPS the run at that phase, records why, and goes
straight to the closing facts. No phase is retried; no verb is looped over indices (<= 1 attempt per verb).

PREDICTED RISKS, written down BEFORE the run so neither is an unpredicted result:
  (i)   `move_in` leaves JUNK `Invoke` node(s) on the target (measured twice: probe_move_ctlterm_v0.log:135 and
        dispatch 3, which recorded ONE junk Invoke reusing the uid the deleted IndexArray had just released).
        They are unwired residue of OUR OWN op and can hold ExecState at 0, which would make phase E's save
        illegal. They are RECORDED and then purged as tools/recipes/build_d1_routeb_v0.py:1279-1287 does.
  (ii)  Nodes[] and Traverse indices SHIFT when an object is added to or removed from a diagram (34(h)). Every
        index is re-resolved by uid readback immediately before use - including after the phase-F reload - and
        the historical pins (43 / 46 / 102 / 25 / 24 / 4) are only a first guess that must survive a uid echo.
  (iii) `wire_indicators` RAISES when the target reads ExecState != 1 after the connection (gscript.py:1794-1797)
        even though the connection was made. The exception text is captured VERBATIM and the run continues to
        phases H and I, exactly as dispatch 3 did.

BOUNDS: <= 1 attempt per verb, NO loop over indices. NO VI IS RUN (34(f)). NO NEW OP VI. No new process device
(user 2026-09-18 08:53). No GUI action. No motor / ASI / camera (rig 조립). Originals never opened for write.
`allow_broken` stays False and `gui_save` is NEVER called. `Is Broken?` is read ONLY in a separate, ordered
second pass and only AFTER the phase-H save attempt (docs/NAMES.md:912-918). NOTHING SAVED IS EVER DELETED.

WHAT ALREADY EXISTED (checked before writing a line of this, per the material brief):
  * tools/recipes/stage_d1_s3a_focus_ind.py - checked on disk; reported, never written, never launched.
  * tools/bench/diag_s57_ctmove_wire.py - dispatch 3's file; this run follows its gate/fact/probe/scratch shape
    and reuses its helpers' pattern verbatim rather than inventing new ones.
  * tools/gscript.py - build_index_array :2322, create_indicator :2388, delete_object :2240, node_info :2462,
    node_terms_uid :925, panel_wiring :826, fp_labels :2440, report_all :488, uids :1017, count :1005,
    wire_indicators :1756, exec_state :1977, save :2062, ensure_loaded :1268, open_panel/close_panel :1241/:1257.
  * tools/recipes/build_d1_v0.py - move_in :318, owner_of :338, diag_index :357.
  * tools/bench/diag_s2_scaffold.py - fresh/Preload/file_facts/version_bytes/md5 and the md5 pins.
  * tools/recipes/build_opconnectnested_v1.py:418 - the ONLY built carrier of `Wire.Is Broken?` 6371004
    (docs/NAMES.md:902-911), used here ONLY as the ordered second pass.
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
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index, owner_of, move_in                              # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
import build_opconnectnested_v1 as CN1                                             # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_s57_typepair.json")
PLACED = os.path.join(g.CLAUDEDEV, "D1_s3a_ind_placed_%s.vi" % STAMP)     # phases A..E; the PRIMARY deliverable
NUMIND = os.path.join(g.CLAUDEDEV, "D1_s3a_num_ind_%s.vi" % STAMP)        # phases G..I, a byte copy of PLACED
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

D639 = 639                      # the frame-loop BODY diagram (nested); owner WhileLoop #637
D536 = 536                      # the TopLevelDiagram (46(b); dispatch 3 re-measured diag_index -> 0)
D686 = 686                      # the FlatSequenceFrame diagram that owns #637
LOOP11_UID = 637                # While loop 1.1 - the 37(e) tunnel/border witness
LOOP11_NODES_PIN = 4            # historical Nodes[] index of #637 on Diagram #686 - never trusted without an echo
SRC_UID = 10757                 # THE ONE CHANGE from dispatch 3: the NUMERIC payload source (45(c))
SRC_TERM_NAME = "element"       # the terminal name 45(c) names; phase A must READ it back before it is used
SRC_WIRE_PIN = 10990            # the wire 45(c) records on that terminal - a PIN, re-measured in phase A
SRC_NODES_PIN = None            # no historical Nodes[] index for #10757 on #639 - a bounded scan resolves it
BOOL_SRC_UID = 10686            # dispatch 3's BOOLEAN source; read here only for the owner comparison (phase A)
IA_LOCATION = (6200, 5200)      # far from every existing object; the IA is deleted again in the same phase
IA_TERM_INDEX = 2               # the terminal 46(a) names for create_indicator
MOVE_POSITION = (120, 4000)     # a position INSIDE Diagram #639; overlap is cosmetic, never functional
SCAN_LIMIT = 80                 # the bounded Nodes[] scan used when a pinned index fails its uid echo
CLASS_CANDIDATES = ("IndexArray", "Function", "SubVI", "Property", "Invoke", "CaseStructure", "WhileLoop",
                    "ForLoop", "Sequence", "EventStructure", "Constant", "LoopTunnel", "ControlTerminal",
                    "Bundle", "Unbundle", "ArraySubset")

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "question": "cycle 57 dispatch 4: (1) does the S3a transport leave a SAVED artefact when the save is taken "
                 "BEFORE any wiring, and (2) does the same transport, with the source changed from the BOOLEAN "
                 "#10686 t0 to the NUMERIC #10757 t1 'element' and nothing else changed, wire without breaking?",
     "chooses_no_route": True, "interprets_nothing": True, "no_vi_was_run": True, "no_new_op": True,
     "no_new_device": True, "no_gui_action": True, "no_recipe": True, "edits_no_plan_document": True,
     "rig_state": "조립 (motors/ASI forbidden, camera not needed)",
     "recipe_file_reported_not_touched": {
         "path": "tools/recipes/stage_d1_s3a_focus_ind.py",
         "exists": os.path.exists(os.path.join(ROOT, "tools", "recipes", "stage_d1_s3a_focus_ind.py")),
         "mtime": None,
         "note": "stop-recorded by archive/peer/2026-09-20-priorart-d1-s3a-focus-ind.md; guard_cycle refuses a "
                 "recipe build this cycle. REPORTED ONLY - not written, not launched."},
     "citations": {"create_route": "Pre-decided 46(a); docs/NAMES.md:476-478; "
                                   "tools/bench/diag_s56_transport3.log:68-80",
                   "dispatch3": "tools/bench/diag_s57_ctmove_wire.log (move_in TOP-LEVEL -> NESTED at ExecState 1; "
                                "wire_indicators made the connection with no 5001; Is Broken? True on the "
                                "ordered second pass)",
                   "numeric_payload_source": "docs/cycle27-plan.md 45(c) (#10757 t1 'element', wire 10990)",
                   "move_in_owner_of_diag_index": "tools/recipes/build_d1_v0.py:318,:338,:357",
                   "junk_invoke_purge": "tools/recipes/build_d1_routeb_v0.py:1279-1287",
                   "is_broken": "docs/NAMES.md:902-911", "ordered_second_pass": "Pre-decided 42(b)",
                   "index_shift_after_mutation": "34(h); cycles 54/56/57",
                   "branch_adds_no_wire_object": "tools/gscript.py:1771-1772",
                   "wire_indicators_raises_on_break": "tools/gscript.py:1794-1797",
                   "no_save_as_verb": "tools/gscript.py:2062 (save persists to the target's OWN path)",
                   "staged_artefacts": "CLAUDE.md 'Big or blocked work is SPLIT into steps that each SAVE an "
                                       "intermediate artefact' (user, 2026-09-19)",
                   "gate_must_make_a_call": "Pre-decided 46(g)"},
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "artefact_placed": PLACED, "artefact_numind": NUMIND,
     "handles": {}, "hash_probe": [], "phaseA": {}, "phaseB": {}, "phaseC": {}, "phaseD": {}, "phaseE": {},
     "phaseF": {}, "phaseG": {}, "phaseH": {}, "phaseI": {}, "phaseJ": {}, "stopped_at": None}

try:
    _rp = os.path.join(ROOT, "tools", "recipes", "stage_d1_s3a_focus_ind.py")
    if os.path.exists(_rp):
        R["recipe_file_reported_not_touched"]["mtime"] = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(_rp)))
except Exception as _e:                                                            # noqa: BLE001
    R["recipe_file_reported_not_touched"]["mtime"] = "ERROR %s" % type(_e).__name__


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
    for k in ("Diagram", "WhileLoop", "SubVI", "Invoke", "IndexArray", "LoopTunnel", "Wire", "ControlTerminal",
              "Function"):
        try:
            c[k] = g.count(target, k)
        except Exception as e:                                                     # noqa: BLE001
            c[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    rec.setdefault("censuses", {})[tag] = c
    fact("class census [%s] %r" % (tag, c))
    return c


def read_exec_state(tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    R.setdefault("exec_state_timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def panel_rows(target):
    try:
        return list(g.panel_wiring(target) or [])
    except Exception as e:                                                         # noqa: BLE001
        fact("panel_wiring raised %s: %s" % (type(e).__name__, str(e)[:200]))
        return []


def fp_label_list(target):
    try:
        return list(g.fp_labels(target, max_n=200) or [])
    except Exception as e:                                                         # noqa: BLE001
        fact("fp_labels raised %s: %s" % (type(e).__name__, str(e)[:200]))
        return []


def owner_read(tag, uid, target):
    """owner_of with the strict identity-echo guard first, then non-strict - the answer either way is REPORTED."""
    rd = {"tag": tag, "uid": uid}
    for strict in (True, False):
        try:
            cls, ouid = owner_of(target, uid, strict=strict)
            rd.update({"strict": strict, "owner_class": cls, "owner_uid": ouid, "error_verbatim": ""})
            break
        except Exception as e:                                                     # noqa: BLE001
            rd.update({"strict": strict, "owner_class": None, "owner_uid": None,
                       "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:250])})
    R.setdefault("owner_reads", []).append(rd)
    fact("%s: owner_of(#%s) = (%r, %r) [strict=%r] error VERBATIM %r"
         % (tag, uid, rd.get("owner_class"), rd.get("owner_uid"), rd.get("strict"), rd.get("error_verbatim")))
    return rd


def node_index_of(target, diagram_index, uid, pin):
    """The 34(h)-safe Nodes[] index: try the historical PIN and accept it ONLY if the uid echoes back; otherwise
    a BOUNDED scan. Returns (index or None, how it was resolved, the rows at that index)."""
    if pin is not None:
        try:
            u, rows = g.node_terms_uid(target, diagram_index, pin)
            if u == uid:
                return pin, "pin %d survived its uid echo" % pin, rows
        except Exception as e:                                                     # noqa: BLE001
            fact("node_terms_uid(d=%r, pin=%r) raised %s: %s"
                 % (diagram_index, pin, type(e).__name__, str(e)[:140]))
    for i in range(SCAN_LIMIT):
        try:
            u, rows = g.node_terms_uid(target, diagram_index, i)
        except Exception:                                                          # noqa: BLE001
            break
        if not u:
            break
        if u == uid:
            return i, "bounded scan (pin %r did not echo)" % pin, rows
    return None, "NOT FOUND in a bounded scan of %d Nodes[] entries" % SCAN_LIMIT, []


def wired_counts(tag, target, diagram_index, uid, pin):
    """(node uid readback, n terminals, n WIRED terminals, the rows) - the 37(e) per-node metric, index-safe."""
    out = {"tag": tag, "diagram_index": diagram_index, "uid_expect": uid}
    i, how, rows = node_index_of(target, diagram_index, uid, pin)
    out["node_index"] = i
    out["index_resolution"] = how
    if i is None:
        out["error"] = "node #%s was not found on diagram index %r" % (uid, diagram_index)
    else:
        out.update({"node_uid_readback": uid, "n_terms": len(rows),
                    "n_wired": sum(1 for r in rows if r.get("wire")),
                    "terms": [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                               "wire": r["wire"]} for r in rows]})
    R.setdefault("wired_counts", []).append(out)
    fact("%s: node #%s at Nodes[%r] (%s), %r terminals, %r WIRED"
         % (tag, uid, i, how, out.get("n_terms"), out.get("n_wired")))
    return out


def class_membership(target, uid):
    """Which live Traverse class list(s) hold this uid, and at what index in each. Pure measurement; every class
    that RAISES is recorded verbatim (e.g. FlatSequence has been refused with error 1092 before)."""
    rows, errs = [], {}
    for cls in CLASS_CANDIDATES:
        try:
            uids = [o["uid"] for o in g.report_all(target, cls)]
        except Exception as e:                                                     # noqa: BLE001
            errs[cls] = "%s: %s" % (type(e).__name__, str(e)[:160])
            continue
        if uid in uids:
            rows.append({"class": cls, "index": uids.index(uid), "members": len(uids)})
    return rows, errs


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


# ==================================================================== STAGE 1: phases A..E, on PLACED
def stage1(target):
    A, B, C, E = R["phaseA"], R["phaseB"], R["phaseC"], R["phaseE"]
    Dp = R["phaseD"]

    # ------------------------------------------------------------------ PHASE A: resolve LIVE, assume nothing
    print("\n=================== PHASE A  (resolve LIVE; assume nothing, 34(h))", flush=True)
    census(R, "A before everything", target)
    read_exec_state("A BEFORE", target)

    for uid, key in ((D639, "diag_index_639"), (D536, "diag_index_536"), (D686, "diag_index_686")):
        try:
            A[key] = diag_index(target, uid)
            A[key + "_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            A[key] = None
            A[key + "_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("A diag_index(#%d) = %r ; error VERBATIM %r" % (uid, A[key], A[key + "_error_verbatim"]))
    d639, d536, d686 = A["diag_index_639"], A["diag_index_536"], A["diag_index_686"]
    gate("A1 diag_index(#639) resolves to an int", isinstance(d639, int),
         "%r (the historical 43 / 46 are NOT reused)" % (d639,), fatal=True)
    gate("A2 diag_index(#536) resolves to 0", d536 == 0, "%r" % (d536,))

    A["owner_of_10757"] = owner_read("A3 owner of the NUMERIC source #10757", SRC_UID, target)
    gate("A3 owner_of(#10757) answers ('Diagram', 639)",
         (A["owner_of_10757"].get("owner_class"), A["owner_of_10757"].get("owner_uid")) == ("Diagram", D639),
         "(%r, %r)" % (A["owner_of_10757"].get("owner_class"), A["owner_of_10757"].get("owner_uid")))
    A["owner_of_10686"] = owner_read("A4 owner of dispatch 3's BOOLEAN source #10686", BOOL_SRC_UID, target)
    gate("A4 owner_of(#10686) answers ('Diagram', 639)",
         (A["owner_of_10686"].get("owner_class"), A["owner_of_10686"].get("owner_uid")) == ("Diagram", D639),
         "(%r, %r)" % (A["owner_of_10686"].get("owner_class"), A["owner_of_10686"].get("owner_uid")))

    rows, errs = class_membership(target, SRC_UID)
    A["class_membership"] = rows
    A["class_scan_errors_verbatim"] = errs
    fact("A5 #%d is a member of these LIVE Traverse class lists: %r" % (SRC_UID, rows))
    fact("A5 classes that RAISED during the scan (recorded, never worked around): %r" % (errs,))
    # MECHANICAL selection, stated before the run: the brief says nothing but the SOURCE may differ from
    # dispatch 3, and dispatch 3 addressed its source as node_class='Function'. So `Function` is used when it
    # holds the uid; otherwise the MOST SPECIFIC class holding it (fewest members). Both are reported.
    chosen = next((r for r in rows if r["class"] == "Function"), None)
    if chosen is None and rows:
        chosen = sorted(rows, key=lambda r: r["members"])[0]
    A["chosen_class_row"] = chosen
    A["chosen_rule"] = ("`Function` when it holds the uid (dispatch 3's own addressing, so nothing but the "
                        "source differs); otherwise the class with the fewest members that holds it.")
    fact("A5 the class phase G will address #%d by: %r (rule: %s)" % (SRC_UID, chosen, A["chosen_rule"]))
    gate("A5 #10757 is found in at least one live Traverse class list, with an index in it",
         bool(chosen) and isinstance(chosen.get("index"), int), "%r" % (chosen,))

    src_terms = wired_counts("A6 the NUMERIC source #%d" % SRC_UID, target, d639, SRC_UID, SRC_NODES_PIN)
    A["source_terminals"] = src_terms
    el = next((t for t in src_terms.get("terms", []) if t["name"] == SRC_TERM_NAME), None)
    A["element_terminal"] = el
    fact("A6 #%d's FULL terminal list: %r" % (SRC_UID, src_terms.get("terms")))
    fact("A6 the terminal named %r: %r ; the wire PIN from 45(c) is %r"
         % (SRC_TERM_NAME, el, SRC_WIRE_PIN))
    gate("A6 #10757 carries a terminal named 'element' that is a SOURCE, and its wire uid is reported",
         bool(el) and bool(el.get("is_source")) and bool(el.get("wire")),
         "%r (wire pin %r)" % (el, SRC_WIRE_PIN))
    dump()
    if not el or not el.get("is_source"):
        R["stopped_at"] = ("PHASE A: #%d has no SOURCE terminal named %r on Diagram #%d, so phase G has no "
                           "payload source to branch from." % (SRC_UID, SRC_TERM_NAME, D639))
        raise Stop(R["stopped_at"])

    # ------------------------------------------------------------------ PHASE B: create ONE indicator, 46(a)
    print("\n=================== PHASE B  (create ONE indicator by the 46(a) route)", flush=True)
    rows_before = panel_rows(target)
    fpl_before = fp_label_list(target)
    B["panel_rows_before"] = len(rows_before)
    B["fp_labels_before"] = len(fpl_before)
    ct_before = g.count(target, "ControlTerminal")
    B["control_terminal_before"] = ct_before
    fact("B BEFORE: panel_wiring rows %r, fp_labels %r, ControlTerminal census %r"
         % (len(rows_before), len(fpl_before), ct_before))

    try:
        top0 = g.node_info(target, max_n=40)
        B["node_info_before_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        top0 = None
        B["node_info_before_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    B["node_info_before"] = top0
    fact("B2 node_info(max_n=40) BEFORE: %r entries -> %r ; error VERBATIM %r"
         % (len(top0) if isinstance(top0, list) else top0, top0, B["node_info_before_error_verbatim"]))

    new_ia, ia_err = None, None
    try:
        new_ia = g.build_index_array(target, IA_LOCATION)
        ia_err = ""
    except Exception as e:                                                         # noqa: BLE001
        ia_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    B["build_index_array"] = {"location": list(IA_LOCATION), "new": new_ia, "error_verbatim": ia_err}
    fact("B1 build_index_array(top-level head, %r) -> new %r ; error VERBATIM %r" % (IA_LOCATION, new_ia, ia_err))
    ia_uid = (new_ia[0]["uid"] if isinstance(new_ia, list) and new_ia else None)
    ia_owner = owner_read("B1 the new IndexArray's owner", ia_uid, target) if ia_uid else {}
    B["index_array_owner"] = ia_owner
    gate("B1 build_index_array put 1 new IndexArray on the target and owner_of reads ('TopLevelDiagram', 536)",
         isinstance(new_ia, list) and len(new_ia) == 1
         and (ia_owner.get("owner_class"), ia_owner.get("owner_uid")) == ("TopLevelDiagram", D536),
         "new %r, owner (%r, %r)" % (new_ia, ia_owner.get("owner_class"), ia_owner.get("owner_uid")))

    try:
        top1 = g.node_info(target, max_n=40)
        B["node_info_after_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        top1 = None
        B["node_info_after_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    B["node_info_after"] = top1
    fact("B2 node_info(max_n=40) AFTER (create_indicator's OWN ladder): %r entries -> %r ; error VERBATIM %r"
         % (len(top1) if isinstance(top1, list) else top1, top1, B["node_info_after_error_verbatim"]))
    gate("B2 node_info goes 0 entries -> 1 entry",
         isinstance(top0, list) and len(top0) == 0 and isinstance(top1, list) and len(top1) == 1,
         "%r -> %r" % (len(top0) if isinstance(top0, list) else top0,
                       len(top1) if isinstance(top1, list) else top1))

    node_i = (top1[-1][0] if isinstance(top1, list) and top1 else None)
    new_ct, ci_err = None, None
    if node_i is None:
        ci_err = "NOT ATTEMPTED: node_info reported no node index to address."
    else:
        try:
            new_ct = g.create_indicator(target, node_i, IA_TERM_INDEX)
            ci_err = ""
        except Exception as e:                                                     # noqa: BLE001
            ci_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    B["create_indicator"] = {"node_index": node_i, "terminal_index": IA_TERM_INDEX, "new": new_ct,
                             "error_verbatim": ci_err}
    fact("B3 create_indicator(Nodes[%r].Terminals[%d]) -> new %r ; error VERBATIM %r"
         % (node_i, IA_TERM_INDEX, new_ct, ci_err))
    ct_after = g.count(target, "ControlTerminal")
    B["control_terminal_after_create"] = ct_after
    new_ct_uid = (new_ct[0].get("uid") if isinstance(new_ct, list) and new_ct else None)
    gate("B3 create_indicator returned a ControlTerminal and the census went %r -> %r" % (ct_before, ct_after),
         isinstance(new_ct_uid, int) and isinstance(ct_before, int) and ct_after == ct_before + 1,
         "new uid %r, census %r -> %r" % (new_ct_uid, ct_before, ct_after))

    gone, del_err = None, None
    if ia_uid is None:
        del_err = "NOT ATTEMPTED: no IndexArray uid to delete."
    else:
        try:
            ias = [o["uid"] for o in g.report_all(target, "IndexArray")]
            B["index_array_traverse_index_at_delete"] = ias.index(ia_uid)
            gone = g.delete_object(target, "IndexArray", ias.index(ia_uid))
            del_err = ""
        except Exception as e:                                                     # noqa: BLE001
            del_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    B["delete_object"] = {"gone": sorted(gone) if gone else gone, "error_verbatim": del_err}
    fact("B4 delete_object(IndexArray[%r]) -> gone %r ; error VERBATIM %r"
         % (B.get("index_array_traverse_index_at_delete"), sorted(gone) if gone else gone, del_err))
    gate("B4 delete_object removed exactly 1 object", bool(gone) and len(gone) == 1,
         "%r (error %r)" % (sorted(gone) if gone else gone, del_err))
    es_after_del = read_exec_state("B5 after delete_object", target)
    B["exec_state_after_delete"] = es_after_del
    gate("B5 ExecState after the delete == 1", es_after_del == 1, "%r" % (es_after_del,))
    dump()
    if not isinstance(new_ct_uid, int):
        R["stopped_at"] = "PHASE B: create_indicator returned no ControlTerminal uid, so there is nothing to move."
        raise Stop(R["stopped_at"])

    # ------------------------------------------------------------------ PHASE C: READ the label off the machine
    print("\n=================== PHASE C  (READ the new indicator's label off the machine - nothing is retyped)",
          flush=True)
    rows_after = panel_rows(target)
    fpl_after = fp_label_list(target)
    C["panel_rows_after_create"] = len(rows_after)
    C["fp_labels_after_create"] = len(fpl_after)
    before_keys = {(r.get("uid"), r.get("label")) for r in rows_before}
    new_rows = [r for r in rows_after if (r.get("uid"), r.get("label")) not in before_keys]
    C["new_panel_rows"] = new_rows
    before_fp = {(i, t) for (i, t, _ind) in fpl_before}
    new_fp = [(i, t, ind) for (i, t, ind) in fpl_after if (i, t) not in before_fp]
    C["new_fp_labels"] = new_fp
    fact("C1 panel_wiring rows %r -> %r ; the NEW row(s) %r" % (len(rows_before), len(rows_after), new_rows))
    fact("C1 fp_labels %r -> %r ; the NEW entr(y/ies) %r" % (len(fpl_before), len(fpl_after), new_fp))

    label, label_source = None, None
    if len(new_rows) == 1 and new_rows[0].get("label") is not None:
        label, label_source = new_rows[0]["label"], "panel_wiring diff (the machine's own Control.Label text)"
    elif len(new_fp) == 1:
        label, label_source = new_fp[0][1], "fp_labels diff (the machine's own Control.Label text)"
    C["label_repr"] = repr(label)
    C["label_utf8_hex"] = (label or "").encode("utf-8").hex() if label is not None else None
    C["label_source"] = label_source
    C["label_contains_newline"] = (("\n" in label) or ("\r" in label)) if label is not None else None
    existing_labels = [r.get("label") for r in rows_before]
    C["label_is_duplicate_of_an_existing_panel_label"] = (label in existing_labels) if label is not None else None
    C["new_ct_uid"] = new_ct_uid
    fact("C THE LABEL, VERBATIM: %r  (utf-8 hex %r, source: %s)" % (label, C["label_utf8_hex"], label_source))
    fact("C contains a NEWLINE: %r (docs/d1-build-plan.md:1232-1233 - a newline still fails from `Wire "
         "Inputs.vi` even at a nested diagram index)" % (C["label_contains_newline"],))
    fact("C is a DUPLICATE of an existing panel label: %r"
         % (C["label_is_duplicate_of_an_existing_panel_label"],))
    gate("C1 exactly ONE new front-panel row appeared and its label was READ off the machine",
         (len(new_rows) == 1 or (not new_rows and len(new_fp) == 1)) and label is not None,
         "%r new panel row(s), %r new fp_labels entr(y/ies), label %r" % (len(new_rows), len(new_fp), label))
    gate("C2 the new label is UNIQUE among the target's panel labels",
         C["label_is_duplicate_of_an_existing_panel_label"] is False,
         "duplicate=%r" % (C["label_is_duplicate_of_an_existing_panel_label"],))
    C["owner_of_new_ct"] = owner_read("C3 the new ControlTerminal's owner (BEFORE the move)", new_ct_uid, target)
    gate("C3 owner_of(new ControlTerminal uid) answers",
         C["owner_of_new_ct"].get("owner_class") is not None,
         "(%r, %r)" % (C["owner_of_new_ct"].get("owner_class"), C["owner_of_new_ct"].get("owner_uid")))
    dump()
    if label is None:
        R["stopped_at"] = ("PHASE C: the new indicator's label could not be READ off the machine, and a label is "
                           "never retyped - phase G would have no byte-exact name to pass.")
        raise Stop(R["stopped_at"])

    # ------------------------------------------------------------------ PHASE D: move_in TOP-LEVEL -> NESTED
    print("\n=================== PHASE D  (move_in TOP-LEVEL -> NESTED Diagram #639)", flush=True)
    Dp["dest_diagram_uid"] = D639
    Dp["dest_diagram_index_live"] = d639
    Dp["position"] = list(MOVE_POSITION)
    Dp["owner_before"] = C["owner_of_new_ct"]
    ct_b = g.count(target, "ControlTerminal")
    rows_b = len(rows_after)
    es_b = read_exec_state("D BEFORE the move", target)
    try:
        inv_before = set(g.uids(target, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_before = set()
        fact("uids(Invoke) BEFORE raised %s: %s" % (type(e).__name__, str(e)[:140]))
    Dp["invoke_uids_before"] = sorted(inv_before)

    mv_ret, mv_err = None, None
    try:
        mv_ret = move_in(target, new_ct_uid, d639, MOVE_POSITION)
        mv_err = ""
    except Exception as e:                                                         # noqa: BLE001
        mv_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    Dp["move_in"] = {"returned": mv_ret, "error_verbatim": mv_err}
    fact("D1 move_in(#%r -> Diagram #%d at Traverse index %r, position %r) returned %r ; error VERBATIM %r"
         % (new_ct_uid, D639, d639, MOVE_POSITION, mv_ret, mv_err))
    gate("D1 move_in returned without raising", mv_err == "", "returned %r, error %r" % (mv_ret, mv_err))

    # PREDICTED RISK (i): the junk `Invoke` residue of the op itself. RECORDED, then purged exactly as
    # tools/recipes/build_d1_routeb_v0.py:1279-1287 does - the set is `after - before`.
    try:
        inv_after = set(g.uids(target, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_after = set()
        fact("uids(Invoke) AFTER raised %s: %s" % (type(e).__name__, str(e)[:140]))
    junk = sorted(inv_after - inv_before)
    Dp["junk_invoke_uids_added_by_move_in"] = junk
    Dp["junk_purge"] = []
    fact("D1 move_in left %r junk `Invoke`(s): %r (PREDICTED RISK (i))" % (len(junk), junk))
    for ju in junk:
        rec = {"uid": ju}
        try:
            cur = [o["uid"] for o in g.report_all(target, "Invoke")]
            rec["gone"] = sorted(g.delete_object(target, "Invoke", cur.index(ju)) or [])
            rec["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            rec["gone"] = None
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        Dp["junk_purge"].append(rec)
        fact("D1 purged junk Invoke #%r -> gone %r ; error VERBATIM %r" % (ju, rec["gone"], rec["error_verbatim"]))

    Dp["owner_after"] = owner_read("D2 the new ControlTerminal's owner (AFTER the move)", new_ct_uid, target)
    ct_a = g.count(target, "ControlTerminal")
    rows_a = panel_rows(target)
    es_a = read_exec_state("D AFTER the move (and the junk purge)", target)
    Dp["control_terminal_census"] = {"before": ct_b, "after": ct_a}
    Dp["panel_row_count"] = {"before": rows_b, "after": len(rows_a)}
    Dp["exec_state"] = {"before": es_b, "after": es_a}
    gate("D2 owner_of(new uid) reads ('Diagram', 639) AFTER the move",
         (Dp["owner_after"].get("owner_class"), Dp["owner_after"].get("owner_uid")) == ("Diagram", D639),
         "(%r, %r) -> (%r, %r)"
         % (Dp["owner_before"].get("owner_class"), Dp["owner_before"].get("owner_uid"),
            Dp["owner_after"].get("owner_class"), Dp["owner_after"].get("owner_uid")))
    gate("D3 the ControlTerminal census is unchanged across the move", ct_b == ct_a, "%r -> %r" % (ct_b, ct_a))
    gate("D4 the panel row count is unchanged across the move", rows_b == len(rows_a),
         "%r -> %r" % (rows_b, len(rows_a)))
    gate("D5 ExecState after the move (and the junk purge) == 1", es_a == 1, "%r -> %r" % (es_b, es_a))
    row_now = next((r for r in rows_a if r.get("label") == label), None)
    Dp["target_row_after_move"] = row_now
    fact("D the target indicator's panel row after the move: %r" % (row_now,))
    dump()

    # ------------------------------------------------------------------ PHASE E: SAVE BEFORE ANY WIRING
    print("\n=================== PHASE E  (SAVE HERE, BEFORE ANY WIRING - the run's PRIMARY deliverable)",
          flush=True)
    es_save = read_exec_state("E immediately before the save attempt", target)
    size, serr = None, None
    if isinstance(es_save, int) and es_save == 1:
        try:
            size = g.save(target)          # allow_broken stays False; gui_save is NEVER called
        except Exception as e:                                                     # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:400])
    else:
        serr = ("NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved. Under this brief that STOPS "
                "the run here, and it is a LEGITIMATE outcome, not a failure to work around." % (es_save,))
    E["exec_state_before_save"] = es_save
    E["returned_bytes"] = size
    E["exception_or_reason_verbatim"] = serr
    E["allow_broken"] = False
    E["gui_save"] = False
    E["new_ct_uid"] = new_ct_uid
    E["label"] = label
    fact("E g.save() returned %r ; exception/reason VERBATIM %r" % (size, serr))
    E["file_after"] = D.file_facts("E the PRIMARY artefact after the save attempt", target)
    gate("E1 ExecState == 1 at the save point and g.save() returned a byte count",
         isinstance(size, int) and size > 0, "ExecState %r, bytes %r, reason %r" % (es_save, size, serr))
    vb = E["file_after"].get("version_candidates") if E["file_after"].get("exists") else None
    gate("E2 the phase-E artefact is on disk and its version bytes read 26 00 80 00 (LV2026)",
         bool(E["file_after"].get("exists")) and any("26 00 80 00" in c.get("bytes", "") for c in (vb or [])),
         "%r" % (vb,))
    dump()
    if not isinstance(size, int):
        R["stopped_at"] = ("PHASE E: ExecState was %r at the save point, so nothing was saved and the run stops "
                           "here exactly as the brief orders." % (es_save,))
        raise Stop(R["stopped_at"])
    return {"new_ct_uid": new_ct_uid, "label": label, "chosen_class": chosen}


# ==================================================================== STAGE 2: phases F..I, on NUMIND
def stage_f_cold(new_ct_uid):
    """PHASE F: the COLD reopen. LabVIEW has just been RESTARTED, so this is a load from disk into a fresh
    instance with NOTHING preloaded - not a read of the in-memory target."""
    F = R["phaseF"]
    print("\n=================== PHASE F  (COLD reopen of the phase-E artefact in a FRESH LabVIEW instance)",
          flush=True)
    F["path"] = PLACED
    F["preloaded"] = False
    F["exec_state_cold"] = read_exec_state("F COLD open of the saved artefact (fresh instance, no preload)",
                                           PLACED)
    gate("F1 the COLD reopen reads ExecState 1", F["exec_state_cold"] == 1, "%r" % (F["exec_state_cold"],))
    F["owner_of_new_ct"] = owner_read("F2 the moved ControlTerminal's owner on the COLD open", new_ct_uid, PLACED)
    gate("F2 owner_of(new uid) on the COLD open reads ('Diagram', 639)",
         (F["owner_of_new_ct"].get("owner_class"), F["owner_of_new_ct"].get("owner_uid")) == ("Diagram", D639),
         "(%r, %r)" % (F["owner_of_new_ct"].get("owner_class"), F["owner_of_new_ct"].get("owner_uid")))
    for uid, key in ((D639, "diag_index_639"), (D536, "diag_index_536"), (D686, "diag_index_686")):
        try:
            F[key] = diag_index(PLACED, uid)
            F[key + "_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            F[key] = None
            F[key + "_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("F diag_index(#%d) on the COLD open = %r ; error VERBATIM %r"
             % (uid, F[key], F[key + "_error_verbatim"]))
    rows, errs = class_membership(PLACED, SRC_UID)
    F["class_membership"] = rows
    F["class_scan_errors_verbatim"] = errs
    fact("F #%d's LIVE class membership on the COLD open: %r (errors %r)" % (SRC_UID, rows, errs))
    census(R, "F on the COLD open", PLACED)
    dump()


def stage2(target, new_ct_uid, label):
    """PHASES G..I on NUMIND, a byte copy of the phase-E artefact (gscript has no save-as, gscript.py:2062)."""
    G, H, I = R["phaseG"], R["phaseH"], R["phaseI"]

    # ------------------------------------------------------------------ PHASE G: wire it
    print("\n=================== PHASE G  (wire the NUMERIC source #%d t 'element' to the new indicator)"
          % SRC_UID, flush=True)
    try:
        d639 = diag_index(target, D639)
    except Exception as e:                                                         # noqa: BLE001
        d639 = None
        fact("diag_index(#639) on the wiring copy raised %s: %s" % (type(e).__name__, str(e)[:160]))
    try:
        d686 = diag_index(target, D686)
    except Exception as e:                                                         # noqa: BLE001
        d686 = None
        fact("diag_index(#686) on the wiring copy raised %s: %s" % (type(e).__name__, str(e)[:160]))
    G["diag_index_639_live"] = d639
    G["diag_index_686_live"] = d686
    rows_live, errs_live = class_membership(target, SRC_UID)
    G["class_membership_live"] = rows_live
    G["class_scan_errors_verbatim"] = errs_live
    chosen = next((r for r in rows_live if r["class"] == "Function"), None)
    if chosen is None and rows_live:
        chosen = sorted(rows_live, key=lambda r: r["members"])[0]
    G["chosen_class_row_live"] = chosen
    fact("G LIVE on the wiring copy: diag_index(#639) = %r, #%d class membership %r, addressing it as %r"
         % (d639, SRC_UID, rows_live, chosen))

    # the source terminal, RE-READ off this file (never carried over as a typed string)
    src_before = wired_counts("G BEFORE #%d (the NUMERIC source node)" % SRC_UID, target, d639, SRC_UID,
                              SRC_NODES_PIN)
    el = next((t for t in src_before.get("terms", []) if t["name"] == SRC_TERM_NAME), None)
    G["element_terminal_live"] = el
    fact("G #%d's terminal %r re-read on this file: %r" % (SRC_UID, SRC_TERM_NAME, el))
    loop_before = wired_counts("G BEFORE #%d (loop 1.1, the tunnel/border witness)" % LOOP11_UID, target,
                               d686 if isinstance(d686, int) else 0, LOOP11_UID, LOOP11_NODES_PIN)

    # the indicator label, RE-READ off this file by its uid/label row
    rows_p = panel_rows(target)
    row_now = next((r for r in rows_p if r.get("label") == label), None)
    G["target_row_before_wiring"] = row_now
    label_live = (row_now or {}).get("label")
    fact("G the indicator row re-read on this file: %r (label VERBATIM %r, utf-8 hex %r)"
         % (row_now, label_live, (label_live or "").encode("utf-8").hex()))

    wire_b = (row_now or {}).get("wire")
    wires_b = g.count(target, "Wire")
    es_pre = read_exec_state("G BEFORE wire_indicators", target)
    wi_dt, wi_err = None, None
    if not chosen or el is None or not isinstance(d639, int) or label_live is None:
        wi_err = ("NOT ATTEMPTED: class row %r / element terminal %r / diagram index %r / label %r unresolved."
                  % (chosen, el, d639, label_live))
    else:
        try:
            wi_dt = g.wire_indicators(target, chosen["index"], [el["name"]], [label_live],
                                      diagram_index=d639, node_class=chosen["class"])
            wi_err = ""
        except Exception as e:                                                     # noqa: BLE001
            wi_err = "%s: %s" % (type(e).__name__, str(e)[:900])
    G["wire_indicators"] = {"node_index": (chosen or {}).get("index"), "node_class": (chosen or {}).get("class"),
                            "src_terms_repr": repr([(el or {}).get("name")]),
                            "indicator_names_repr": repr([label_live]),
                            "indicator_names_utf8_hex": [(label_live or "").encode("utf-8").hex()],
                            "diagram_index": d639, "seconds": wi_dt, "error_verbatim": wi_err}
    fact("G1 wire_indicators(%s[%r], [%r] -> [%r], diagram_index=%r) error VERBATIM %r"
         % ((chosen or {}).get("class"), (chosen or {}).get("index"), (el or {}).get("name"), label_live,
            d639, wi_err))
    gate("G1 wire_indicators returned an EMPTY error column", wi_err == "", repr(wi_err))

    rows_w = panel_rows(target)
    row_w = next((r for r in rows_w if r.get("label") == label), None)
    wire_a = (row_w or {}).get("wire")
    wires_a = g.count(target, "Wire")
    G["target_row_after_wiring"] = row_w
    G["target_wire_uid"] = {"before": wire_b, "after": wire_a}
    G["whole_vi_wire_count"] = {"before": wires_b, "after": wires_a,
                                "delta": (wires_a - wires_b) if isinstance(wires_a, int)
                                and isinstance(wires_b, int) else None}
    fact("G2 the target indicator's wire uid %r -> %r ; whole-VI Wire count %r -> %r (delta %r; a BRANCH adds NO "
         "Wire object, tools/gscript.py:1771-1772). The source terminal's own wire reads %r (45(c) pin %r)"
         % (wire_b, wire_a, wires_b, wires_a, G["whole_vi_wire_count"]["delta"], (el or {}).get("wire"),
            SRC_WIRE_PIN))
    gate("G2 the new indicator's wire uid changed from 0", bool(wire_a) and wire_a != wire_b,
         "%r -> %r" % (wire_b, wire_a))
    es_post = read_exec_state("G AFTER wire_indicators", target)
    G["exec_state"] = {"before": es_pre, "after": es_post}

    src_after = wired_counts("G AFTER #%d (the NUMERIC source node)" % SRC_UID, target, d639, SRC_UID,
                             SRC_NODES_PIN)
    loop_after = wired_counts("G AFTER #%d (loop 1.1, the tunnel/border witness)" % LOOP11_UID, target,
                              d686 if isinstance(d686, int) else 0, LOOP11_UID, LOOP11_NODES_PIN)
    gate("G3 #%d's wired-terminal count is unchanged across the wiring (37(e))" % SRC_UID,
         src_before.get("n_wired") is not None and src_after.get("n_wired") is not None
         and src_before.get("n_wired") == src_after.get("n_wired"),
         "%r -> %r wired of %r -> %r terminals" % (src_before.get("n_wired"), src_after.get("n_wired"),
                                                   src_before.get("n_terms"), src_after.get("n_terms")))
    gate("G4 #%d's terminal count unchanged - NO tunnel or border object appeared (37(e))" % LOOP11_UID,
         loop_before.get("n_terms") is not None and loop_before.get("n_terms") == loop_after.get("n_terms"),
         "%r -> %r terminals, %r -> %r wired"
         % (loop_before.get("n_terms"), loop_after.get("n_terms"),
            loop_before.get("n_wired"), loop_after.get("n_wired")))
    fact("G4 EXPLICIT (37(e) grain): #%d terminals %r -> %r, wired %r -> %r; a tunnel or border object would show "
         "as a terminal-count INCREASE. Increase observed: %r"
         % (LOOP11_UID, loop_before.get("n_terms"), loop_after.get("n_terms"), loop_before.get("n_wired"),
            loop_after.get("n_wired"),
            (loop_after.get("n_terms") or 0) - (loop_before.get("n_terms") or 0)))
    census(R, "G after the wiring attempt", target)
    dump()

    # ------------------------------------------------------------------ PHASE H: save again IFF legal
    print("\n=================== PHASE H  (save again IFF ExecState == 1 - a 0 is a LEGITIMATE outcome and "
          "phase E's artefact still stands)", flush=True)
    es_save = read_exec_state("H immediately before the second save attempt", target)
    size, serr = None, None
    if isinstance(es_save, int) and es_save == 1:
        try:
            size = g.save(target)          # allow_broken stays False; gui_save is NEVER called
        except Exception as e:                                                     # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:400])
    else:
        serr = ("NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved. Phase E's artefact still "
                "stands." % (es_save,))
    H["exec_state_before_save"] = es_save
    H["returned_bytes"] = size
    H["exception_or_reason_verbatim"] = serr
    H["allow_broken"] = False
    H["gui_save"] = False
    fact("H g.save() returned %r ; exception/reason VERBATIM %r" % (size, serr))
    H["file_after"] = D.file_facts("H the second artefact after the save attempt", target)
    gate("H1 ExecState == 1 at the second save point and g.save() returned a byte count",
         isinstance(size, int) and size > 0, "ExecState %r, bytes %r, reason %r" % (es_save, size, serr))
    dump()

    # ------------------------------------------------------------------ PHASE I: the ORDERED second pass, 42(b)
    print("\n=================== PHASE I  (ORDERED second pass: `Is Broken?`, AFTER the phase-H save, 42(b))",
          flush=True)
    if not wire_a:
        I["not_attempted_because"] = ("phase G produced no wire on the indicator (uid %r -> %r), so 42(b)'s "
                                      "ordered pass has nothing to read." % (wire_b, wire_a))
        fact("I NOT ATTEMPTED: %s" % I["not_attempted_because"])
        dump()
        return
    # The idempotent re-connect needs an EXISTING connection on the SAME net: a non-source terminal already
    # carrying the source's wire, DISCOVERED on the machine (never pinned).
    src_i, src_how, _rows = node_index_of(target, d639, SRC_UID, SRC_NODES_PIN)
    net_wire = (el or {}).get("wire")
    sink = None
    if isinstance(d639, int) and net_wire:
        for i in range(SCAN_LIMIT):
            try:
                u, rows_n = g.node_terms_uid(target, d639, i)
            except Exception:                                                      # noqa: BLE001
                break
            if not u:
                break
            if u == SRC_UID:
                continue
            for r in rows_n:
                if r.get("wire") == net_wire and not r.get("is_source"):
                    sink = {"node_uid": u, "node_index": i, "term_index": r["i"], "term_name": r["name"],
                            "wire": r["wire"]}
                    break
            if sink:
                break
    I["source"] = {"uid": SRC_UID, "node_index": src_i, "index_resolution": src_how,
                   "term_index": (el or {}).get("i"), "term_name": (el or {}).get("name"), "wire": net_wire}
    I["sink_discovered"] = sink
    I["method"] = ("an IDEMPOTENT re-connect of an EXISTING connection on the SAME net (wire %r): the source "
                   "terminal #%d '%s' into a non-source terminal already carrying that wire, DISCOVERED by a "
                   "bounded scan of Diagram #%d. A front-panel ControlTerminal is not in Nodes[], so no 6371004 "
                   "carrier can address the indicator end; the same NET is read instead. wire_delta must be 0."
                   % (net_wire, SRC_UID, SRC_TERM_NAME, D639))
    fact("I the ordered pass will re-connect: source %r -> sink %r" % (I["source"], sink))
    if sink is None or src_i is None:
        I["not_attempted_because"] = ("the 6371004 carrier needs BOTH ends addressable in Nodes[]: source index "
                                      "%r, a sink already on wire %r %r." % (src_i, net_wire, sink))
        fact("I NOT ATTEMPTED: %s" % I["not_attempted_because"])
        dump()
        return
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, d639, sink["node_index"], sink["term_index"],
                                     d639, src_i, (el or {}).get("i", 0), V1_LABELS)
        I.update({"wire_delta": dw, "exec_state_returned": es, "error_verbatim": err})
    except Exception as e:                                                         # noqa: BLE001
        I.update({"wire_delta": None, "exec_state_returned": None,
                  "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    I["op_indicators"] = op_indicators()
    ib = I["op_indicators"].get("Is Broken?")
    I["is_broken_ordered"] = ib
    fact("I ORDERED `Is Broken?` = %r on wire uid %r (op error column %r, wire_delta %r). True here is a "
         "LEGITIMATE reading, not a failure."
         % (ib, I["op_indicators"].get("UID 2"), I.get("error_verbatim"), I.get("wire_delta")))
    gate("I1 the ORDERED second-pass `Is Broken?` read returned a boolean", isinstance(ib, bool), repr(ib))
    read_exec_state("I after the Is Broken? read (SUSPECT, docs/NAMES.md:912-918; both saves already happened)",
                    target)
    dump()


# ==================================================================== PHASE J: the files-only reading
def phase_j():
    """Is there ANY reader in the fleet that returns a TERMINAL's or a CONTROL's DATA TYPE? Files only, no build."""
    import re
    J = R["phaseJ"]
    print("\n=================== PHASE J  (files-only: does ANY reader return a terminal's/control's DATA TYPE?)",
          flush=True)
    pat = re.compile(r"representation|data\s*type|datatype|type\s*descriptor|typedesc", re.I)
    targets = [os.path.join(ROOT, "tools", "gscript.py"),
               os.path.join(ROOT, "docs", "toolkit-capabilities.md"),
               os.path.join(ROOT, "docs", "NAMES.md"),
               os.path.join(ROOT, "docs", "vi-server-ids.json")]
    hits = []
    for p in targets:
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                for n, line in enumerate(f, 1):
                    if pat.search(line):
                        hits.append({"file": os.path.relpath(p, ROOT).replace("\\", "/"), "line": n,
                                     "text": line.strip()[:220]})
        except Exception as e:                                                     # noqa: BLE001
            hits.append({"file": p, "line": None, "text": "ERROR %s: %s" % (type(e).__name__, str(e)[:120])})
    J["hits"] = hits
    J["n_hits"] = len(hits)
    for h in hits[:20]:
        fact("J hit %s:%s  %s" % (h["file"], h["line"], h["text"][:180]))
    fact("J total hits across gscript.py + toolkit-capabilities.md + NAMES.md + vi-server-ids.json: %d" % len(hits))
    J["verdict_note"] = ("The hits are REPORTED, not interpreted. The one representation reader the fleet owns is "
                         "`OpConstValueN_v1.vi` (`NumericConstant.Representation` 5DCFC00, "
                         "docs/toolkit-capabilities.md:59, docs/NAMES.md:969) and it reads a numeric CONSTANT's "
                         "representation - not a TERMINAL's and not a CONTROL's data type. Whether any hit above "
                         "amounts to a terminal/control type reader is left to the reader of this log; NOTHING "
                         "WAS BUILT.")
    fact("J %s" % J["verdict_note"])
    dump()


# ======================================================================================== MAIN
def main():
    print("=== diag_s57_typepair  %s   (cycle 57 dispatch 4; DIAGNOSTIC, never a recipe; phases A..J; NO VI IS "
          "RUN, 34(f); no new op, no new device, no GUI action; CHOOSES NOTHING)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    fact("tools/recipes/stage_d1_s3a_focus_ind.py: exists=%r mtime=%r - REPORTED, NOT TOUCHED (stop-recorded by "
         "archive/peer/2026-09-20-priorart-d1-s3a-focus-ind.md; guard_cycle refuses a recipe build this cycle)"
         % (R["recipe_file_reported_not_touched"]["exists"], R["recipe_file_reported_not_touched"]["mtime"]))
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (cycle 57 dispatch 3 left the instance at ~60,299; fresh baseline ~31,500): %r"
         % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    # ---- the mechanical pre-batch restart the brief orders (44(e)/46(j); standing restart permission, CLAUDE.md 3)
    D.fresh("T2b RESTART (pre-batch, 44(e)/46(j))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    # ---- the dated scratch, which IS the phase-E artefact path (no save-as verb exists, gscript.py:2062)
    if os.path.exists(PLACED):
        os.remove(PLACED)
    shutil.copy2(S2_ARTEFACT, PLACED)
    p = probe("T3 the scratch at creation (copied from D1_s2_loops.vi)", PLACED)
    R["scratch_at_creation"] = p
    gate("T3 the scratch is byte-identical to D1_s2_loops.vi at creation", p.get("md5") == S2_MD5,
         "%s (expected %s)" % (p.get("md5", "?"), S2_MD5), fatal=True)
    dump()

    placed_saved, carry = False, None
    try:
        with D.Preload("S57B stage 1"):
            g.open_panel(PLACED)
            time.sleep(1.0)
            try:
                carry = stage1(PLACED)
            finally:
                placed_saved = isinstance(R["phaseE"].get("returned_bytes"), int)
                close_quietly(PLACED)
    except Stop as s:
        fact("STOPPED at a phase precondition: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        fact("stage 1 raised %s: %s" % (type(e).__name__, str(e)[:600]))
    dump()

    numind_saved = False
    if placed_saved and carry:
        # ---- PHASE F needs a genuinely COLD load: restart LabVIEW so nothing of stage 1 is resident.
        try:
            R["handles"]["before_cold_restart"] = labview_handles()
            D.fresh("F RESTART (so the phase-E artefact is loaded COLD, from disk, with nothing preloaded)")
            R["handles"]["after_cold_restart"] = labview_handles()
            fact("LabVIEW handles across the phase-F restart: %r -> %r"
                 % (R["handles"].get("before_cold_restart"), R["handles"].get("after_cold_restart")))
            stage_f_cold(carry["new_ct_uid"])
        except Exception as e:                                                     # noqa: BLE001
            fact("PHASE F raised %s: %s" % (type(e).__name__, str(e)[:400]))
        dump()

        # ---- PHASES G..I on a byte copy under the phase-H name, so phase E's file is never overwritten.
        try:
            if os.path.exists(NUMIND):
                os.remove(NUMIND)
            shutil.copy2(PLACED, NUMIND)
            q = probe("G0 the wiring copy at creation (copied from the phase-E artefact)", NUMIND)
            R["numind_at_creation"] = q
            fact("G0 the wiring copy is byte-identical to the phase-E artefact: %r"
                 % (q.get("md5") == R["phaseE"].get("file_after", {}).get("md5"),))
            with D.Preload("S57B stage 2"):
                g.open_panel(NUMIND)
                time.sleep(1.0)
                try:
                    stage2(NUMIND, carry["new_ct_uid"], carry["label"])
                finally:
                    numind_saved = isinstance(R["phaseH"].get("returned_bytes"), int)
                    close_quietly(NUMIND)
        except Stop as s:
            fact("STOPPED at a phase precondition: %s" % s)
        except Exception as e:                                                     # noqa: BLE001
            fact("stage 2 raised %s: %s" % (type(e).__name__, str(e)[:600]))
    else:
        fact("PHASES F..I NOT ATTEMPTED: phase E did not save (ExecState %r), and the brief orders the run to "
             "stop there." % (R["phaseE"].get("exec_state_before_save"),))
    dump()

    phase_j()

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

    # NOTHING SAVED IS EVER DELETED. The phase-E artefact is the run's primary deliverable and is KEPT whatever
    # happened later. The wiring copy is removed ONLY when phase H did not save it, because it is then a
    # byte-identical duplicate of the phase-E artefact with nothing of its own on disk. ONE attempt, no retry.
    R["cleanup"] = []
    for path, saved, what in ((PLACED, placed_saved, "the PRIMARY (phase-E) artefact"),
                              (NUMIND, numind_saved, "the phase-G/H wiring copy")):
        rec = {"path": path, "saved": saved, "what": what, "exists": os.path.exists(path)}
        if saved:
            rec["action"] = "KEPT - saved; deleting a saved artefact is forbidden."
        elif not rec["exists"]:
            rec["action"] = "nothing on disk"
        else:
            try:
                os.remove(path)
                rec["action"] = "removed (never saved by this run)"
                rec["error_verbatim"] = ""
            except Exception as e:                                                 # noqa: BLE001
                rec["action"] = "remove FAILED"
                rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        R["cleanup"].append(rec)
        fact("cleanup: %r" % (rec,))

    zo = probe("Z1 ORIGINAL after everything", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after everything", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after everything", S2_ARTEFACT)
    gate("Z1 ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 all unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5,
         "%s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z2 refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    fact("ARTEFACTS: PRIMARY %r ; wiring copy %r"
         % ({"path": PLACED, "bytes": R["phaseE"].get("returned_bytes"),
             "file": R["phaseE"].get("file_after")},
            {"path": NUMIND, "bytes": R["phaseH"].get("returned_bytes"),
             "file": R["phaseH"].get("file_after")}))
    if R.get("stopped_at"):
        fact("THE RUN STOPPED AT: %s" % R["stopped_at"])

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
