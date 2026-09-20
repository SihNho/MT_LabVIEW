"""diag_s57_ctmove_wire - cycle 57 material #3. A DIAGNOSTIC under tools/bench/, never a recipe.

WHAT IS BEING MEASURED (the brief's words; this script interprets nothing, chooses nothing, edits no plan):
  THE S3a TRANSPORT ROUTE, END TO END, ON ONE INDICATOR. Each of its three steps is individually measured on
  disk and NO RUN HAS EVER JOINED THEM:
    * create at top level  - Pre-decided 46(a): `build_index_array` on the `VI -> Block Diagram` head ->
      `create_indicator(Nodes[0].Terminals[2])` -> `delete_object(IndexArray[0])`. Measured 2026-09-20 in
      tools/bench/diag_s56_transport3.log:68-80 (IndexArray #23486 owner ('TopLevelDiagram', 536), node_info
      0 -> 1, ControlTerminal #23541, census 114 -> 115, ExecState 1 after the delete).
    * `move_in` a `ControlTerminal` into a NESTED diagram - tools/bench/probe_move_ctlterm_v0.log:130-133 did it
      ONCE (CT #642, Diagram #639 -> #1170, PASS, census 114 -> 114). That was NESTED -> NESTED; TOP-LEVEL ->
      NESTED has never been tried, and neither has it on a FRESHLY CREATED terminal.
    * wire by LABEL at a nested diagram index - docs/d1-build-plan.md:1231: 'Auto-Reset' at
      `src_diagram_index=43` (= Diagram #639) WIRED, sink wire 0 -> 1231, no error, while `src_diagram_index=0`
      gave 5001 from `Get Controls.vi`. Known hazard at :1232-1233: a label containing a NEWLINE still fails,
      from `Wire Inputs.vi`, even at index 43.

PHASES (measure and report each; decide nothing from them):
  1  Resolve LIVE indices on THIS scratch, assuming none of them: diag_index(#639), diag_index(#536),
     owner_of(#639), owner_of(#10686), and the live Traverse(`Function`) index of #10686. Cycles 54/56 measured
     that S2's three added loops shift Traverse order, so 43, 46 and 102 are HISTORICAL and are not reused.
  2  Create ONE indicator by the 46(a) route.
  3  READ the new indicator's front-panel LABEL off the machine (panel_wiring diff + fp_labels diff) and report
     it VERBATIM, stating explicitly whether it contains a newline or duplicates an existing panel label.
     Nothing is retyped: the string handed to phase 5 is the one the machine returned.
  4  `move_in(new ControlTerminal uid, dest_diagram_index = the LIVE index of #639 from phase 1)`.
  5  `wire_indicators(node_index = live Traverse('Function') index of #10686, src_terms=['x .and. y?'],
     indicator_names=[the label read in phase 3], diagram_index = live index of #639, node_class='Function')`.
  6  Save IFF legal: ExecState == 1 on a PRELOADED open -> `g.save()`. ExecState 0 => NO SAVE, and that is a
     LEGITIMATE outcome, not a failure to work around.
  7  ORDERED SECOND PASS (42(b)), only if phase 5 produced a wire and only AFTER the save: read
     `Wire.Is Broken?` by an IDEMPOTENT re-connect on the same net, wire_delta expected 0.

PREDICTION CONTRACT (every line is a printed GATE. 46(g): a gate that makes NO CALL to the machine is a note,
not a FAIL - every gate below is the readback of a call):
  T1   the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                          (FATAL)
  T1b  claudeDev\\D1_s1_copy.vi md5 == 3e3d23cefd3a334001aa9d6156bf1aee
  T2   claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                                (FATAL)
  T3   the scratch is byte-identical to D1_s2_loops.vi at creation                                      (FATAL)
  P1a  diag_index(#639) resolves to an int
  P1b  diag_index(#536) resolves to 0                        (46(b) measured this live in cycle 56; re-measured)
  P1c  owner_of(#639) answers ('WhileLoop', 637)
  P1d  owner_of(#10686) answers ('Diagram', 639)
  P1e  #10686 is found in the live Traverse(`Function`) uid list
  P2a  build_index_array puts exactly 1 new IndexArray on the target and owner_of reads ('TopLevelDiagram', 536)
  P2b  node_info(max_n=40) goes 0 entries -> 1 entry
  P2c  create_indicator(Nodes[0].Terminals[2]) returns a ControlTerminal and the census goes 114 -> 115
  P2d  delete_object(IndexArray[0]) removes exactly 1 object
  P2e  ExecState after the delete == 1
  P3a  exactly ONE new front-panel row appeared, and its label is READ off the machine (not retyped)
  P3b  the new label is UNIQUE among the target's panel labels                       (a duplicate is a READING)
  P3c  owner_of(new ControlTerminal uid) answers
  P4a  move_in returned without raising                                       (TOP-LEVEL -> NESTED, never tried)
  P4b  owner_of(new uid) reads ('Diagram', 639) AFTER the move                                (the EFFECT gate)
  P4c  the ControlTerminal census is unchanged across the move (115 -> 115)
  P4d  the panel row count is unchanged across the move (115 -> 115)
  P5a  wire_indicators returned an EMPTY error column
  P5b  the new indicator's wire uid changed from 0                                             (the EFFECT gate)
  P5c  #10686 t0 stays wired and its wired-terminal count is reported before and after                  (37(e))
  P5d  #637's terminal count is unchanged - no tunnel or border object appeared                         (37(e))
  P6   ExecState == 1 at the save point and g.save() returned a byte count      (a 0 here is a LEGITIMATE STOP)
  P7   the ORDERED second-pass `Is Broken?` read returned a boolean             (True is a LEGITIMATE reading)
  Z1   ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 unchanged after everything
  Z2   refs opened == refs closed, 0 live

STOP DISCIPLINE: if a phase's own precondition is not met, the run STOPS at that phase, records why, and goes
straight to the closing facts. No phase is retried and no verb is looped over indices (<= 1 attempt per verb).

PREDICTED RISKS, written down BEFORE the run so neither is an unpredicted result:
  (i)  `move_in` leaves JUNK `Invoke` node(s) behind on the target (measured: probe_move_ctlterm_v0.log:135,
       "purged 2 junk Invoke(s) left by the two move_in runs"). They are an unwired residue of the op, so they
       can hold ExecState at 0 and make phase 6's save illegal. The uids added by the move are RECORDED and
       then purged exactly as the built S5 step does (tools/recipes/build_d1_routeb_v0.py:1279-1287) - the junk
       set is `uids_after - uids_before`, so nothing pre-existing can be touched. This is mechanical residue
       cleanup of our OWN op, not a route choice.
  (ii) Nodes[] and Traverse indices SHIFT when an object is added to a diagram (34(h)). Every index used after
       a mutation is RE-RESOLVED by uid readback immediately before use; the historical pins 43 / 46 / 102 /
       25 / 24 / 4 are used only as a first guess that must survive a `node_terms_uid` uid echo, else a bounded
       scan replaces them.

BOUNDS: <= 1 attempt per verb, NO loop over indices. NO VI IS RUN (34(f)). NO NEW OP VI (Pre-decided 2). No new
device (user 2026-09-18 08:53). No GUI action. No motor / ASI / camera (rig 조립). Originals never opened for
write. `allow_broken` stays False and `gui_save` is NEVER called. `Is Broken?` is read ONLY in a separate,
ordered second pass, never in the pass that makes the connection (42(b)), and AFTER the save, so the artefact
survives that read's known ExecState perturbation (docs/NAMES.md:912-918). NOTHING IS DELETED THAT WAS SAVED.

WHAT ALREADY EXISTED (checked before writing a line of this, per the material brief):
  * tools/recipes/stage_d1_s3a_focus_ind.py DOES NOT EXIST on disk (checked 2026-09-20; reported, not touched).
  * tools/gscript.py - `build_index_array` :2322, `create_indicator` :2388, `delete_object` :2240,
    `node_info` :2462, `node_terms_uid` :925, `panel_wiring` :826, `fp_labels` :2440, `report`/`report_all`
    :455/:488, `uids` :1017, `count` :1005, `wire_indicators` :1756, `exec_state` :1977, `save` :2062,
    `remove_bad_wires_scripted` :2486, `ensure_loaded` :1268, `open_panel`/`close_panel` :1241/:1257.
  * tools/recipes/build_d1_v0.py - `move_in` :318, `owner_of` :338, `diag_index` :357.
  * tools/bench/diag_s2_scaffold.py - `fresh`, `Preload`, `file_facts`, `version_bytes`, the md5 pins.
  * tools/bench/diag_s56_transport3.py - the gate/fact/probe/scratch/save shape this file follows.
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
OUT = os.path.join(HERE, "diag_s57_ctmove_wire.json")
SCRATCH = os.path.join(g.CLAUDEDEV, "DIAG_s57_ctmove_%s.vi" % STAMP)
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

D639 = 639                      # the frame-loop BODY diagram (nested); owner WhileLoop #637
D536 = 536                      # the TopLevelDiagram (46(b))
LOOP11_UID = 637                # While loop 1.1
LOOP11_NODES_PIN = 4            # historical: #637 is Nodes[4] of Diagram #686 - VERIFIED by uid echo, never trusted
D686 = 686                      # the FlatSequenceFrame diagram that owns #637
SRC_UID = 10686                 # class Function, label 'And'; t0 'x .and. y?' is a SOURCE carrying wire 10799
SRC_TERM_NAME = "x .and. y?"
SRC_NODES_PIN = 25              # historical Nodes[] index of #10686 on Diagram #639
SINK_UID = 10407                # already sourced by wire 10799 - the idempotent pass-2 sink
SINK_NODES_PIN = 24             # historical Nodes[] index of #10407 on Diagram #639
SRC_WIRE = 10799
IA_LOCATION = (6200, 5200)      # far from every existing object; the IA is deleted again in the same phase
IA_TERM_INDEX = 2               # the terminal 46(a) names for create_indicator
MOVE_POSITION = (120, 4000)     # a position INSIDE Diagram #639; overlap is cosmetic, never functional
SCAN_LIMIT = 80                 # the bounded Nodes[] scan used only when a pinned index fails its uid echo

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "question": "cycle 57: does the S3a transport route work END TO END on ONE indicator - create at top level "
                 "(46(a)) -> move_in TOP-LEVEL -> NESTED Diagram #639 -> wire by LABEL at that nested diagram "
                 "index? Each step is measured individually on disk; no run has ever joined them.",
     "chooses_no_route": True, "interprets_nothing": True, "no_vi_was_run": True, "no_new_op": True,
     "no_new_device": True, "no_gui_action": True, "no_recipe": True, "edits_no_plan_document": True,
     "rig_state": "조립 (motors/ASI forbidden, camera not needed)",
     "recipe_file_reported_not_touched": {
         "path": "tools/recipes/stage_d1_s3a_focus_ind.py",
         "exists": os.path.exists(os.path.join(ROOT, "tools", "recipes", "stage_d1_s3a_focus_ind.py")),
         "mtime": None,
         "note": "The brief FORBIDS writing or launching it this cycle (guard_cycle refuses a recipe build). "
                 "Reported only."},
     "citations": {"create_route": "Pre-decided 46(a); docs/NAMES.md:476-478; "
                                   "docs/stage2-assembly-step-b.md:49-50; tools/bench/diag_s56_transport3.log:68-80",
                   "ct_move_prior_art": "tools/bench/probe_move_ctlterm_v0.log:130-133 (NESTED -> NESTED only)",
                   "wire_by_label_at_nested_index": "docs/d1-build-plan.md:1231 (WIRED at 43); "
                                                    ":1232-1233 (a NEWLINE in the label still fails)",
                   "move_in_owner_of_diag_index": "tools/recipes/build_d1_v0.py:318,:338,:357",
                   "junk_invoke_purge": "tools/recipes/build_d1_routeb_v0.py:1279-1287; "
                                        "tools/bench/probe_move_ctlterm_v0.log:135",
                   "is_broken": "docs/NAMES.md:902-911", "ordered_second_pass": "Pre-decided 42(b)",
                   "index_shift_after_mutation": "34(h); cycles 54/56",
                   "branch_adds_no_wire_object": "tools/gscript.py:1771-1772",
                   "gate_must_make_a_call": "Pre-decided 46(g)"},
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "scratch": SCRATCH,
     "handles": {}, "hash_probe": [], "phase1": {}, "phase2": {}, "phase3": {}, "phase4": {}, "phase5": {},
     "phase6": {}, "phase7": {}, "stopped_at": None}

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


# ============================================================================ THE ONE SEQUENCE
def sequence(target):
    P1, P2, P3, P4, P5, P6, P7 = (R["phase%d" % k] for k in range(1, 8))

    # ------------------------------------------------------------------ PHASE 1: resolve LIVE indices
    print("\n=================== PHASE 1  (resolve LIVE indices; assume none of them, 34(h))", flush=True)
    census(R, "before everything", target)
    read_exec_state("PHASE 1 BEFORE", target)

    for uid, key in ((D639, "diag_index_639"), (D536, "diag_index_536"), (D686, "diag_index_686")):
        try:
            P1[key] = diag_index(target, uid)
            P1[key + "_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            P1[key] = None
            P1[key + "_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("P1 diag_index(#%d) = %r ; error VERBATIM %r" % (uid, P1[key], P1[key + "_error_verbatim"]))
    d639, d536, d686 = P1["diag_index_639"], P1["diag_index_536"], P1["diag_index_686"]
    gate("P1a diag_index(#639) resolves to an int", isinstance(d639, int),
         "%r (historical values 43 / 46 are NOT reused)" % (d639,))
    gate("P1b diag_index(#536) resolves to 0", d536 == 0, "%r" % (d536,))

    P1["owner_of_639"] = owner_read("P1c owner of Diagram #639", D639, target)
    gate("P1c owner_of(#639) answers ('WhileLoop', 637)",
         (P1["owner_of_639"].get("owner_class"), P1["owner_of_639"].get("owner_uid")) == ("WhileLoop", 637),
         "(%r, %r)" % (P1["owner_of_639"].get("owner_class"), P1["owner_of_639"].get("owner_uid")))
    P1["owner_of_10686"] = owner_read("P1d owner of Function #10686", SRC_UID, target)
    gate("P1d owner_of(#10686) answers ('Diagram', 639)",
         (P1["owner_of_10686"].get("owner_class"), P1["owner_of_10686"].get("owner_uid")) == ("Diagram", 639),
         "(%r, %r)" % (P1["owner_of_10686"].get("owner_class"), P1["owner_of_10686"].get("owner_uid")))

    try:
        fn_uids = [o["uid"] for o in g.report_all(target, "Function")]
        P1["function_class_count"] = len(fn_uids)
        P1["function_index_of_10686"] = fn_uids.index(SRC_UID) if SRC_UID in fn_uids else None
        P1["function_index_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        fn_uids = []
        P1["function_class_count"] = None
        P1["function_index_of_10686"] = None
        P1["function_index_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    fn_i = P1["function_index_of_10686"]
    fact("P1e #%d sits at LIVE Traverse index %r of class `Function` (%r members); the historical value 102 is "
         "NOT reused. error VERBATIM %r"
         % (SRC_UID, fn_i, P1["function_class_count"], P1["function_index_error_verbatim"]))
    gate("P1e #10686 is found in the live Traverse(`Function`) uid list", isinstance(fn_i, int), "%r" % (fn_i,))
    dump()
    if not isinstance(d639, int):
        R["stopped_at"] = "PHASE 1: Diagram #639 has no live Traverse index, so phase 4's destination is unknown."
        raise Stop(R["stopped_at"])

    # ------------------------------------------------------------------ PHASE 2: create ONE indicator, 46(a)
    print("\n=================== PHASE 2  (create ONE indicator by the 46(a) route)", flush=True)
    rows_before = panel_rows(target)
    fpl_before = fp_label_list(target)
    P2["panel_rows_before"] = len(rows_before)
    P2["fp_labels_before"] = len(fpl_before)
    ct_before = g.count(target, "ControlTerminal")
    P2["control_terminal_before"] = ct_before
    fact("P2 BEFORE: panel_wiring rows %r, fp_labels %r, ControlTerminal census %r"
         % (len(rows_before), len(fpl_before), ct_before))

    try:
        top0 = g.node_info(target, max_n=40)
        P2["node_info_before_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        top0 = None
        P2["node_info_before_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    P2["node_info_before"] = top0
    fact("P2b node_info(max_n=40) BEFORE: %r entries -> %r ; error VERBATIM %r"
         % (len(top0) if isinstance(top0, list) else top0, top0, P2["node_info_before_error_verbatim"]))

    new_ia, ia_err = None, None
    try:
        new_ia = g.build_index_array(target, IA_LOCATION)
        ia_err = ""
    except Exception as e:                                                         # noqa: BLE001
        ia_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    P2["build_index_array"] = {"location": list(IA_LOCATION), "new": new_ia, "error_verbatim": ia_err}
    fact("P2a build_index_array(top-level head, %r) -> new %r ; error VERBATIM %r" % (IA_LOCATION, new_ia, ia_err))
    ia_uid = (new_ia[0]["uid"] if isinstance(new_ia, list) and new_ia else None)
    ia_owner = owner_read("P2a the new IndexArray's owner", ia_uid, target) if ia_uid else {}
    P2["index_array_owner"] = ia_owner
    gate("P2a build_index_array put 1 new IndexArray on the target and owner_of reads ('TopLevelDiagram', 536)",
         isinstance(new_ia, list) and len(new_ia) == 1
         and (ia_owner.get("owner_class"), ia_owner.get("owner_uid")) == ("TopLevelDiagram", 536),
         "new %r, owner (%r, %r)" % (new_ia, ia_owner.get("owner_class"), ia_owner.get("owner_uid")))

    try:
        top1 = g.node_info(target, max_n=40)
        P2["node_info_after_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        top1 = None
        P2["node_info_after_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    P2["node_info_after"] = top1
    fact("P2b node_info(max_n=40) AFTER (create_indicator's OWN ladder): %r entries -> %r ; error VERBATIM %r"
         % (len(top1) if isinstance(top1, list) else top1, top1, P2["node_info_after_error_verbatim"]))
    gate("P2b node_info goes 0 entries -> 1 entry",
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
    P2["create_indicator"] = {"node_index": node_i, "terminal_index": IA_TERM_INDEX, "new": new_ct,
                              "error_verbatim": ci_err}
    fact("P2c create_indicator(Nodes[%r].Terminals[%d]) -> new %r ; error VERBATIM %r"
         % (node_i, IA_TERM_INDEX, new_ct, ci_err))
    ct_after = g.count(target, "ControlTerminal")
    P2["control_terminal_after_create"] = ct_after
    new_ct_uid = (new_ct[0].get("uid") if isinstance(new_ct, list) and new_ct else None)
    gate("P2c create_indicator returned a ControlTerminal and the census went %r -> %r" % (ct_before, ct_after),
         isinstance(new_ct_uid, int) and isinstance(ct_before, int) and ct_after == ct_before + 1,
         "new uid %r, census %r -> %r" % (new_ct_uid, ct_before, ct_after))

    gone, del_err = None, None
    if ia_uid is None:
        del_err = "NOT ATTEMPTED: no IndexArray uid to delete."
    else:
        try:
            ias = [o["uid"] for o in g.report_all(target, "IndexArray")]
            P2["index_array_traverse_index_at_delete"] = ias.index(ia_uid)
            gone = g.delete_object(target, "IndexArray", ias.index(ia_uid))
            del_err = ""
        except Exception as e:                                                     # noqa: BLE001
            del_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    P2["delete_object"] = {"gone": sorted(gone) if gone else gone, "error_verbatim": del_err}
    fact("P2d delete_object(IndexArray[%r]) -> gone %r ; error VERBATIM %r"
         % (P2.get("index_array_traverse_index_at_delete"), sorted(gone) if gone else gone, del_err))
    gate("P2d delete_object removed exactly 1 object", bool(gone) and len(gone) == 1,
         "%r (error %r)" % (sorted(gone) if gone else gone, del_err))
    es_after_del = read_exec_state("P2e after delete_object", target)
    P2["exec_state_after_delete"] = es_after_del
    gate("P2e ExecState after the delete == 1", es_after_del == 1, "%r" % (es_after_del,))
    dump()
    if not isinstance(new_ct_uid, int):
        R["stopped_at"] = "PHASE 2: create_indicator returned no ControlTerminal uid, so there is nothing to move."
        raise Stop(R["stopped_at"])

    # ------------------------------------------------------------------ PHASE 3: READ the label off the machine
    print("\n=================== PHASE 3  (READ the new indicator's label off the machine - nothing is retyped)",
          flush=True)
    rows_after = panel_rows(target)
    fpl_after = fp_label_list(target)
    P3["panel_rows_after_create"] = len(rows_after)
    P3["fp_labels_after_create"] = len(fpl_after)
    before_keys = {(r.get("uid"), r.get("label")) for r in rows_before}
    new_rows = [r for r in rows_after if (r.get("uid"), r.get("label")) not in before_keys]
    P3["new_panel_rows"] = new_rows
    before_fp = {(i, t) for (i, t, _ind) in fpl_before}
    new_fp = [(i, t, ind) for (i, t, ind) in fpl_after if (i, t) not in before_fp]
    P3["new_fp_labels"] = new_fp
    fact("P3a panel_wiring rows %r -> %r ; the NEW row(s) %r" % (len(rows_before), len(rows_after), new_rows))
    fact("P3a2 fp_labels %r -> %r ; the NEW entr(y/ies) %r" % (len(fpl_before), len(fpl_after), new_fp))

    label = None
    label_source = None
    if len(new_rows) == 1 and new_rows[0].get("label") is not None:
        label, label_source = new_rows[0]["label"], "panel_wiring diff (the machine's own Control.Label text)"
    elif len(new_fp) == 1:
        label, label_source = new_fp[0][1], "fp_labels diff (the machine's own Control.Label text)"
    P3["label_repr"] = repr(label)
    P3["label_utf8_hex"] = (label or "").encode("utf-8").hex() if label is not None else None
    P3["label_source"] = label_source
    P3["label_contains_newline"] = (("\n" in label) or ("\r" in label)) if label is not None else None
    existing_labels = [r.get("label") for r in rows_before]
    P3["label_is_duplicate_of_an_existing_panel_label"] = (label in existing_labels) if label is not None else None
    P3["new_ct_uid"] = new_ct_uid
    fact("P3 THE LABEL, VERBATIM: %r  (utf-8 hex %r, source: %s)" % (label, P3["label_utf8_hex"], label_source))
    fact("P3 contains a NEWLINE: %r  (docs/d1-build-plan.md:1232-1233 - a newline in the label still fails from "
         "`Wire Inputs.vi` even at a nested diagram index)" % (P3["label_contains_newline"],))
    fact("P3 is a DUPLICATE of an existing panel label: %r" % (P3["label_is_duplicate_of_an_existing_panel_label"],))
    gate("P3a exactly ONE new front-panel row appeared and its label was READ off the machine",
         len(new_rows) + (1 if (not new_rows and len(new_fp) == 1) else 0) >= 1 and label is not None,
         "%r new panel row(s), %r new fp_labels entr(y/ies), label %r"
         % (len(new_rows), len(new_fp), label))
    gate("P3b the new label is UNIQUE among the target's panel labels",
         P3["label_is_duplicate_of_an_existing_panel_label"] is False,
         "duplicate=%r" % (P3["label_is_duplicate_of_an_existing_panel_label"],))
    P3["owner_of_new_ct"] = owner_read("P3c the new ControlTerminal's owner (BEFORE the move)", new_ct_uid, target)
    gate("P3c owner_of(new ControlTerminal uid) answers",
         P3["owner_of_new_ct"].get("owner_class") is not None,
         "(%r, %r)" % (P3["owner_of_new_ct"].get("owner_class"), P3["owner_of_new_ct"].get("owner_uid")))
    dump()
    if label is None:
        R["stopped_at"] = ("PHASE 3: the new indicator's label could not be READ off the machine, and a label is "
                           "never retyped - phase 5 has no byte-exact name to pass.")
        raise Stop(R["stopped_at"])

    # ------------------------------------------------------------------ PHASE 4: move_in TOP-LEVEL -> NESTED
    print("\n=================== PHASE 4  (move_in TOP-LEVEL -> NESTED Diagram #639 - never tried before)",
          flush=True)
    P4["dest_diagram_uid"] = D639
    P4["dest_diagram_index_live"] = d639
    P4["position"] = list(MOVE_POSITION)
    P4["owner_before"] = P3["owner_of_new_ct"]
    ct_b = g.count(target, "ControlTerminal")
    rows_b = len(rows_after)
    es_b = read_exec_state("P4 BEFORE the move", target)
    try:
        inv_before = set(g.uids(target, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_before = set()
        fact("uids(Invoke) BEFORE raised %s: %s" % (type(e).__name__, str(e)[:140]))
    P4["invoke_uids_before"] = sorted(inv_before)

    mv_ret, mv_err = None, None
    try:
        mv_ret = move_in(target, new_ct_uid, d639, MOVE_POSITION)
        mv_err = ""
    except Exception as e:                                                         # noqa: BLE001
        mv_err = "%s: %s" % (type(e).__name__, str(e)[:500])
    P4["move_in"] = {"returned": mv_ret, "error_verbatim": mv_err}
    fact("P4a move_in(#%r -> Diagram #%d at Traverse index %r, position %r) returned %r ; error VERBATIM %r  "
         "(the Move returns NO reference to the object at its new home, "
         "archive/peer/2026-08-28-copy-nodes-between-vis.md:51)"
         % (new_ct_uid, D639, d639, MOVE_POSITION, mv_ret, mv_err))
    gate("P4a move_in returned without raising", mv_err == "", "returned %r, error %r" % (mv_ret, mv_err))

    # PREDICTED RISK (i): the junk `Invoke` residue of the op itself. RECORDED, then purged exactly as
    # tools/recipes/build_d1_routeb_v0.py:1279-1287 does - the set is `after - before`, so nothing pre-existing
    # can be touched. This is mechanical residue cleanup of OUR OWN op, not a route choice.
    try:
        inv_after = set(g.uids(target, "Invoke"))
    except Exception as e:                                                         # noqa: BLE001
        inv_after = set()
        fact("uids(Invoke) AFTER raised %s: %s" % (type(e).__name__, str(e)[:140]))
    junk = sorted(inv_after - inv_before)
    P4["junk_invoke_uids_added_by_move_in"] = junk
    P4["junk_purge"] = []
    fact("P4a2 move_in left %r junk `Invoke`(s): %r (PREDICTED RISK (i))" % (len(junk), junk))
    for ju in junk:
        rec = {"uid": ju}
        try:
            cur = [o["uid"] for o in g.report_all(target, "Invoke")]
            rec["gone"] = sorted(g.delete_object(target, "Invoke", cur.index(ju)) or [])
            rec["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            rec["gone"] = None
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        P4["junk_purge"].append(rec)
        fact("P4a3 purged junk Invoke #%r -> gone %r ; error VERBATIM %r"
             % (ju, rec["gone"], rec["error_verbatim"]))

    P4["owner_after"] = owner_read("P4b the new ControlTerminal's owner (AFTER the move)", new_ct_uid, target)
    ct_a = g.count(target, "ControlTerminal")
    rows_a = panel_rows(target)
    es_a = read_exec_state("P4 AFTER the move (and the junk purge)", target)
    P4["control_terminal_census"] = {"before": ct_b, "after": ct_a}
    P4["panel_row_count"] = {"before": rows_b, "after": len(rows_a)}
    P4["exec_state"] = {"before": es_b, "after": es_a}
    gate("P4b owner_of(new uid) reads ('Diagram', 639) AFTER the move",
         (P4["owner_after"].get("owner_class"), P4["owner_after"].get("owner_uid")) == ("Diagram", D639),
         "(%r, %r) -> (%r, %r)"
         % (P4["owner_before"].get("owner_class"), P4["owner_before"].get("owner_uid"),
            P4["owner_after"].get("owner_class"), P4["owner_after"].get("owner_uid")))
    gate("P4c the ControlTerminal census is unchanged across the move", ct_b == ct_a, "%r -> %r" % (ct_b, ct_a))
    gate("P4d the panel row count is unchanged across the move", rows_b == len(rows_a),
         "%r -> %r" % (rows_b, len(rows_a)))
    row_now = next((r for r in rows_a if r.get("label") == label), None)
    P4["target_row_after_move"] = row_now
    fact("P4 the target indicator's panel row after the move: %r" % (row_now,))
    dump()

    # ------------------------------------------------------------------ PHASE 5: wire by LABEL at the nested index
    print("\n=================== PHASE 5  (wire_indicators by LABEL at the nested diagram index)", flush=True)
    d639_now = None
    try:
        d639_now = diag_index(target, D639)
    except Exception as e:                                                         # noqa: BLE001
        fact("diag_index(#639) re-read raised %s: %s" % (type(e).__name__, str(e)[:160]))
    P5["diagram_index_639_reread_after_the_move"] = d639_now
    fact("P5 Diagram #639 re-reads Traverse index %r after the move (was %r); 34(h): never cached across a "
         "mutation" % (d639_now, d639))
    d_use = d639_now if isinstance(d639_now, int) else d639
    try:
        fn_uids2 = [o["uid"] for o in g.report_all(target, "Function")]
        fn_i2 = fn_uids2.index(SRC_UID) if SRC_UID in fn_uids2 else None
    except Exception as e:                                                         # noqa: BLE001
        fn_i2 = None
        fact("report_all(Function) re-read raised %s: %s" % (type(e).__name__, str(e)[:160]))
    P5["function_index_of_10686_reread"] = fn_i2
    fact("P5 #%d re-reads Traverse `Function` index %r after the move (was %r)" % (SRC_UID, fn_i2, fn_i))
    fn_use = fn_i2 if isinstance(fn_i2, int) else fn_i

    src_before = wired_counts("P5c BEFORE #%d (the source node)" % SRC_UID, target, d_use, SRC_UID, SRC_NODES_PIN)
    t0 = next((t for t in src_before.get("terms", []) if t["i"] == 0), None)
    fact("P5c #%d t0 reads %r (is_source %r, wire %r; the pin is wire %d)"
         % (SRC_UID, (t0 or {}).get("name"), (t0 or {}).get("is_source"), (t0 or {}).get("wire"), SRC_WIRE))
    loop_before = wired_counts("P5d BEFORE #%d (loop 1.1, the tunnel/border check)" % LOOP11_UID, target,
                               d686 if isinstance(d686, int) else 0, LOOP11_UID, LOOP11_NODES_PIN)

    wire_b = (row_now or {}).get("wire")
    wires_b = g.count(target, "Wire")
    es_pre = read_exec_state("P5 BEFORE wire_indicators", target)
    wi_dt, wi_err = None, None
    if fn_use is None or not isinstance(d_use, int):
        wi_err = "NOT ATTEMPTED: Function index %r / diagram index %r unresolved." % (fn_use, d_use)
    else:
        try:
            wi_dt = g.wire_indicators(target, fn_use, [SRC_TERM_NAME], [label],
                                      diagram_index=d_use, node_class="Function")
            wi_err = ""
        except Exception as e:                                                     # noqa: BLE001
            wi_err = "%s: %s" % (type(e).__name__, str(e)[:900])
    P5["wire_indicators"] = {"node_index": fn_use, "node_class": "Function", "src_terms": [SRC_TERM_NAME],
                             "indicator_names_repr": repr([label]),
                             "indicator_names_utf8_hex": [(label or "").encode("utf-8").hex()],
                             "diagram_index": d_use, "seconds": wi_dt, "error_verbatim": wi_err}
    fact("P5a wire_indicators(Function[%r], [%r] -> [%r], diagram_index=%r) error VERBATIM %r"
         % (fn_use, SRC_TERM_NAME, label, d_use, wi_err))
    gate("P5a wire_indicators returned an EMPTY error column", wi_err == "", repr(wi_err))

    rows_w = panel_rows(target)
    row_w = next((r for r in rows_w if r.get("label") == label), None)
    wire_a = (row_w or {}).get("wire")
    wires_a = g.count(target, "Wire")
    P5["target_row_after_wiring"] = row_w
    P5["target_wire_uid"] = {"before": wire_b, "after": wire_a}
    P5["whole_vi_wire_count"] = {"before": wires_b, "after": wires_a, "delta": (wires_a - wires_b)
                                 if isinstance(wires_a, int) and isinstance(wires_b, int) else None}
    fact("P5b the target indicator's wire uid %r -> %r ; whole-VI Wire count %r -> %r (delta %r; a BRANCH adds "
         "NO Wire object, tools/gscript.py:1771-1772)"
         % (wire_b, wire_a, wires_b, wires_a, P5["whole_vi_wire_count"]["delta"]))
    gate("P5b the new indicator's wire uid changed from 0", bool(wire_a) and wire_a != wire_b,
         "%r -> %r" % (wire_b, wire_a))
    es_post = read_exec_state("P5 AFTER wire_indicators", target)
    P5["exec_state"] = {"before": es_pre, "after": es_post}

    src_after = wired_counts("P5c AFTER #%d (the source node)" % SRC_UID, target, d_use, SRC_UID, SRC_NODES_PIN)
    loop_after = wired_counts("P5d AFTER #%d (loop 1.1, the tunnel/border check)" % LOOP11_UID, target,
                              d686 if isinstance(d686, int) else 0, LOOP11_UID, LOOP11_NODES_PIN)
    gate("P5c #%d t0 stays wired and its wired-terminal count is reported (37(e))" % SRC_UID,
         src_before.get("n_wired") is not None and src_after.get("n_wired") is not None
         and src_before.get("n_wired") == src_after.get("n_wired"),
         "%r -> %r wired of %r -> %r terminals" % (src_before.get("n_wired"), src_after.get("n_wired"),
                                                   src_before.get("n_terms"), src_after.get("n_terms")))
    gate("P5d #%d terminal count unchanged - NO tunnel or border object appeared (37(e))" % LOOP11_UID,
         loop_before.get("n_terms") is not None and loop_before.get("n_terms") == loop_after.get("n_terms"),
         "%r -> %r terminals, %r -> %r wired"
         % (loop_before.get("n_terms"), loop_after.get("n_terms"),
            loop_before.get("n_wired"), loop_after.get("n_wired")))
    fact("P5d EXPLICIT (37(e) grain): #%d terminals %r -> %r, wired %r -> %r; a tunnel or border object would "
         "show as a terminal-count INCREASE. Increase observed: %r"
         % (LOOP11_UID, loop_before.get("n_terms"), loop_after.get("n_terms"), loop_before.get("n_wired"),
            loop_after.get("n_wired"),
            (loop_after.get("n_terms") or 0) - (loop_before.get("n_terms") or 0)))
    census(R, "after the wiring attempt", target)
    dump()

    # ------------------------------------------------------------------ PHASE 6: save IFF legal
    print("\n=================== PHASE 6  (save IFF ExecState == 1 - a 0 is a LEGITIMATE outcome)", flush=True)
    es_save = read_exec_state("P6 immediately before the save attempt", target)
    size, serr = None, None
    if isinstance(es_save, int) and es_save == 1:
        try:
            size = g.save(target)          # allow_broken stays False; gui_save is NEVER called
        except Exception as e:                                                     # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:400])
    else:
        serr = ("NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved. This is a LEGITIMATE outcome "
                "under this brief, not a failure to work around." % (es_save,))
    P6["exec_state_before_save"] = es_save
    P6["returned_bytes"] = size
    P6["exception_or_reason_verbatim"] = serr
    P6["allow_broken"] = False
    P6["gui_save"] = False
    fact("P6 g.save() returned %r ; exception/reason VERBATIM %r" % (size, serr))
    P6["file_after"] = D.file_facts("P6 the artefact after the save attempt", target)
    gate("P6 ExecState == 1 at the save point and g.save() returned a byte count",
         isinstance(size, int) and size > 0, "ExecState %r, bytes %r, reason %r" % (es_save, size, serr))
    dump()

    # ------------------------------------------------------------------ PHASE 7: the ORDERED second pass, 42(b)
    print("\n=================== PHASE 7  (ORDERED second pass: `Is Broken?`, AFTER the save, 42(b))", flush=True)
    if not wire_a:
        P7["not_attempted_because"] = ("phase 5 produced no wire (target wire uid %r -> %r), and 42(b)'s ordered "
                                       "pass has nothing to read." % (wire_b, wire_a))
        fact("P7 NOT ATTEMPTED: %s" % P7["not_attempted_because"])
        dump()
        return
    si, si_how, _ = node_index_of(target, d_use, SINK_UID, SINK_NODES_PIN)
    ni, ni_how, _ = node_index_of(target, d_use, SRC_UID, SRC_NODES_PIN)
    P7["sink"] = {"uid": SINK_UID, "node_index": si, "index_resolution": si_how}
    P7["source"] = {"uid": SRC_UID, "node_index": ni, "index_resolution": ni_how}
    P7["method"] = ("an IDEMPOTENT re-connect of the EXISTING #%d t0 -> #%d t0 connection on the SAME net "
                    "(wire %d). A front-panel ControlTerminal is not in Nodes[], so no 6371004 carrier can "
                    "address the indicator end; the same NET is read instead. wire_delta must be 0."
                    % (SRC_UID, SINK_UID, SRC_WIRE))
    if si is None or ni is None:
        P7["not_attempted_because"] = ("the 6371004 carrier needs BOTH ends addressable in Nodes[]: sink %r, "
                                       "source %r." % (si, ni))
        fact("P7 NOT ATTEMPTED: %s" % P7["not_attempted_because"])
        dump()
        return
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, d_use, si, 0, d_use, ni, 0, V1_LABELS)
        P7.update({"wire_delta": dw, "exec_state_returned": es, "error_verbatim": err})
    except Exception as e:                                                         # noqa: BLE001
        P7.update({"wire_delta": None, "exec_state_returned": None,
                   "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    P7["op_indicators"] = op_indicators()
    ib = P7["op_indicators"].get("Is Broken?")
    P7["is_broken_ordered"] = ib
    fact("P7 ORDERED `Is Broken?` = %r on wire uid %r (op error column %r, wire_delta %r). True here is a "
         "LEGITIMATE reading, not a failure."
         % (ib, P7["op_indicators"].get("UID 2"), P7.get("error_verbatim"), P7.get("wire_delta")))
    gate("P7 the ORDERED second-pass `Is Broken?` read returned a boolean", isinstance(ib, bool), repr(ib))
    read_exec_state("P7 after the Is Broken? read (SUSPECT, docs/NAMES.md:912-918; the save already happened)",
                    target)
    dump()


# ======================================================================================== MAIN
def main():
    print("=== diag_s57_ctmove_wire  %s   (cycle 57 dispatch 3; DIAGNOSTIC, never a recipe; PHASES 1..7 on ONE "
          "scratch; NO VI IS RUN, 34(f); no new op, no new device, no GUI action; CHOOSES NOTHING)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    fact("tools/recipes/stage_d1_s3a_focus_ind.py: exists=%r mtime=%r - REPORTED, NOT TOUCHED (the brief forbids "
         "writing or launching it this cycle)"
         % (R["recipe_file_reported_not_touched"]["exists"], R["recipe_file_reported_not_touched"]["mtime"]))
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (cycle 56 left the instance UP at ~63,517; fresh baseline ~31,500): %r"
         % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    # ---- the mechanical pre-batch restart the brief orders (44(e)/46(j); standing restart permission, CLAUDE.md 3)
    D.fresh("T2b RESTART (pre-batch, 44(e)/46(j); cycle 56 left pid 8856 UP at ~63,517 handles)")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])
    dump()

    # ---- the dated scratch
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copy2(S2_ARTEFACT, SCRATCH)
    p = probe("T3 the scratch at creation (copied from D1_s2_loops.vi)", SCRATCH)
    R["scratch_at_creation"] = p
    gate("T3 the scratch is byte-identical to D1_s2_loops.vi at creation", p.get("md5") == S2_MD5,
         "%s (expected %s)" % (p.get("md5", "?"), S2_MD5), fatal=True)
    dump()

    saved_ok = False
    try:
        with D.Preload("S57"):
            g.open_panel(SCRATCH)
            time.sleep(1.0)
            try:
                sequence(SCRATCH)
            finally:
                saved_ok = isinstance(R["phase6"].get("returned_bytes"), int)
                close_quietly(SCRATCH)
    except Stop as s:
        fact("STOPPED at a phase precondition: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        fact("the sequence raised %s: %s" % (type(e).__name__, str(e)[:600]))
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

    # NOTHING SAVED IS EVER DELETED (a step is not done until it has left a file). Only an UNSAVED scratch this
    # run created is cleaned up, from inside the run. ONE attempt, no retry.
    R["scratch_cleanup"] = {"path": SCRATCH, "saved": saved_ok}
    if saved_ok:
        R["scratch_cleanup"]["action"] = "KEPT - phase 6 saved it; deleting a saved artefact is forbidden."
    else:
        try:
            if os.path.exists(SCRATCH):
                os.remove(SCRATCH)
            R["scratch_cleanup"]["action"] = "removed (never saved)"
            R["scratch_cleanup"]["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            R["scratch_cleanup"]["action"] = "remove FAILED"
            R["scratch_cleanup"]["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    fact("scratch cleanup: %r" % (R["scratch_cleanup"],))

    zo = probe("Z1 ORIGINAL after everything", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after everything", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after everything", S2_ARTEFACT)
    gate("Z1 ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 all unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5,
         "%s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z2 refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    fact("ARTEFACT: %r" % ({"path": SCRATCH, "bytes": R["phase6"].get("returned_bytes"),
                            "file": R["phase6"].get("file_after")},))
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
